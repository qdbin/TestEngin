# 流马测试平台 - 测试执行引擎

## 一、项目概述

### 1.1 项目定位

测试执行引擎（TestEngin）是流马自动化测试平台的分布式执行组件，采用 Python + Unittest/Pytest 双框架构建，负责接收平台下发的测试任务，解析测试数据，执行 API/WEB/APP 测试，并回传执行结果。

### 1.2 技术栈

| 技术 | 说明 |
|------|------|
| Python 3.8+ | 核心语言 |
| Unittest | WEB/APP测试框架（原有） |
| **Pytest** | **API测试框架（重构新增）** |
| Requests | HTTP请求处理 |
| Selenium | Web自动化 |
| uiautomator2 | Android自动化 |
| Facebook-wda | iOS自动化 |
| WebSocket | 与平台实时通信 |
| Allure | 报告生成（可选） |

### 1.3 核心特性

- **分布式架构**：引擎可注册到任意机器，突破资源限制
- **多测试类型**：支持 API、WebUI、AppUI 三种测试
- **双框架支持**：API使用Pytest，Web/App使用Unittest
- **实时通信**：WebSocket 长连接，任务实时推送
- **并发执行**：多进程 + 多线程，支持高并发
- **结果回传**：实时上传执行结果和截图日志
- **Allure报告**：可选的详细测试报告（独立于平台推送）

---

## 二、项目结构

```
TestEngin/
├── app/                          # 应用入口
│   ├── start.py                  # 启动入口
│   ├── run.py                   # 执行入口（支持Pytest/Unittest双模式）
│   ├── ws.py                    # WebSocket通信
│   ├── config.py                 # 配置加载
│   ├── log.py                   # 日志配置
│   ├── json_collector.py         # Pytest JSON收集器（新增）
│   └── pytest_hooks.py          # Pytest钩子函数（新增）
├── core/                         # 核心执行引擎
│   ├── api/                     # API测试执行器
│   │   ├── collector.py         # 用例收集
│   │   ├── testcase.py          # 用例执行
│   │   └── teststep.py          # 步骤执行
│   ├── web/                     # Web测试执行器
│   │   ├── driver/              # 浏览器驱动
│   │   ├── collector.py
│   │   ├── testcase.py
│   │   └── teststep.py
│   ├── app/                    # App测试执行器
│   │   ├── device/             # 设备操作
│   │   ├── collector.py
│   │   ├── testcase.py
│   │   └── teststep.py
│   ├── assertion.py             # 断言处理
│   └── template.py             # 模板处理
├── tools/                       # 工具模块
│   ├── funclib/                # 函数库
│   │   ├── provider/           # 函数提供者
│   │   └── load_faker.py      # Faker数据生成
│   └── utils/                  # 工具类
│       ├── sql.py              # 数据库操作
│       └── utils.py            # 通用工具
├── tests/                       # 单元测试（新增）
│   ├── test_collector/         # 收集器测试
│   ├── test_hooks/             # 钩子函数测试
│   ├── test_integration/       # 集成测试
│   └── fixtures/               # 测试数据
├── config/                      # 配置文件
│   └── config.ini              # 引擎配置
├── browser/                     # 浏览器驱动
│   └── readme.md               # 驱动说明
└── assets/                      # 说明文档
    └── engin相关说明(按需了解即可)/
```

---

## 三、核心模块说明

### 3.1 应用入口 (app/)

| 文件 | 职责 |
|------|------|
| start.py | 引擎启动入口，初始化配置和连接 |
| run.py | 测试执行入口，管理任务执行流程（支持Pytest/Unittest双模式） |
| ws.py | WebSocket 通信，与平台实时交互 |
| config.py | 配置文件加载和解析 |
| log.py | 日志配置和输出管理 |
| **json_collector.py** | **Pytest自定义JSON收集器（新增）** |
| **pytest_hooks.py** | **Pytest钩子函数+Allure报告（新增）** |

### 3.2 核心执行引擎 (core/)

#### API 测试执行器 (core/api/)
- **collector.py**：用例收集器，解析平台下发的测试数据
- **testcase.py**：用例执行器，管理单个用例的执行流程
- **teststep.py**：步骤执行器，执行具体的接口请求

#### Web 测试执行器 (core/web/)
- **driver/**：Selenium 封装，包含浏览器操作、元素定位、断言等
- **collector.py**：Web 用例收集
- **testcase.py**：Web 用例执行
- **teststep.py**：Web 步骤执行

#### App 测试执行器 (core/app/)
- **device/**：设备操作封装（Android uiautomator2 / iOS wda）
- **collector.py**：App 用例收集
- **testcase.py**：App 用例执行
- **teststep.py**：App 步骤执行

### 3.3 工具模块 (tools/)

| 模块 | 职责 |
|------|------|
| funclib/provider | 内置函数提供者 |
| load_faker | Faker 数据生成封装 |
| utils/sql | 数据库操作工具 |
| utils/utils | 通用工具函数 |

### 3.4 测试模块 (tests/)

| 目录 | 职责 |
|------|------|
| test_collector | JSON收集器单元测试 |
| test_hooks | Pytest钩子函数单元测试 |
| test_integration | 全链路集成测试 |
| fixtures | 测试数据和fixtures |

---

## 四、执行模式说明

### 4.1 双模式执行架构

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

### 4.2 Pytest模式（API测试）

当检测到纯API测试时，使用Pytest执行：

```python
# app/run.py
def run_test(self):
    test_types = set(case.get("test_type") for case in self.plan_tuple)
    
    if len(test_types) == 1 and "API" in test_types:
        self._run_with_pytest()  # Pytest执行
    else:
        self._run_with_unittest()  # Unittest执行
```

**Pytest执行流程**：
1. `pytest_collect_file` 钩子识别JSON文件
2. `JSONFile` 收集器解析JSON数据
3. `JSONCaseItem` 执行测试
4. 复用 `ApiTestCase.execute()` 执行逻辑
5. `pytest_runtest_makereport` 收集结果

### 4.3 Unittest模式（WEB/APP测试）

WEB和APP测试保持原有Unittest执行方式不变。

---

## 五、Allure报告说明

### 5.1 功能特点

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

# 或者
allure generate htmlcov/allure-results -o allure-report
allure open allure-report
```

---

## 六、单元测试说明

### 6.1 测试覆盖

```bash
# 运行测试并查看覆盖率
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

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

## 七、数据格式说明

### 7.1 任务数据 (case_data.json)

引擎从平台接收的测试数据格式：

```json
{
    "taskId": "任务ID",
    "testType": "api/web/app",
    "testClass": "测试类名",
    "cases": [
        {
            "caseId": "用例ID",
            "name": "用例名称",
            "steps": [
                {
                    "stepId": "步骤ID",
                    "action": "请求方法",
                    "target": "请求URL",
                    "value": "请求参数",
                    "assertions": []
                }
            ]
        }
    ]
}
```

### 7.2 结果数据 (case_result.json)

引擎回传给平台的结果格式：

```json
{
    "taskId": "任务ID",
    "results": [
        {
            "caseId": "用例ID",
            "status": "pass/fail/error",
            "startTime": "开始时间",
            "endTime": "结束时间",
            "duration": 1000,
            "transList": [
                {
                    "id": "步骤ID",
                    "status": 1,
                    "log": "执行日志",
                    "screenShotList": []
                }
            ]
        }
    ]
}
```

---

## 八、配置说明

### 8.1 config.ini 配置项

```ini
[Platform]
url = http://localhost:8080  # 平台后端地址
engine-code = your_code      # 引擎编码
engine-secret = your_secret  # 引擎密钥

[Engine]
max-run = 3                  # 最大并发任务数

[WebDriver]
path = chromedriver          # 驱动路径
options = --no-sandbox       # 启动选项
```

### 8.2 环境要求

- Python 3.8+
- Chrome 浏览器 + ChromeDriver
- MySQL/Redis（平台依赖）

---

## 九、开发指南

### 9.1 添加自定义函数

```python
# tools/funclib/provider/provider.py
def custom_function(param):
    """
    自定义函数说明
    @param {string} param - 参数说明
    @returns {string} 返回值说明
    """
    # 函数逻辑
    return result
```

### 9.2 添加新断言类型

```python
# core/assertion.py
def assert_custom(actual, expected):
    """
    自定义断言逻辑
    @param actual: 实际值
    @param expected: 期望值
    @returns: 断言结果
    """
    return actual == expected
```

### 9.3 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest tests/

# 运行测试并查看覆盖率
pytest tests/ --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_collector/ -v
```

---

## 十、相关文档

- [引擎业务逻辑设计](./assets/engin相关说明(按需了解即可)/业务逻辑设计.md)
- [功能模块设计](./assets/engin相关说明(按需了解即可)/功能模块设计.md)
- [数据格式说明](./assets/engin相关说明(按需了解即可)/补充（数据详情）/json数据设计及示例.md)
- [Pytest重构技术方案](./assets/engin相关说明(按需了解即可)/Pytest重构技术方案.md)

---

## 十一、部署与启动

### 11.1 本地启动

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 配置引擎参数
# 编辑 config/config.ini，填入 engine-code 和 engine-secret

# 3. 启动引擎
python3 startup.py
```

### 11.2 Docker 部署

详见官方部署文档：http://www.liumatest.cn/deployDoc

---

## 十二、联系与支持

- 演示平台：http://demo-ee.liumatest.cn
- 官网地址：http://www.liumatest.cn
- 社区地址：http://community.liumatest.cn
- B站课堂：https://www.bilibili.com/cheese/play/ss7009
