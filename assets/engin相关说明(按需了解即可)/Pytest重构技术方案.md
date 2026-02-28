# Pytest重构技术方案

## 一、背景与需求

### 1.1 重构背景

随着流马测试平台的发展，对API测试执行框架提出了更高的要求。当前使用的Unittest框架在以下方面存在局限性：

| 方面 | Unittest现状 | 期望 |
|------|-------------|------|
| 扩展性 | 缺乏插件生态 | 支持分布式、失败重试等插件 |
| 报告能力 | 依赖自定义Result | 标准化的Allure报告 |
| 收集机制 | 动态创建类 | 更灵活的JSON文件收集 |
| 社区生态 | 相对小众 | 主流测试框架，资源丰富 |

### 1.2 重构目标

| 目标 | 说明 |
|------|------|
| 核心目标 | 将API测试执行框架从Unittest迁移至Pytest |
| 附加目标1 | 集成Allure报告作为补充报告能力 |
| 附加目标2 | 保留原有平台结果推送功能 |
| 附加目标3 | 便于后续扩展负载均衡和插件生态 |
| 约束条件 | 仅重构API模块，Web/App保持不变 |
| 质量目标 | MVP最小可行方案，最小改动原则 |

---

## 二、技术方案设计

### 2.1 整体架构

```
                    测试任务
                        │
          ┌─────────────┴─────────────┐
          │                           │
    检测测试类型                 检测测试类型
          │                           │
          ▼                           ▼
    纯API测试                   WEB/APP测试
          │                           │
          ▼                           ▼
    Pytest执行                  Unittest执行
    (新增)                      (原有)
          │                           │
          └─────────────┬─────────────┘
                        │
                        ▼
              result.py → queue
                        │
                        ▼
                  平台推送
```

### 2.2 核心设计原则

| 原则 | 说明 |
|------|------|
| 最小改动原则 | 核心执行逻辑（core/api/）完全不动 |
| 解耦原则 | Allure报告采用旁路观察者模式，不侵入测试代码 |
| 复用原则 | 复用现有ApiTestCase.execute()执行逻辑 |
| 渐进原则 | MVP优先，Web/App保持现状 |

### 2.3 模块划分

| 模块 | 状态 | 说明 |
|------|------|------|
| `core/api/testcase.py` | **不变** | ApiTestCase核心执行逻辑 |
| `core/api/teststep.py` | **不变** | 步骤执行器 |
| `core/api/collector.py` | **不变** | 数据收集器 |
| `core/template.py` | **不变** | 模板渲染引擎 |
| `app/run.py` | **小改** | 支持Pytest/Unittest双模式 |
| `app/json_collector.py` | **新增** | 自定义JSON收集器 |
| `app/pytest_hooks.py` | **新增** | pytest钩子函数 |

---

## 三、核心实现方案

### 3.1 JSON文件收集器（pytest_collect_file）

#### 设计思路

利用pytest的`pytest_collect_file`钩子函数，让pytest能够识别并收集平台下发的JSON测试文件。

#### 工作流程

```
pytest扫描目录
    ↓
pytest_collect_file() 钩子被调用
    ↓
检测.json文件 → 返回JSONFile收集器
    ↓
JSONFile.collect() 解析JSON
    ↓
为每个用例生成JSONCaseItem
    ↓
runtest()执行时调用ApiTestCase
```

### 3.2 旁路观察者模式（Allure报告）

#### 设计思路

采用旁路观察者模式，测试执行只负责生成`trans_list`数据，报告生成作为独立"观察者"。

#### 实现方式

| 阶段 | 处理方式 |
|------|---------|
| 测试执行时 | 正常执行，填充trans_list |
| 测试结束后 | pytest_runtest_makereport钩子观察trans_list |
| 报告生成 | 遍历trans_list，生成Allure step |

### 3.3 双通道报告机制

```
测试执行 → trans_list → pytest_runtest_makereport
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
        平台推送                        Allure报告
        (原有功能)                     (可选功能)
```

---

## 四、文件改动清单

### 4.1 新增文件

| 文件路径 | 说明 |
|---------|------|
| `app/json_collector.py` | 自定义JSON测试用例收集器 |
| `app/pytest_hooks.py` | pytest钩子函数（平台推送+Allure） |
| `tests/` | 单元测试目录 |

### 4.2 改动文件

| 文件路径 | 改动说明 |
|---------|---------|
| `app/run.py` | 支持Pytest/Unittest双模式执行 |
| `requirements.txt` | 添加pytest、allure-pytest依赖 |

### 4.3 保留文件

| 文件路径 | 说明 |
|---------|------|
| `core/api/testcase.py` | 完全不变，复用执行逻辑 |
| `core/api/teststep.py` | 完全不变 |
| `core/api/collector.py` | 完全不变 |
| `core/template.py` | 完全不变 |
| `app/case.py` | Web/App仍使用 |
| `app/result.py` | Web/App仍使用 |
| `core/web/` | 完全不变 |
| `core/app/` | 完全不变 |

---

## 五、Allure报告说明

### 5.1 设计原则

- **可选功能**：默认关闭，不影响平台推送
- **完全解耦**：采用旁路观察者模式，不侵入测试代码
- **独立使用**：仅供开发人员本地查看

### 5.2 开启方式

```bash
# 方式1：环境变量
set ALLURE_ENABLED=true
pytest tests/

# 方式2：命令行参数
pytest tests/ --allure-enabled
```

### 5.3 报告查看

```bash
# 生成报告
allure serve htmlcov/allure-results
```

---

## 六、单元测试说明

### 6.1 测试覆盖

| 模块 | 覆盖率 |
|------|--------|
| json_collector.py | 88% |
| pytest_hooks.py | 75% |

### 6.2 测试分类

| 测试类型 | 目录 | 说明 |
|---------|------|------|
| 单元测试 | test_collector/ | 测试JSON收集器 |
| 单元测试 | test_hooks/ | 测试钩子函数 |
| 集成测试 | test_integration/ | 全链路测试 |

---

## 七、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| pytest API调用方式不熟悉 | 可能无法正确执行 | 先行编写Demo验证 |
| trans_list数据格式兼容 | Allure报告可能不完整 | 适配器类做兼容处理 |
| 现有功能回归 | 破坏原有功能 | 保留原有执行路径 |
| Web/App执行受影响 | 其他测试类型不可用 | 区分case_type执行 |

---

## 八、后续扩展方向

### 8.1 负载均衡

Pytest天然支持pytest-xdist插件，可实现分布式并行执行：

```bash
pytest -n auto --dist loadscope
```

### 8.2 插件扩展

| 插件 | 用途 |
|------|------|
| pytest-xdist | 分布式并行执行 |
| pytest-rerunfailures | 失败重试 |
| pytest-html | HTML报告 |
| pytest-mark | 测试标记和分类 |

---

## 九、总结

本方案以最小改动原则为核心，通过：

1. **自定义收集器**（pytest_collect_file）实现JSON文件识别
2. **复用现有核心**（ApiTestCase）保持执行逻辑不变
3. **旁路观察者**（AllureObserver）实现报告解耦
4. **双通道输出**保留平台推送，新增Allure报告

实现从Unittest到Pytest的平滑迁移，同时为后续扩展负载均衡和插件生态奠定基础。
