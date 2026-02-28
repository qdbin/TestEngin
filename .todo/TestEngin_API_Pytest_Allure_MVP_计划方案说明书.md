# TestEngin（仅API）Pytest+Allure 重构：MVP计划方案说明书

## 1. 目标与范围

### 1.1 背景现状（以当前代码实现为准）

- 调度与控制：平台通过 WebSocket 维持心跳与下发控制指令（start/stop/stopAll），引擎通过 HTTP 拉取任务并执行。
- 执行：当前 API/WEB/APP 三类测试均通过 `LMCase + Unittest` 的动态造类/绑方法执行，结果通过队列实时推送到结果上报进程，再批量上传平台。
- 报告：平台侧是主报告与主数据源；引擎侧仅维护结构化 `case_info`（包含 `transactionList`）并上传；截图为异步上传附件。

### 1.2 本次重构目标（MVP 优先）

MVP 目标：在**不改平台接口/协议**的前提下，将**接口（API）执行引擎**从 Unittest 运行形态演进为 **Pytest 执行内核**，并以 **Allure 旁路增强**输出本地报告（可选开关），同时保持以下能力不回退：

- 任务调度方式不变：WebSocket 控制 + HTTP 拉取任务。
- 平台回传方式不变：`case_info` / `caseResultList` 的结构与上传节奏不变；任务完成回调不变。
- 引擎并发策略短期不变（按 collection 并发、collection 内串行），后续可无缝演进到 xdist/分布式。
- 仅重构 API 相关：Web/App 模块允许保持不变或逐步删除，但 MVP 不以删除为主（避免无关风险）。

### 1.3 非目标（MVP 不做）

- 不改平台后端接口协议、字段结构、鉴权方式。
- 不做跨引擎负载均衡算法升级（但预留演进点）。
- 不强制引入 pytest-xdist（并行分布式可作为后续里程碑）。
- 不将 Allure 作为平台主报告来源（Allure 仅为引擎侧旁路增强）。

### 1.4 关键约束

- “最小改动”优先：尽可能复用 `core/api/*` 的业务执行器实现（请求、断言、提取、前后置等）。
- “业务解耦”优先：执行引擎的核心业务逻辑要与 Pytest/Allure 低耦合，避免将报告调用散落到 `core/api/*`。

---

## 2. 核心设计原则（企业实践）

### 2.1 控制面/数据面分离

- 控制面：引擎在线状态、心跳、停止任务、继续拉取等（WebSocket）。
- 数据面：任务内容、用例包、执行结果与附件上传（HTTP）。

企业实践：**控制面轻量、数据面可靠**，利于扩容、容错、重试、幂等。

### 2.2 “执行内核”与“业务执行器”解耦

- Pytest 仅作为“执行内核”（组织用例、生命周期回调、插件生态）。
- `core/api/*` 作为“业务执行器”（如何执行接口步骤与断言、如何产出 transactionList）。

### 2.3 “运行时容器（Runtime）”作为统一抽象

引入 Runtime 作为“用例运行时上下文容器”，承载：

- 用例元信息：taskId、collectionId、caseId、index、caseName、caseType、runTimes、开始/结束时间等
- 共享对象：session、context（collection 级共享策略保持不变）
- 事务与日志：transactionList、debugLog/errorLog、附件（可选）
- 结果判定：失败/错误记录、最终 status 计算、错误摘要

Runtime 的定位：让 `core/api/*` 只依赖 Runtime 能力，不依赖 Unittest/Pytest 的内部结构。

### 2.4 Allure 旁路观察者（Observer）模式

AllureReporter 作为“旁路观察者”，监听 Runtime 事件或基于 `transactionList` 回放生成 Allure step。

- 执行业务逻辑不调用 allure。
- 是否开启 Allure 由配置开关控制，关闭时无任何副作用。

---

## 3. 目标架构（MVP 版）

### 3.1 引擎进程结构（保持现有风格）

- 主进程：启动线程（心跳、拉取、消息监听）；管理任务进程生命周期（start/stop）。
- 任务执行进程（Executor）：负责解析任务、构建执行计划、运行 Pytest（API-only）。
- 结果上报进程（Reporter）：复用现有结果队列协议与批量上传逻辑（不改平台）。
- 附件上传进程（Artifacts，可选）：API MVP 可先不上传截图；后续可上传请求/响应原文等。

### 3.2 API-only 执行链路（高层数据流）

1) fetch_task（HTTP）获取 task
2) data_pull + unzip（本地）得到 case json
3) 构建 `case_descriptor_list`（一条用例一条描述）
4) 运行 pytest：
   - 收集阶段：把每条 descriptor 转成一个 pytest Item（方案二）
   - 执行阶段：Item.run 调用 `core/api` 执行器，产出 transactionList
   - 结束阶段：组装 `case_info` 并实时推送 queue
5) Reporter 进程批量 upload_result，最后 complete_task

---

## 4. MVP 技术路线选择（默认最贴合本项目）

### 4.1 执行路线：优先采用“方案二：pytest 插件动态收集 Item”，但做成最小闭环

选择理由：

- 平台是“数据驱动（JSON）+ 引擎执行”的模式，pytest Item 动态收集更贴合企业执行内核做法；
- 更利于后续扩展：过滤、标签、按 collection 分组、引入 xdist 分发等；
- 以 `--plan` 指定计划文件，避免扫描目录造成误收集，适合引擎集成。

MVP 复杂度控制策略：

- 不实现复杂的 Collector 树，仅实现一个 PlanCollector（读取 plan.json）并生成 Items；
- Items 的 metadata 直接来自 plan.json（taskId/collectionId/caseId/index/jsonPath 等），不需要解析平台全部字段；
- 先保证“可执行+可上报+可停止”闭环，后续再做性能与并行增强。

### 4.2 Allure 路线：MVP 先使用“方式二：执行后回放 transactionList”为主，预留方式一演进点

选择理由：

- 方式二侵入最小：不需要严格维护 step 的开始/结束事件边界；
- 先验证“报告可用、数据完整”，避免在 MVP 阶段引入过多状态管理与并发隔离复杂度；
- 后续如果需要更真实的 step 现场，再演进到方式一（事件驱动实时 step）。

---

## 5. 关键模块设计（MVP）

### 5.1 Runtime（运行时容器）

#### 5.1.1 责任边界

- 面向业务执行器（`core/api`）提供统一接口：
  - `defineTrans/updateTransStatus/debugLog/errorLog`
  - `recordFailStatus/recordErrorStatus`
  - `handleResult`（计算最终 case status、生成错误摘要）
- 不继承 `unittest.TestCase`，不依赖 `self._outcome` 的 unittest 私有结构。
- 提供 `transactionList`（兼容平台 schema）与“可回放数据”（供 Allure）。

#### 5.1.2 最小字段（建议）

- `task_id, collection_id, case_id, index, case_type, case_name, case_desc`
- `start_time_ms, end_time_ms, run_times`
- `context, session`
- `trans_list`
- `errors`（失败/错误列表，含类型、消息、堆栈摘要）
- `status`（0/1/2/3）

### 5.2 Pytest 插件（Plan -> Items）

#### 5.2.1 CLI 入口

- `--plan=PATH`：计划文件路径（由引擎生成）
- `--task-id=ID`：便于日志与隔离（可选）
- `--allure=on/off`：Allure 开关（可选）

#### 5.2.2 收集策略（MVP）

- 在 collection 阶段读取 plan.json，生成 N 个 Items：
  - Item 名称包含 `collectionId/caseId/index`，便于定位与 stop/重跑
  - Item 持有 descriptor（jsonPath/debugData）

#### 5.2.3 执行策略（MVP）

Item.run 过程：

1) 创建/获取 collection 级共享对象：
   - `session` 与 `context` 复用策略与现有一致（collection 内共享）
2) 构造 Runtime，加载 case json（或 debugData）
3) 调用 `core/api` 执行器（保持现有执行逻辑）
4) Runtime.handleResult 计算最终 status
5) 组装 `case_info` 并推送到结果队列（供 Reporter 进程上传平台）
6) 若失败/错误：抛出 pytest 断言异常，使 pytest 结果与平台一致（平台仍以 case_info 为准）

### 5.3 平台结果回传（保持不变）

- `case_info` 结构保持不变（字段名与 status 语义保持 0/1/2/3）
- Reporter 继续保持 3 秒批量上传、stop 触发 flush + complete_task 的逻辑

### 5.4 AllureReporter（MVP：回放模式）

- 在每个 case 完成后，将 `transactionList` 回放生成 Allure step：
  - 每个 transaction -> 一个 step
  - transaction.log -> attach 文本
  - 请求/响应摘要（如有）-> attach JSON
- 将原始 `transactionList` 作为 JSON 附件整体 attach，保证排障信息完整

可选演进：若后续需要更细粒度与实时性，将 Runtime 的事务生命周期变为事件流，AllureReporter 订阅事件做方式一实时 step。

---

## 6. 计划文件（plan.json）规范（MVP）

引擎在任务执行进程生成 plan.json，建议最小结构：

```json
{
  "taskId": "T123",
  "collections": [
    {
      "collectionId": "C1",
      "cases": [
        {
          "caseId": "100",
          "index": 1,
          "caseType": "API",
          "caseName": "登录接口",
          "casePath": "data/T123/C1/100.json"
        }
      ]
    }
  ]
}
```

说明：

- 该 plan.json 是“引擎内部协议”，不需要平台参与修改；
- 为后续过滤/重跑/并行分发预留扩展字段：tags、priority、retry、timeout、resourceProfile 等。

---

## 7. 单元测试体系（与业务环境完全隔离）

### 7.1 测试分层（企业推荐）

- `tests/unit`：纯单元测试
  - 不连平台、不发真实 HTTP、不连 WebSocket、不起多进程
  - 对外部依赖一律 mock/fake
- `tests/integration`：集成测试（可选）
  - 允许读真实 case json、模拟本地 HTTP server、跑一个最小任务闭环

### 7.2 推荐目录结构

```
TestEngin/
  tests/
    unit/
      test_plan_builder.py
      test_runtime_status.py
      test_pytest_plugin_collect.py
      test_allure_replay.py
      test_report_batch_upload.py
    integration/
      test_task_mvp_run.py
    conftest.py
  pytest.ini
```

### 7.3 关键单测点（MVP 必测）

- Runtime：
  - recordFail/recordError + handleResult 的状态计算（0/1/2）
  - transactionList 组装完整性
- PlanBuilder：
  - task -> plan.json 的映射正确（collection 分组、路径正确）
- Pytest 插件：
  - `--plan` 能收集正确数量的 Items（`--collect-only`）
  - Item 执行能调用到 API 执行器（用 fake 执行器或 mock）
- Reporter：
  - 3 秒批量窗口与 stop flush 行为（mock LMApi.upload_result/complete_task）
- Allure 回放：
  - 给定 transactionList 能生成预期 step 与 attach（开启/关闭开关行为一致）

### 7.4 绝对隔离策略（必须遵守）

- 所有网络访问（requests/websocket）在 unit 测试中必须 mock 掉：
  - 统一在 `tests/conftest.py` 里提供 mock LMApi fixture
- 单元测试禁止读取真实 config.ini：
  - 测试用例通过 fixture 注入配置对象或环境变量
- 禁止 import 触发副作用（连接、线程启动）：
  - 引擎启动入口必须只在 `startup.py` 或显式函数调用时触发

---

## 8. 里程碑与代办（MVP 拆解）

### 8.1 里程碑

1) MVP-0：完成 Runtime 抽象与状态计算（不引入 pytest）
2) MVP-1：引擎生成 plan.json；pytest 插件能 collect Items（`--collect-only` 可用）
3) MVP-2：Items 执行调用 `core/api`，实时生成 `case_info` 并通过现有 Reporter 上传平台
4) MVP-3：Allure 回放报告可选输出（开关控制，不影响平台上报）
5) MVP-4：补齐单元测试与基本覆盖率门槛（建议 70%+，优先覆盖核心链路）

### 8.2 代办清单（供后续编码实现参考）

- 抽象 Runtime：替代 unittest._outcome，保留 core/api 依赖的方法签名
- 新增 plan.json 生成逻辑：从现有 task_analysis/test_plan 转换为 descriptor
- 新增 pytest 插件：支持 `--plan`，收集 Items，执行并上报
- 复用/适配现有 Reporter：保持平台上传协议不变
- 新增 AllureReporter：实现 transactionList 回放 + attach
- 建立 tests 体系：unit 优先，mock 网络与副作用
- 增加 pytest.ini：markers、testpaths、严格配置、可选覆盖率

---

## 9. 风险与对策（企业级视角）

### 9.1 风险：现有 core/api 对 `LMCase`/unittest 行为有隐式依赖

对策：

- Runtime 先做“接口兼容层”，保证 `recordFailStatus/recordErrorStatus` 行为一致；
- 用单测覆盖 `core/api` 的关键执行路径（用最小 json case 数据）验证行为不变。

### 9.2 风险：pytest 全局状态与引擎线程/多进程并发冲突

对策：

- MVP 阶段：每任务一个执行进程，进程内只启动一次 pytest；
- 后续并发增强优先走 xdist 多进程，而不是多线程多次调用 pytest.main。

### 9.3 风险：Allure 引入导致执行链路被污染或出错

对策：

- AllureReporter 独立模块 + 开关控制；
- Allure 仅旁路，不影响平台回传；Allure 失败不能导致任务失败（MVP 先保证这一点）。

---

## 10. 验收标准（MVP）

- API 任务能被拉取、执行、stop、complete，平台侧结果展示与原先一致（字段与状态一致）。
- 引擎侧 Pytest 输出可读（最少能定位到 collectionId/caseId/index）。
- Allure 可选开启：生成报告并包含 transactionList 与日志附件；关闭时不产生任何副作用。
- 单元测试可运行：不需要平台服务、不需要网络、不依赖真实配置；核心模块覆盖到位。

