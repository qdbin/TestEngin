# JSON 数据设计及示例

## 文档概述

本文档基于 LiuMa-engine 自动化测试引擎的源码分析，详细说明项目中所有核心数据对象的 JSON 设计规范和示例。文档按照由浅入深的方式，覆盖项目运作所依赖的所有数据设计对象，确保与源码字段原意和设计思想完全一致。

## 数据对象分层设计

### 0. 基础配置数据对象

引擎的基础配置信息，用于初始化测试引擎的运行环境和连接参数。

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

### 1. task_plan

```json
{
	"collection_id_01": [
		{
			"session": session,
			"context": context,
			"task_id": self.task["taskId"],
			"test_type": case["caseType"],
			"test_class": "class_" + collection,  # 测试类名
			"test_case": "case_%s_%s" % (case["caseId"], case["index"]),  # 测试用例名
			"test_data": os.path.join(self.data_path, self.task["taskId"], collection, case["caseId"] + ".json")
		},
		{},
		{}
	],
	"collection_id_02": [
		{},{},{}
	]

}
```

### 2. task 响应对象

```json
{
  "taskId": "TASK-20241201-001",
  "taskType": "tmp/case/collection/plan",
  "downloadUrl": "/openapi/task/file/download/task_id",
  "maxThread":"3",
  "reRun":"true",
  "testCollectionList": [
    {
      "collectionId": "COL-USER-001",
      "collectionName": "用户登录测试集",
      "testCaseList": [
    		{"index":"1","caseId":"12-22"，"caseType":"api"},
		{"index":"2","caseId":"12-22"，"caseType":"api"}
		]
    }
  ]
  "DebugData":{}
}
```

### 3. case 响应对象（DebugData）

```json
{
  // caseInfo
  "comment": null,
  "caseId": "7e471c1f-b541-4ae6-91b2-d73964bc2b42",
  "caseName": "login_反例",

  // 自定义函数
  "functions": [
    {
      "code": "import xxx\n\ndef xxx:\n    xxxx",
      "name": "01_func_test",
      "params": {
        "types": ["String", "Boolean"],
        "names": ["params1", "params2"]
      }
    }
  ],

  // 公参
  "params": {
    "count": {
      "type": "Int",
      "value": "122"
    },
    "var": {}
  },

  // apiList
  "apiList": [
    {
      "apiId": "ff506192-3c44-4020-92b9-712a6d40c8a5",
      "apiName": "登录",
      "apiDesc": "描述内容内容",
      "url": "http://127.0.0.1:8080",
      "path": "/autotest/login",
      "method": "POST",
      "protocol": "HTTP",

      // 请求头
      "headers": {
        "content-type": "application/json",
        "token": "toekn"
      },

      // 代理
      "proxies": {
        "password": "123456",
        "url": "192.0.0.1:8080",
        "username": "root"
      },

      // 请求体
      "body": {
        "file": [],
        "form": [],
        "raw": "",
        "json": "{\"account\":\"test-05\",\"password\":\"MTIzNDU2\"}",
        "type": "json"
      },

      // 查询参数
      "query": {
        "query_param_02": "02",
        "query_param_01": "01"
      },

      // 路径参数
      "rest": {
        "query_param_01": "10",
        "path_param_01": "10"
      },

      // 断言
      "assertions": [
        {
          "expect": "0",
          "expression": "$.status",
          "method": "jsonpath",
          "from": "resCode",
          "assertion": "isGreaterThanOrEqualTo"
        },
        {
          "expect": "",
          "expression": "$.data",
          "method": "jsonpath",
          "from": "resBody",
          "assertion": "isTrue"
        }
      ],

      // 关联
      "relations": [
        {
          "expression": "$.token",
          "method": "jsonpath",
          "name": "token",
          "from": "resBody"
        }
      ],

      // 控制
      "controller": {
        // 常规
        "useSession": "true",
        "saveSession": "true",
        "sleepBeforeRun": "1",
        "sleepAfterRun": "1",
        "requireVerify": "true",
        "requireStream": "true",
        "loopExec": "{\"type\":\"FOR\",\"target\":\"\",\"assertion\":\"equals\",\"expect\":\"\",\"timeout\":0,\"indexName\":\"index-01\",\"times\":\"2\",\"num\":3}",
        "timeout": "30",
        "errorContinue": "true",

        // 前置
        "pre": [
          {
            "edit": false,
            "name": "preScript",
            "index": 1,
            "value": "import xxx\n\ndef func():\n    xxx\n    \nif 1==1:\n    print(\"xxx\")",
            "desc": "pre-01"
          },
          {
            "edit": false,
            "name": "preSql",
            "index": 2,
            "value": "{\"sqlType\":\"query\",\"sqlText\":\"select * from t\",\"names\":\"var1,var2\",\"db\":{\"password\":\"123456\",\"port\":\"3306\",\"host\":\"127.0.0.1\",\"user\":\"root\",\"db\":\"mysql\",\"tpz\":\"mysql\"}}",
            "desc": "pre-03"
          }
        ],

        // 后置
        "post": [
          {
            "edit": false,
            "name": "postScript",
            "index": 1,
            "value": "import xxx\n\ndef func():\n    xxx\n    \nif 1==1:\n    print(\"xxx\")",
            "desc": "post-01"
          }
        ]
      }
    }
  ]
}
```
