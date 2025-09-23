# JSON数据设计及示例

## 文档概述

本文档基于LiuMa-engine自动化测试引擎的源码分析，详细说明项目中所有核心数据对象的JSON设计规范和示例。文档按照由浅入深的方式，覆盖项目运作所依赖的所有数据设计对象，确保与源码字段原意和设计思想完全一致。

## 数据对象分层设计

### 1. 基础配置数据对象

#### 1.1 引擎配置对象 (EngineConfig)

引擎的基础配置信息，用于初始化测试引擎的运行环境和连接参数。

```json
{
  "url": "string",           // 测试平台服务器地址
  "engine": "string",        // 引擎标识码
  "secret": "string",        // 引擎密钥
  "header": {                 // HTTP请求头配置
    "Content-Type": "string", // 内容类型，通常为application/json
    "token": "string"         // 访问令牌
  },
  "webdriver": {              // WebDriver配置
    "chrome-options": "string", // Chrome浏览器启动选项
    "firefox-options": "string" // Firefox浏览器启动选项
  },
  "run_setting": {            // 运行设置
    "max-run": "string"        // 最大运行次数
  }
}
```

**示例：**
```json
{
  "url": "https://api.liuma-test.com",
  "engine": "ENGINE-001",
  "secret": "abc123def456ghi789",
  "header": {
    "Content-Type": "application/json",
    "token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "webdriver": {
    "chrome-options": "--headless --no-sandbox --disable-dev-shm-usage",
    "firefox-options": "--headless --width=1920 --height=1080"
  },
  "run_setting": {
    "max-run": "3"
  }
}
```

### 2. 任务管理数据对象

#### 2.1 测试任务对象 (Task)

测试任务的完整配置信息，包含任务元数据、测试集合列表和执行参数。

```json
{
  "taskId": "string",                    // 任务唯一标识符
  "taskType": "string",                  // 任务类型：normal/urgent/scheduled
  "taskName": "string",                  // 任务名称
  "downloadUrl": "string",               // 测试数据下载地址
  "testCollectionList": [],              // 测试集合列表，类型为TestCollection数组
  "executionConfig": {                   // 执行配置
    "maxRetry": "number",                // 最大重试次数
    "timeout": "number",                 // 超时时间（秒）
    "parallel": "boolean",               // 是否并行执行
    "threadCount": "number",              // 线程数量
    "reportConfig": {                     // 报告配置
      "generateReport": "boolean",        // 是否生成报告
      "reportFormat": "string",           // 报告格式：html/json/xml
      "reportPath": "string"              // 报告保存路径
    },
    "notificationConfig": {               // 通知配置
      "enabled": "boolean",               // 是否启用通知
      "email": {
        "recipients": [],                  // 收件人列表
        "subject": "string",              // 邮件主题
        "template": "string"               // 邮件模板
      },
      "webhook": {
        "url": "string",                   // Webhook地址
        "method": "string",                // 请求方法
        "headers": {}                      // 请求头
      }
    }
  },
  "environment": {                       // 环境配置
    "baseUrl": "string",                 // 基础URL
    "database": {                         // 数据库连接配置
      "host": "string",                   // 数据库主机
      "port": "number",                   // 数据库端口
      "username": "string",               // 用户名
      "password": "string",               // 密码
      "database": "string",               // 数据库名
      "type": "string",                   // 数据库类型：mysql/postgresql/oracle等
      "charset": "string",                // 字符集
      "pool": {                           // 连接池配置
        "minSize": "number",              // 最小连接数
        "maxSize": "number",              // 最大连接数
        "timeout": "number"               // 连接超时时间
      }
    },
    "variables": {                        // 环境变量
      "global": {},                       // 全局变量
      "runtime": {},                      // 运行时变量
      "secrets": {}                       // 敏感信息变量
    },
    "proxy": {                           // 代理配置
      "enabled": "boolean",               // 是否启用代理
      "http": "string",                   // HTTP代理地址
      "https": "string",                  // HTTPS代理地址
      "auth": {                           // 代理认证
        "username": "string",             // 用户名
        "password": "string"              // 密码
      }
    }
  }
}
```

**示例：**
```json
{
  "taskId": "TASK-20241201-001",
  "taskType": "normal",
  "taskName": "用户管理模块回归测试",
  "downloadUrl": "https://api.liuma-test.com/download/TASK-20241201-001.zip",
  "testCollectionList": [
    {
      "collectionId": "COL-USER-001",
      "collectionName": "用户登录测试集",
      "testCaseList": []
    }
  ],
  "executionConfig": {
    "maxRetry": 2,
    "timeout": 300,
    "parallel": true,
    "threadCount": 4,
    "reportConfig": {
      "generateReport": true,
      "reportFormat": "html",
      "reportPath": "./reports/test_report_${@timestamp()}.html"
    },
    "notificationConfig": {
      "enabled": true,
      "email": {
        "recipients": ["test@example.com", "admin@example.com"],
        "subject": "测试执行结果通知 - ${taskName}",
        "template": "default"
      },
      "webhook": {
        "url": "https://hooks.slack.com/services/xxx/yyy/zzz",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer ${webhook_token}"
        }
      }
    }
  },
  "environment": {
    "baseUrl": "https://test-api.example.com",
    "database": {
      "host": "localhost",
      "port": 3306,
      "username": "test_user",
      "password": "test_pass",
      "database": "test_db",
      "type": "mysql",
      "charset": "utf8mb4",
      "pool": {
        "minSize": 5,
        "maxSize": 20,
        "timeout": 30
      }
    },
    "variables": {
      "global": {
        "app_version": "1.0.0",
        "test_env": "staging",
        "base_timeout": 30
      },
      "runtime": {
        "admin_token": "${@generate_token()}",
        "test_user_id": "12345",
        "session_id": "${@uuid()}"
      },
      "secrets": {
        "api_key": "${@env('API_KEY')}",
        "db_password": "${@env('DB_PASSWORD')}"
      }
    },
    "proxy": {
      "enabled": false,
      "http": "http://proxy.company.com:8080",
      "https": "https://proxy.company.com:8443",
      "auth": {
        "username": "proxy_user",
        "password": "proxy_pass"
      }
    }
  }
}
```

#### 2.2 测试集合对象 (TestCollection)

测试用例的逻辑分组，包含多个相关的测试用例。

```json
{
  "collectionId": "string",              // 集合唯一标识符
  "collectionName": "string",            // 集合名称
  "description": "string",               // 集合描述
  "testCaseList": [],                    // 测试用例列表，类型为TestCase数组
  "setupScript": "string",               // 前置脚本
  "teardownScript": "string",            // 后置脚本
  "variables": {                          // 集合级变量
    "common": {},                         // 通用变量
    "environment": {},                    // 环境相关变量
    "testData": {}                        // 测试数据变量
  },
  "priority": "string",                  // 优先级：high/medium/low
  "tags": [],                            // 标签列表
  "dependencies": [],                    // 依赖的其他集合ID列表
  "retryConfig": {                       // 重试配置
    "enabled": "boolean",                // 是否启用重试
    "maxRetries": "number",              // 最大重试次数
    "retryInterval": "number"             // 重试间隔（秒）
  },
  "parallelConfig": {                    // 并行配置
    "enabled": "boolean",                // 是否启用并行执行
    "maxThreads": "number"               // 最大线程数
  }
}
```

**示例：**
```json
{
  "collectionId": "COL-USER-001",
  "collectionName": "用户登录测试集",
  "description": "测试用户登录相关功能，包括正常登录、异常登录和权限验证",
  "testCaseList": [
    {
      "caseId": "TC-LOGIN-001",
      "caseName": "正常用户登录测试",
        "index":001
    }
  ],
  "setupScript": "# 初始化测试数据\nsys_put('test_start_time', '${@current_timestamp()}')\nsys_put('collection_id', '${collectionId}')\nprint('开始执行用户登录测试集')",
  "teardownScript": "# 清理测试数据\nsys_put('test_end_time', '${@current_timestamp()}')\nprint('用户登录测试集执行完成')\n# 清理临时数据\nsys_put('temp_token', '')",
  "variables": {
    "common": {
      "valid_username": "test_user",
      "valid_password": "Test123456",
      "invalid_password": "wrong_pass",
      "test_email": "test@example.com"
    },
    "environment": {
      "login_url": "${baseUrl}/api/v1/auth/login",
      "logout_url": "${baseUrl}/api/v1/auth/logout",
      "profile_url": "${baseUrl}/api/v1/user/profile"
    },
    "testData": {
      "user_roles": ["admin", "user", "guest"],
      "test_accounts": [
        {"username": "admin_user", "password": "Admin123", "role": "admin"},
        {"username": "normal_user", "password": "User123", "role": "user"}
      ]
    }
  },
  "priority": "high",
  "tags": ["authentication", "login", "security", "smoke"],
  "dependencies": ["COL-SETUP-001"],
  "retryConfig": {
    "enabled": true,
    "maxRetries": 2,
    "retryInterval": 5
  },
  "parallelConfig": {
    "enabled": false,
    "maxThreads": 1
  }
}
```

### 3. 测试用例数据对象

#### 3.1 基础测试用例对象 (TestCase)

所有类型测试用例的基础结构，包含通用的测试用例信息。

```json
{
  "caseId": "string",                    // 用例唯一标识符
  "caseName": "string",                  // 用例名称
  "caseType": "string",                  // 用例类型：API/WEB/APP
  "description": "string",               // 用例描述
  "priority": "string",                  // 优先级：high/medium/low
  "tags": [],                            // 标签数组，类型为string数组
  "author": "string",                    // 用例作者
  "createTime": "string",                // 创建时间
  "updateTime": "string",                // 更新时间
  "enabled": "boolean",                  // 是否启用
  "timeout": "number",                   // 超时时间（秒）
  "retryCount": "number",                // 重试次数
  "preScript": "string",                 // 前置脚本
  "postScript": "string",                // 后置脚本
  "variables": {                          // 用例级变量
    "input": {},                          // 输入参数变量
    "expected": {},                       // 期望结果变量
    "runtime": {}                         // 运行时变量
  },
  "assertions": [],                      // 断言列表，类型为Assertion数组
  "testData": {                        // 测试数据配置
    "source": "string",                   // 数据来源：inline/file/database/api
    "format": "string",                   // 数据格式：json/csv/xml/yaml
    "inline": {                           // 内联数据
      "parameters": {},                   // 参数数据
      "expected": {},                     // 期望结果数据
      "fixtures": {}                      // 固定数据
    },
    "file": {                             // 文件数据源
      "path": "string",                   // 文件路径
      "sheet": "string",                  // Excel工作表名
      "encoding": "string",               // 文件编码
      "delimiter": "string"               // CSV分隔符
    },
    "database": {                         // 数据库数据源
      "connection": "string",             // 连接配置
      "query": "string",                  // 查询语句
      "parameters": {}                    // 查询参数
    },
    "api": {                              // API数据源
      "url": "string",                    // API地址
      "method": "string",                 // 请求方法
      "headers": {},                      // 请求头
      "auth": {}                          // 认证信息
    },
    "transformation": {                   // 数据转换
      "enabled": "boolean",               // 是否启用转换
      "script": "string",                 // 转换脚本
      "mapping": {}                       // 字段映射
    },
    "validation": {                       // 数据验证
      "enabled": "boolean",               // 是否启用验证
      "schema": {},                       // 数据模式
      "rules": []                         // 验证规则
    },
    "cache": {                            // 数据缓存
      "enabled": "boolean",               // 是否启用缓存
      "ttl": "number",                    // 缓存时间
      "key": "string"                     // 缓存键
    }
   },
    "setupHooks": {                        // 前置钩子配置
    "database": [],                       // 数据库前置操作
    "api": [],                            // API前置调用
    "files": []                           // 文件前置操作
  },
  "teardownHooks": {                     // 后置钩子配置
    "database": [],                       // 数据库后置操作
    "api": [],                            // API后置调用
    "files": []                           // 文件后置操作
  },
  "dataProviders": [],                   // 数据提供者列表
  "skipConditions": []                   // 跳过条件列表
}
```

**示例：**
```json
{
  "caseId": "TC-LOGIN-001",
  "caseName": "正常用户登录测试",
  "caseType": "API",
  "description": "验证用户使用正确的用户名和密码能够成功登录系统",
  "testData": {
    "caseId": "TC-LOGIN-001",
  	"caseName": "正常用户登录测试",
      "functions":{}
    "apiList": []
  },
  "priority": "high",
  "tags": ["login", "authentication", "smoke"],
  "author": "张三",
  "createTime": "2024-12-01T10:00:00Z",
  "updateTime": "2024-12-01T15:30:00Z",
  "enabled": true,
  "timeout": 30,
  "retryCount": 2,
  "preScript": "# 准备测试数据\nsys_put('username', '${valid_username}')\nsys_put('password', '${valid_password}')\nsys_put('test_start_time', '${@current_timestamp()}')\nprint('开始执行登录测试用例')",
  "postScript": "# 保存登录token\nsys_put('login_token', '${response.json.data.token}')\nsys_put('user_info', '${response.json.data.userInfo}')\nprint('登录测试用例执行完成')",
  "variables": {
    "input": {
      "username": "${valid_username}",
      "password": "${valid_password}",
      "captcha_required": false,
      "remember_me": true
    },
    "expected": {
      "status_code": 200,
      "business_code": "0",
      "message": "登录成功",
      "token_length": 32
    },
    "runtime": {
      "request_id": "${@uuid()}",
      "client_ip": "127.0.0.1",
      "user_agent": "LiuMa-Engine/1.0"
    }
  },
  "assertions": [
    {
      "type": "equalsNumber",
      "actual": "${response.status_code}",
      "expected": "${expected.status_code}",
      "description": "验证响应状态码为200"
    },
    {
      "type": "equal",
      "actual": "${response.json.code}",
      "expected": "${expected.business_code}",
      "description": "验证业务状态码"
    },
    {
      "type": "contains",
      "actual": "${response.json.message}",
      "expected": "${expected.message}",
      "description": "验证响应消息"
    }
  ],
  "setupHooks": {
    "database": [
      {
        "type": "execute",
        "sql": "UPDATE users SET login_attempts = 0 WHERE username = '${input.username}'",
        "description": "重置用户登录尝试次数"
      }
    ],
    "api": [
      {
        "name": "获取验证码",
        "url": "${baseUrl}/api/v1/captcha",
        "method": "GET",
        "saveAs": "captcha_info"
      }
    ],
    "files": [
      {
        "action": "create",
        "path": "./temp/login_test_${@timestamp()}.log",
        "content": "Login test started at ${@current_timestamp()}"
      }
    ]
  },
  "teardownHooks": {
    "database": [
      {
        "type": "execute",
        "sql": "INSERT INTO login_logs (username, login_time, result) VALUES ('${input.username}', NOW(), 'SUCCESS')",
        "description": "记录登录日志"
      }
    ],
    "api": [],
    "files": [
      {
        "action": "append",
        "path": "./temp/login_test_${@timestamp()}.log",
        "content": "Login test completed at ${@current_timestamp()}"
      }
    ]
  },
  "dataProviders": [
    {
      "name": "user_credentials",
      "type": "csv",
      "source": "./data/test_users.csv",
      "columns": ["username", "password", "expected_result"]
    }
  ],
  "skipConditions": [
    {
      "condition": "${@env('SKIP_LOGIN_TESTS')} == 'true'",
      "reason": "登录测试在当前环境中被跳过"
    }
  ]
}
```

### 4. API测试数据对象

#### 4.1 API测试用例对象 (ApiTestCase)

继承自基础测试用例，专门用于API接口测试。

```json
{
  "caseId": "string",
  "caseName": "string",
  "caseType": "API",
  "testData": {
    "apiList": [],                       // API请求列表，类型为ApiRequest数组
    "loopController": {                  // 循环控制器配置
      "enabled": "boolean",              // 是否启用循环
      "loopType": "string",              // 循环类型：count/condition/data
      "loopCount": "number",             // 循环次数
      "condition": "string",             // 循环条件表达式
      "dataSource": {                    // 数据源配置
        "type": "string",                // 数据源类型：csv/json/database
        "source": "string",              // 数据源路径或SQL
        "columns": []                    // 数据列名
      },
      "breakOnError": "boolean"          // 出错时是否中断循环
    },
    "conditionalController": {           // 条件控制器配置
      "enabled": "boolean",              // 是否启用条件控制
      "condition": "string",             // 条件表达式
      "executeWhenTrue": "boolean",      // 条件为真时是否执行
      "description": "string"            // 条件描述
    },
    "functions": {                       // 自定义函数配置
      "customFunctions": [],             // 自定义函数列表
      "builtinFunctions": [],            // 内置函数配置
      "globalVariables": {}              // 全局变量
    },
    "dataValidation": {                  // 数据验证配置
      "schema": {},                       // JSON Schema验证
      "rules": []                        // 自定义验证规则
    },
    "performance": {                     // 性能测试配置
      "enabled": "boolean",              // 是否启用性能监控
      "thresholds": {                    // 性能阈值
        "responseTime": "number",        // 响应时间阈值（毫秒）
        "throughput": "number"           // 吞吐量阈值（请求/秒）
      }
    }
  }
}
```

#### 4.2 API请求对象 (ApiRequest)

API接口请求的完整配置信息，包含请求参数、头部、体等。根据源码中ApiRequestCollector的实际结构定义。

```json
{
  "name": "string",                      // 接口名称
  "url": "string",                       // 请求URL
  "method": "string",                    // 请求方法：GET/POST/PUT/DELETE等
  "headers": {},                         // 请求头配置，键值对格式
  "params": {},                          // 查询参数，键值对格式
  "data": {},                            // 请求体数据（表单格式）
  "json": {},                            // 请求体数据（JSON格式）
  "files": {},                           // 文件上传配置
  "auth": {},                            // 认证配置
  "proxies": {},                         // 代理配置
  "timeout": "number",                   // 超时时间（秒）
  "allow_redirects": "boolean",          // 是否允许重定向
  "verify": "boolean",                   // 是否验证SSL证书
  "stream": "boolean",                   // 是否流式传输
  "cert": "string",                      // 客户端证书路径
  "cookies": {},                         // Cookie配置
  "hooks": {},                           // 请求钩子
  "extractors": [],                      // 数据提取器列表
  "assertions": [],                      // 断言列表
  "looper": {},                          // 循环控制器
  "conditions": [],                      // 条件控制器
  "setup_script": "string",              // 前置脚本
  "teardown_script": "string",           // 后置脚本
  "setup_sql": "string",                 // 前置SQL
  "teardown_sql": "string",              // 后置SQL
  "wait_time_before": "number",          // 请求前等待时间
  "wait_time_after": "number"            // 请求后等待时间
}
```

**示例：**
```json
{
  "name": "用户登录接口",
  "url": "${baseUrl}/api/v1/auth/login",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "User-Agent": "LiuMa-Engine/1.0",
    "X-Request-ID": "${@uuid()}"
  },
  "params": {},
  "data": {},
  "json": {
    "username": "${sys_get('username')}",
    "password": "${sys_get('password')}",
    "captcha": "${@random_string(4)}",
    "rememberMe": true
  },
  "files": {},
  "auth": {},
  "proxies": {},
  "timeout": 30,
  "allow_redirects": true,
  "verify": false,
  "stream": false,
  "cert": null,
  "cookies": {},
  "hooks": {},
  "extractors": [
    {
      "name": "login_token",
      "type": "jsonpath",
      "expression": "$.data.token",
      "description": "提取登录令牌"
    },
    {
      "name": "user_id",
      "type": "jsonpath",
      "expression": "$.data.userInfo.id",
      "description": "提取用户ID"
    }
  ],
  "assertions": [
    {
      "type": "equalsNumber",
      "actual": "${response.status_code}",
      "expected": 200,
      "description": "验证HTTP状态码"
    },
    {
      "type": "equal",
      "actual": "${response.json.code}",
      "expected": "0",
      "description": "验证业务状态码"
    },
    {
      "type": "contains",
      "actual": "${response.json.message}",
      "expected": "成功",
      "description": "验证响应消息"
    },
    {
      "type": "notEmpty",
      "actual": "${response.json.data.token}",
      "expected": null,
      "description": "验证token不为空"
    }
  ],
  "looper": {},
  "conditions": [],
  "setup_script": "print('开始执行登录请求')",
  "teardown_script": "print('登录请求执行完成')",
  "setup_sql": "",
  "teardown_sql": "",
  "wait_time_before": 0,
  "wait_time_after": 1
}
```

#### 4.3 请求体数据对象 (RequestBody)

API请求体的详细配置，支持多种数据格式。

```json
{
  "dataType": "string",                  // 数据类型：json/form/raw/binary
  "data": {                              // 具体数据内容
    "json": {},                          // JSON格式数据
    "form": {                            // 表单数据
      "fields": {},                      // 表单字段
      "files": []                        // 文件字段
    },
    "raw": "string",                     // 原始文本数据
    "binary": {                          // 二进制数据
      "content": "string",               // Base64编码内容
      "filename": "string",              // 文件名
      "contentType": "string"            // 内容类型
    },
    "xml": "string",                     // XML格式数据
    "graphql": {                         // GraphQL数据
      "query": "string",                 // 查询语句
      "variables": {},                   // 变量
      "operationName": "string"          // 操作名称
    }
  },
  "encoding": "string",                  // 编码格式：utf-8/gbk等
  "compression": "string",               // 压缩格式：gzip/deflate
  "validation": {                        // 数据验证
    "enabled": "boolean",                // 是否启用验证
    "schema": {},                        // 数据模式
    "strict": "boolean"                  // 严格模式
  },
  "transformation": {                    // 数据转换
    "enabled": "boolean",                // 是否启用转换
    "preProcess": "string",              // 预处理脚本
    "postProcess": "string"              // 后处理脚本
  }
}
```

**JSON格式示例：**
```json
{
  "dataType": "json",
  "data": {
    "username": "${username}",
    "password": "${password}",
    "loginType": "password",
    "deviceInfo": {
      "deviceId": "${@uuid()}",
      "platform": "web",
      "version": "1.0.0"
    }
  },
  "encoding": "utf-8"
}
```

**表单格式示例：**
```json
{
  "dataType": "form",
  "data": {
    "username": "test_user",
    "password": "Test123456",
    "submit": "登录"
  },
  "encoding": "utf-8"
}
```

### 5. Web测试数据对象

#### 5.1 Web测试用例对象 (WebTestCase)

专门用于Web自动化测试的用例结构。

```json
{
  "caseId": "string",
  "caseName": "string",
  "caseType": "WEB",
  "testData": {
    "stepList": [],                      // 操作步骤列表，类型为WebStep数组
    "pageObjects": {                     // 页面对象配置
      "pages": {},                       // 页面定义
      "elements": {},                    // 元素定义
      "actions": {}                      // 动作定义
    },
    "browserConfig": {                   // 浏览器配置
      "browserType": "string",           // 浏览器类型：chrome/firefox/safari/edge
      "headless": "boolean",             // 是否无头模式
      "windowSize": {                    // 窗口大小
        "width": "number",               // 宽度
        "height": "number"               // 高度
      },
      "options": [],                     // 浏览器启动选项
      "capabilities": {},                // 浏览器能力配置
      "proxy": {                         // 代理配置
        "enabled": "boolean",            // 是否启用代理
        "host": "string",                // 代理主机
        "port": "number"                 // 代理端口
      }
    },
    "waitConfig": {                      // 等待配置
      "implicitWait": "number",          // 隐式等待时间（秒）
      "explicitWait": "number",          // 显式等待时间（秒）
      "pageLoadTimeout": "number",       // 页面加载超时时间（秒）
      "scriptTimeout": "number"          // 脚本执行超时时间（秒）
    },
    "screenshotConfig": {                // 截图配置
      "enabled": "boolean",              // 是否启用截图
      "onFailure": "boolean",            // 失败时是否截图
      "onSuccess": "boolean",            // 成功时是否截图
      "path": "string",                  // 截图保存路径
      "format": "string"                 // 截图格式：png/jpg
    },
    "videoConfig": {                     // 视频录制配置
      "enabled": "boolean",              // 是否启用视频录制
      "path": "string",                  // 视频保存路径
      "quality": "string"                // 视频质量：high/medium/low
    }
  }
}
```

#### 5.2 Web操作步骤对象 (WebStep)

Web自动化测试中的单个操作步骤。

```json
{
  "stepId": "string",                    // 步骤唯一标识符
  "stepName": "string",                  // 步骤名称
  "action": "string",                    // 操作类型：click/input/select/wait等
  "locator": {                        // 元素定位器
    "type": "string",                    // 定位类型：id/name/xpath/css/class等
    "value": "string",                   // 定位值
    "index": "number",                   // 元素索引（当有多个匹配元素时）
    "frame": "string"                    // 所在框架名称
  },
  "value": "string",                     // 操作值
  "timeout": "number",                   // 超时时间
  "screenshot": "boolean",               // 是否截图
  "description": "string",               // 步骤描述
  "waitCondition": {                     // 等待条件
    "type": "string",                    // 等待类型：visible/clickable/present等
    "timeout": "number"                  // 等待超时时间
  },
  "retry": {                             // 重试配置
    "enabled": "boolean",                // 是否启用重试
    "maxRetries": "number",              // 最大重试次数
    "interval": "number"                 // 重试间隔（秒）
  },
  "validation": {                        // 验证配置
    "enabled": "boolean",                // 是否启用验证
    "assertions": []                     // 断言列表
  },
  "data": {                              // 步骤数据
    "input": {},                         // 输入数据
    "expected": {}                       // 期望结果
  }
}
```

**示例：**
```json
{
  "stepId": "STEP-001",
  "stepName": "打开登录页面",
  "action": "navigate",
  "locator": {
    "type": "url",
    "value": "${baseUrl}/login"
  },
  "value": null,
  "timeout": 10,
  "screenshot": true,
  "description": "导航到登录页面"
}
```

#### 5.3 元素定位器对象 (Locator)

Web元素的定位配置信息。

```json
{
  "type": "string",                      // 定位类型：id/name/xpath/css/class等
  "value": "string",                     // 定位值
  "index": "number",                     // 元素索引（当有多个匹配元素时）
  "frame": "string"                      // 所在框架名称
}
```

**示例：**
```json
{
  "type": "xpath",
  "value": "//input[@placeholder='请输入用户名']",
  "index": 0,
  "frame": null
}
```

### 6. App测试数据对象

#### 6.1 App测试用例对象 (AppTestCase)

专门用于移动应用自动化测试的用例结构。

```json
{
  "caseId": "string",
  "caseName": "string",
  "caseType": "APP",
  "testData": {
    "stepList": [],                      // 操作步骤列表，类型为AppStep数组
    "deviceConfig": {                    // 设备配置
      "platformName": "string",          // 平台名称：iOS/Android
      "platformVersion": "string",       // 平台版本
      "deviceName": "string",            // 设备名称
      "udid": "string",                  // 设备唯一标识
      "orientation": "string",           // 屏幕方向：portrait/landscape
      "resolution": {                    // 屏幕分辨率
        "width": "number",               // 宽度
        "height": "number"               // 高度
      },
      "capabilities": {                 // 设备能力配置
        "automationName": "string",       // 自动化引擎名称
        "platformVersion": "string",      // 平台版本
        "deviceName": "string",           // 设备名称
        "udid": "string",                 // 设备唯一标识符
        "orientation": "string",          // 屏幕方向
        "autoGrantPermissions": "boolean", // 自动授权权限
        "noReset": "boolean",             // 不重置应用
        "fullReset": "boolean",           // 完全重置
        "newCommandTimeout": "number",    // 新命令超时时间
        "language": "string",             // 语言设置
        "locale": "string",               // 地区设置
        "timezone": "string",             // 时区设置
        "customCapabilities": {}          // 自定义能力
      }
    },
    "appConfig": {                       // 应用配置
      "appPackage": "string",            // 应用包名
      "appActivity": "string",           // 应用活动
      "appPath": "string",               // 应用路径
      "bundleId": "string",              // iOS应用Bundle ID
      "autoLaunch": "boolean",           // 是否自动启动
      "noReset": "boolean",              // 是否重置应用
      "fullReset": "boolean",            // 是否完全重置
      "permissions": []                  // 应用权限列表
    },
    "gestureConfig": {                   // 手势配置
      "swipeSpeed": "number",            // 滑动速度
      "tapDuration": "number",           // 点击持续时间
      "longPressDuration": "number",     // 长按持续时间
      "pinchSpeed": "number",            // 缩放速度
      "rotationSpeed": "number"          // 旋转速度
    },
    "networkConfig": {                   // 网络配置
      "enabled": "boolean",              // 是否启用网络模拟
      "type": "string",                  // 网络类型：wifi/3g/4g/5g/offline
      "speed": "string",                 // 网络速度：fast/slow/medium
      "latency": "number"                // 网络延迟（毫秒）
    },
    "recordingConfig": {                 // 录制配置
      "enabled": "boolean",              // 是否启用录制
      "videoPath": "string",             // 视频保存路径
      "quality": "string",               // 录制质量：high/medium/low
      "fps": "number"                    // 帧率
    }
  }
}
```

#### 6.2 App操作步骤对象 (AppStep)

移动应用自动化测试中的单个操作步骤。

```json
{
  "stepId": "string",                    // 步骤唯一标识符
  "stepName": "string",                  // 步骤名称
  "action": "string",                    // 操作类型：tap/swipe/input/wait等
  "locator": {                        // 元素定位器
    "type": "string",                    // 定位类型：id/xpath/accessibility_id/class等
    "value": "string",                   // 定位值
    "index": "number",                   // 元素索引
    "context": "string"                  // 上下文信息
  },
  "value": "string",                     // 操作值
  "coordinate": {                        // 坐标信息（用于坐标点击）
    "x": "number",                       // X坐标
    "y": "number",                       // Y坐标
    "relative": "boolean"                // 是否相对坐标
  },
  "timeout": "number",                   // 超时时间
  "screenshot": "boolean",               // 是否截图
  "description": "string",               // 步骤描述
  "gesture": {                           // 手势配置
    "type": "string",                    // 手势类型：tap/swipe/pinch/rotate等
    "duration": "number",                // 手势持续时间
    "direction": "string",               // 手势方向：up/down/left/right
    "distance": "number"                 // 手势距离
  },
  "validation": {                        // 验证配置
    "enabled": "boolean",                // 是否启用验证
    "assertions": []                     // 断言列表
  },
  "retry": {                             // 重试配置
    "enabled": "boolean",                // 是否启用重试
    "maxRetries": "number",              // 最大重试次数
    "interval": "number"                 // 重试间隔（秒）
  },
  "waitCondition": {                     // 等待条件
    "type": "string",                    // 等待类型：visible/enabled/clickable等
    "timeout": "number"                  // 等待超时时间
  }
}
```

**示例：**
```json
{
  "stepId": "APP-STEP-001",
  "stepName": "点击登录按钮",
  "action": "tap",
  "locator": {
    "type": "accessibility_id",
    "value": "login_button"
  },
  "value": null,
  "coordinates": {
    "x": 200,
    "y": 400
  },
  "timeout": 5,
  "screenshot": true,
  "description": "点击登录按钮提交登录信息"
}
```

### 7. 断言数据对象

#### 7.1 断言对象 (Assertion)

测试断言的配置信息，用于验证测试结果。

```json
{
  "assertionId": "string",               // 断言唯一标识符
  "type": "string",                      // 断言类型：equal/contains/notEmpty等
  "actual": "string",                    // 实际值表达式
  "expected": "any",                     // 期望值
  "description": "string",               // 断言描述
  "enabled": "boolean",                  // 是否启用
  "continueOnFailure": "boolean",        // 失败时是否继续执行
  "operator": "string",                  // 断言操作符：eq/ne/gt/lt/contains等
  "message": "string",                   // 断言失败消息
  "path": "string",                      // JSON路径或XPath
  "ignoreCase": "boolean",               // 是否忽略大小写
  "regex": "boolean",                    // 是否使用正则表达式
  "tolerance": "number",                 // 数值比较容差
  "customFunction": "string",            // 自定义断言函数
  "severity": "string",                  // 断言严重级别：critical/major/minor
  "tags": [],                            // 断言标签
  "metadata": {                          // 断言元数据
    "category": "string",                // 断言分类
    "reference": "string"                // 参考文档
  }
}
```

**示例：**
```json
{
  "assertionId": "ASSERT-001",
  "type": "equalsNumber",
  "actual": "${response.status_code}",
  "expected": 200,
  "description": "验证HTTP响应状态码为200",
  "enabled": true,
  "continueOnFailure": false
}
```

### 8. 数据提取器对象

#### 8.1 数据提取器对象 (Extractor)

用于从响应中提取数据并保存到变量中。

```json
{
  "extractorId": "string",               // 提取器唯一标识符
  "name": "string",                      // 变量名称
  "type": "string",                      // 提取类型：jsonpath/regex/xpath等
  "expression": "string",                // 提取表达式
  "defaultValue": "string",              // 默认值
  "description": "string",               // 提取器描述
  "scope": "string",                     // 作用域：global/local/session
  "index": "number",                     // 提取索引（当有多个匹配时）
  "transform": {                          // 数据转换配置
    "enabled": "boolean",                // 是否启用转换
    "function": "string",                // 转换函数
    "parameters": {}                     // 转换参数
  },
  "validation": {                         // 提取验证配置
    "enabled": "boolean",                // 是否启用验证
    "required": "boolean",               // 是否必需
    "pattern": "string",                 // 验证模式
    "minLength": "number",               // 最小长度
    "maxLength": "number"                // 最大长度
  },
  "cache": {                              // 缓存配置
    "enabled": "boolean",                // 是否启用缓存
    "ttl": "number",                     // 缓存生存时间（秒）
    "key": "string"                      // 缓存键
  },
  "metadata": {                           // 提取器元数据
    "category": "string",                // 分类
    "tags": []                           // 标签
  }
}
```

**示例：**
```json
{
  "extractorId": "EXT-TOKEN-001",
  "name": "access_token",
  "type": "jsonpath",
  "expression": "$.data.accessToken",
  "defaultValue": "",
  "description": "从登录响应中提取访问令牌"
}
```

### 9. 控制器数据对象

#### 9.1 循环控制器对象 (LoopController)

用于控制测试用例或步骤的循环执行。

```json
{
  "enabled": "boolean",                  // 是否启用循环
  "loopType": "string",                  // 循环类型：count/condition/data
  "loopCount": "number",                 // 循环次数
  "condition": "string",                 // 循环条件表达式
  "dataSource": {                        // 数据源配置
    "type": "string",                    // 数据源类型：csv/json/database/api
    "source": "string",                  // 数据源路径或连接字符串
    "query": "string",                   // 查询语句（数据库类型时使用）
    "columns": [],                       // 数据列名
    "parameters": {},                    // 查询参数
    "cache": {                           // 缓存配置
      "enabled": "boolean",              // 是否启用缓存
      "ttl": "number"                    // 缓存生存时间（秒）
    },
    "transform": {                       // 数据转换配置
      "enabled": "boolean",              // 是否启用转换
      "script": "string"                 // 转换脚本
    }
  },
  "breakOnError": "boolean",             // 出错时是否中断循环
  "maxIterations": "number",             // 最大迭代次数限制
  "interval": "number",                  // 循环间隔时间（秒）
  "variables": {                          // 循环变量配置
    "iterator": "string",                // 迭代器变量名
    "index": "string",                   // 索引变量名
    "current": "string"                  // 当前值变量名
  },
  "validation": {                         // 循环验证配置
    "enabled": "boolean",                // 是否启用验证
    "rules": [],                         // 验证规则列表
    "stopOnValidationFailure": "boolean" // 验证失败时是否停止
  },
  "reporting": {                          // 循环报告配置
    "enabled": "boolean",                // 是否启用循环报告
    "logEachIteration": "boolean",       // 是否记录每次迭代
    "summaryOnly": "boolean"             // 是否只显示摘要
  },
  "metadata": {                           // 循环控制器元数据
    "description": "string",             // 详细描述
    "category": "string",               // 分类
    "version": "string",                // 版本
    "tags": []                           // 标签列表
  }
}
```

**示例：**
```json
{
  "enabled": true,
  "loopType": "count",
  "loopCount": 3,
  "condition": null,
  "dataSource": null,
  "breakOnError": true
}
```

#### 9.2 条件控制器对象 (ConditionalController)

用于控制测试用例或步骤的条件执行。

```json
{
  "enabled": "boolean",                  // 是否启用条件控制
  "condition": "string",                 // 条件表达式
  "executeWhenTrue": "boolean",          // 条件为真时是否执行
  "description": "string",               // 条件描述
  "operator": "string",                  // 条件操作符：and/or/not
  "conditions": [],                       // 多条件组合列表
  "variables": {                          // 条件变量配置
    "context": {},                        // 上下文变量
    "runtime": {},                        // 运行时变量
    "external": {}                        // 外部变量
  },
  "evaluation": {                         // 条件评估配置
    "mode": "string",                     // 评估模式：strict/loose
    "timeout": "number",                 // 评估超时时间（秒）
    "retryOnError": "boolean",           // 错误时是否重试
    "maxRetries": "number"               // 最大重试次数
  },
  "actions": {                            // 条件动作配置
    "onTrue": {                           // 条件为真时的动作
      "execute": "boolean",               // 是否执行
      "script": "string",                // 执行脚本
      "variables": {}                     // 设置变量
    },
    "onFalse": {                          // 条件为假时的动作
      "execute": "boolean",               // 是否执行
      "script": "string",                // 执行脚本
      "variables": {}                     // 设置变量
    },
    "onError": {                          // 条件错误时的动作
      "execute": "boolean",               // 是否执行
      "script": "string",                // 执行脚本
      "fallback": "boolean"               // 是否使用回退值
    }
  },
  "logging": {                            // 条件日志配置
    "enabled": "boolean",                // 是否启用日志
    "level": "string",                   // 日志级别：debug/info/warn/error
    "logCondition": "boolean",           // 是否记录条件表达式
    "logResult": "boolean"               // 是否记录评估结果
  },
  "metadata": {                           // 条件控制器元数据
    "description": "string",             // 详细描述
    "category": "string",               // 分类
    "version": "string",                // 版本
    "dependencies": [],                  // 依赖关系
    "tags": []                           // 标签列表
  }
}
```

**示例：**
```json
{
  "enabled": true,
  "condition": "${response.json.code} == '0'",
  "executeWhenTrue": true,
  "description": "仅在登录成功时执行后续步骤"
}
```

### 10. 函数库数据对象

#### 10.1 自定义函数对象 (CustomFunction)

用户自定义的函数配置，支持在测试过程中调用。根据源码中的实际结构定义。

```json
{
  "name": "string",                      // 函数名称
  "code": "string",                      // Python代码字符串
  "params": {                            // 参数配置对象
    "names": [],                         // 参数名称列表，类型为string数组
    "types": []                          // 参数类型列表，类型为string数组
  },
  "description": "string",               // 函数描述
  "category": "string",                  // 函数分类：utility/validation/transformation等
  "version": "string",                   // 函数版本
  "dependencies": [],                    // 依赖的其他函数或库
  "examples": [                          // 使用示例
    {
      "input": {},                       // 输入示例
      "output": "any",                   // 输出示例
      "description": "string"            // 示例描述
    }
  ],
  "performance": {                       // 性能配置
    "timeout": "number",                // 执行超时时间（毫秒）
    "maxMemory": "number",              // 最大内存使用（MB）
    "cache": {                          // 缓存配置
      "enabled": "boolean",             // 是否启用缓存
      "ttl": "number",                  // 缓存生存时间（秒）
      "maxSize": "number"               // 最大缓存大小
    }
  },
  "security": {                          // 安全配置
    "sandbox": "boolean",               // 是否在沙箱中执行
    "allowedModules": [],               // 允许导入的模块
    "restrictedOperations": []          // 限制的操作
  },
  "metadata": {                          // 函数元数据
    "author": "string",                 // 作者
    "created": "string",                // 创建时间
    "modified": "string",               // 修改时间
    "tags": [],                         // 标签
    "documentation": "string"           // 详细文档链接
  }
}
```

**支持的参数类型：**
- `"Int"`: 整数类型
- `"Float"`: 浮点数类型  
- `"Boolean"`: 布尔类型
- `"Bytes"`: 字节类型
- `"JSONObject"`: 字典类型
- `"JSONArray"`: 列表类型
- `"Other"`: 无类型限制
- 其他值: 字符串类型（默认）

**示例：**
```json
{
  "name": "generate_test_data",
  "code": "import random\nusername = f'test_user_{random.randint(1000, 9999)}'\nemail = f'test_{random.randint(100, 999)}@example.com'\nresult = {'username': username, 'email': email}\nsys_return(result)",
  "params": {
    "names": [],
    "types": []
  }
}
```

**带参数的函数示例：**
```json
{
  "name": "calculate_age",
  "code": "from datetime import datetime\ncurrent_year = datetime.now().year\nage = current_year - birth_year\nsys_return(age)",
  "params": {
    "names": ["birth_year"],
    "types": ["Int"]
  }
}
```

**内置函数说明：**
在自定义函数代码中可以使用以下内置函数：
- `sys_return(value)`: 设置函数返回值
- `sys_get(name)`: 获取公共参数或关联变量
- `sys_put(name, value, ps=False)`: 设置公共参数或关联变量
- `print(...)`: 输出信息到测试缓冲区
```

### 11. 结果数据对象

#### 11.1 测试结果对象 (TestResult)

测试执行结果的完整信息。

```json
{
  "resultId": "string",                  // 结果唯一标识符
  "taskId": "string",                    // 关联的任务ID
  "caseId": "string",                    // 关联的用例ID
  "caseName": "string",                  // 用例名称
  "status": "string",                    // 执行状态：PASS/FAIL/ERROR/SKIP
  "startTime": "string",                 // 开始时间
  "endTime": "string",                   // 结束时间
  "duration": "number",                  // 执行时长（毫秒）
  "errorMessage": "string",              // 错误信息
  "stackTrace": "string",                // 堆栈跟踪
  "screenshots": [                       // 截图列表
    {
      "stepName": "string",              // 步骤名称
      "timestamp": "string",             // 截图时间戳
      "filePath": "string",              // 文件路径
      "size": "number",                  // 文件大小（字节）
      "format": "string",                // 图片格式：png/jpg
      "description": "string"            // 截图描述
    }
  ],
  "logs": [                              // 日志列表
    {
      "level": "string",                 // 日志级别：DEBUG/INFO/WARN/ERROR
      "timestamp": "string",             // 时间戳
      "message": "string",               // 日志消息
      "source": "string",                // 日志来源
      "category": "string",              // 日志分类
      "details": {}                      // 详细信息
    }
  ],
  "assertionResults": [                  // 断言结果列表
    {
      "assertionId": "string",           // 断言ID
      "status": "string",                // 断言状态：PASS/FAIL
      "actual": "any",                   // 实际值
      "expected": "any",                 // 期望值
      "message": "string",               // 断言消息
      "operator": "string",              // 断言操作符
      "path": "string",                  // 断言路径
      "duration": "number"               // 断言执行时间（毫秒）
    }
  ],
  "extractedData": {                     // 提取的数据
    "variables": {},                     // 提取的变量
    "tokens": {},                        // 提取的令牌
    "cookies": {},                       // 提取的Cookie
    "headers": {}                        // 提取的请求头
  },
  "performance": {                       // 性能指标
    "responseTime": "number",            // 响应时间（毫秒）
    "throughput": "number",              // 吞吐量（请求/秒）
    "memoryUsage": "number",             // 内存使用（MB）
    "cpuUsage": "number",                // CPU使用率（%）
    "networkLatency": "number"           // 网络延迟（毫秒）
  },
  "environment": {                       // 环境信息
    "os": "string",                     // 操作系统
    "browser": "string",                // 浏览器版本
    "device": "string",                 // 设备信息
    "network": "string",                // 网络环境
    "location": "string"                // 执行位置
  },
  "metadata": {                          // 结果元数据
    "testSuite": "string",              // 测试套件名称
    "version": "string",                // 测试版本
    "build": "string",                  // 构建版本
    "branch": "string",                 // 代码分支
    "tags": [],                         // 标签列表
    "category": "string",               // 分类
    "priority": "string"                // 优先级
  },
  "attachments": [                       // 附件列表
    {
      "type": "string",                  // 附件类型：video/report/data
      "name": "string",                  // 附件名称
      "path": "string",                  // 附件路径
      "size": "number",                  // 附件大小（字节）
      "mimeType": "string",              // MIME类型
      "description": "string"            // 附件描述
    }
  ],
  "retryInfo": {                         // 重试信息
    "retryCount": "number",              // 重试次数
    "maxRetries": "number",             // 最大重试次数
    "retryReason": "string",            // 重试原因
    "retryHistory": []                   // 重试历史
  }
}
```

**示例：**
```json
{
  "resultId": "RESULT-20241201-001",
  "taskId": "TASK-20241201-001",
  "caseId": "TC-LOGIN-001",
  "caseName": "正常用户登录测试",
  "status": "PASS",
  "startTime": "2024-12-01T10:30:00.000Z",
  "endTime": "2024-12-01T10:30:05.234Z",
  "duration": 5234,
  "errorMessage": null,
  "stackTrace": null,
  "screenshots": [
    {
      "stepName": "登录页面",
      "timestamp": "2024-12-01T10:30:02.000Z",
      "filePath": "/screenshots/login_page_20241201103002.png"
    }
  ],
  "logs": [
    {
      "level": "INFO",
      "timestamp": "2024-12-01T10:30:01.000Z",
      "message": "开始执行登录测试"
    },
    {
      "level": "INFO",
      "timestamp": "2024-12-01T10:30:05.000Z",
      "message": "登录测试执行完成"
    }
  ],
  "assertionResults": [
    {
      "assertionId": "ASSERT-001",
      "status": "PASS",
      "actual": "200",
      "expected": "200",
      "message": "HTTP状态码验证通过"
    }
  ],
  "extractedData": {
    "login_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_id": "12345"
  }
}
```

### 12. 模板引擎数据对象

#### 12.1 模板变量对象 (TemplateVariable)

模板引擎中使用的变量配置。

```json
{
  "variableName": "string",              // 变量名称
  "variableType": "string",              // 变量类型：string/number/boolean/object
  "value": "any",                       // 变量值
  "scope": "string",                     // 作用域：global/collection/case
  "description": "string",               // 变量描述
  "source": "string",                    // 变量来源：manual/environment/function/extractor
  "readonly": "boolean",                 // 是否只读
  "encrypted": "boolean",                // 是否加密存储
  "validation": {                        // 变量验证配置
    "required": "boolean",               // 是否必需
    "pattern": "string",                 // 验证正则表达式
    "minLength": "number",               // 最小长度
    "maxLength": "number",               // 最大长度
    "minValue": "number",                // 最小值
    "maxValue": "number",                // 最大值
    "allowedValues": []                  // 允许的值列表
  },
  "transformation": {                    // 变量转换配置
    "enabled": "boolean",                // 是否启用转换
    "function": "string",                // 转换函数
    "parameters": {}                     // 转换参数
  },
  "lifecycle": {                         // 变量生命周期
    "created": "string",                 // 创建时间
    "modified": "string",                // 修改时间
    "expires": "string",                 // 过期时间
    "autoCleanup": "boolean"             // 是否自动清理
  },
  "metadata": {                          // 变量元数据
    "category": "string",                // 变量分类
    "tags": [],                          // 标签列表
    "version": "string",                 // 版本
    "author": "string"                   // 创建者
  }
}
```

**示例：**
```json
{
  "variableName": "base_url",
  "variableType": "string",
  "value": "https://api.test.com",
  "scope": "global",
  "description": "测试环境基础URL"
}
```

### 13. 通信数据对象

#### 13.1 WebSocket消息对象 (WebSocketMessage)

WebSocket通信中的消息格式。

```json
{
  "messageId": "string",                 // 消息唯一标识符
  "messageType": "string",               // 消息类型：heartbeat/task/result/error
  "timestamp": "string",                 // 时间戳
  "source": "string",                    // 消息来源：engine/platform
  "target": "string",                    // 消息目标
  "data": {                              // 消息数据
    "action": "string",                  // 操作类型
    "payload": {},                       // 负载数据
    "metadata": {},                      // 元数据
    "context": {}                        // 上下文信息
  },
  "priority": "string",                  // 消息优先级：high/medium/low
  "ttl": "number",                       // 消息生存时间（秒）
  "retry": {                             // 重试配置
    "enabled": "boolean",                // 是否启用重试
    "maxRetries": "number",              // 最大重试次数
    "interval": "number"                 // 重试间隔（秒）
  },
  "security": {                          // 安全配置
    "encrypted": "boolean",              // 是否加密
    "signature": "string",               // 消息签名
    "checksum": "string"                 // 校验和
  },
  "routing": {                           // 路由配置
    "broadcast": "boolean",              // 是否广播
    "targets": [],                       // 目标列表
    "filters": {}                        // 路由过滤器
  },
  "tracking": {                          // 跟踪信息
    "correlationId": "string",           // 关联ID
    "sessionId": "string",               // 会话ID
    "requestId": "string",               // 请求ID
    "parentMessageId": "string"          // 父消息ID
  },
  "status": {                            // 消息状态
    "sent": "boolean",                   // 是否已发送
    "delivered": "boolean",              // 是否已送达
    "acknowledged": "boolean",           // 是否已确认
    "processed": "boolean"               // 是否已处理
  }
}
```

**示例：**
```json
{
  "messageId": "MSG-20241201-001",
  "messageType": "task",
  "timestamp": "2024-12-01T10:00:00.000Z",
  "source": "platform",
  "target": "engine",
  "data": {
    "action": "start_task",
    "taskId": "TASK-20241201-001",
    "priority": "high"
  }
}
```

## 数据对象关系图

```
Task (任务)
├── TestCollection (测试集合)
│   ├── TestCase (测试用例)
│   │   ├── ApiTestCase (API测试用例)
│   │   │   └── ApiRequest (API请求)
│   │   │       ├── RequestBody (请求体)
│   │   │       ├── Assertion (断言)
│   │   │       └── Extractor (数据提取器)
│   │   ├── WebTestCase (Web测试用例)
│   │   │   └── WebStep (Web步骤)
│   │   │       └── Locator (定位器)
│   │   └── AppTestCase (App测试用例)
│   │       └── AppStep (App步骤)
│   ├── LoopController (循环控制器)
│   ├── ConditionalController (条件控制器)
│   └── CustomFunction (自定义函数)
├── EngineConfig (引擎配置)
├── TemplateVariable (模板变量)
├── TestResult (测试结果)
└── WebSocketMessage (WebSocket消息)
```

## 总结

本文档详细描述了LiuMa-engine自动化测试引擎中所有核心数据对象的JSON设计规范和示例。这些数据对象构成了整个测试引擎的数据基础，支持API、Web、App三种类型的自动化测试。

### 关键特性

1. **分层设计**：从基础配置到具体测试用例，采用分层的数据结构设计
2. **类型安全**：明确定义每个字段的数据类型和约束条件
3. **扩展性**：支持自定义函数、变量和断言，具有良好的扩展性
4. **模板支持**：内置模板引擎，支持变量插值和函数调用
5. **多端支持**：统一的数据结构支持API、Web、App多种测试类型

### 使用建议

1. 严格按照JSON Schema定义创建测试数据
2. 合理使用变量和函数提高测试数据的复用性
3. 充分利用断言和数据提取器确保测试的准确性
4. 根据实际需求配置循环和条件控制器
5. 定期维护和更新测试数据以保持测试的有效性

本文档将随着项目的发展持续更新，确保与源码保持一致。