# -*- coding: utf-8 -*-
"""
Pytest配置文件

提供共享的fixtures，用于单元测试。
所有测试数据手动构造，与真实业务完全解耦。
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List


@pytest.fixture
def sample_case_data():
    """
    Fixture: 示例用例数据

    手动构造的测试数据，与真实业务完全解耦。
    包含基本的API测试用例结构。

    Returns:
        Dict: 测试用例数据字典
    """
    return {
        "caseId": "test_case_001",
        "caseName": "测试用户登录接口",
        "comment": "这是一个测试用例",
        "params": {
            "username": "test_user",
            "password": "123456"
        },
        "functions": [],
        "apiList": [
            {
                "apiId": "api_001",
                "apiName": "用户登录",
                "apiDesc": "用户登录接口",
                "url": "http://api.example.com",
                "path": "/login",
                "method": "POST",
                "protocol": "HTTP",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "type": "json",
                    "json": '{"username": "${username}", "password": "${password}"}'
                },
                "query": {},
                "rest": {},
                "assertions": [
                    {
                        "expect": "0",
                        "expression": "$.code",
                        "method": "jsonpath",
                        "from": "resBody",
                        "assertion": "equals"
                    }
                ],
                "relations": [],
                "controller": {
                    "useSession": "true",
                    "saveSession": "true",
                    "timeout": "30",
                    "errorContinue": "true",
                    "pre": [],
                    "post": []
                }
            }
        ]
    }


@pytest.fixture
def sample_trans_list():
    """
    Fixture: 示例事务列表

    返回API执行过程中的事务列表数据。

    Returns:
        List[Dict]: 事务列表
    """
    return [
        {
            "id": "api_001",
            "name": "用户登录",
            "description": "调用登录接口",
            "request": {
                "method": "POST",
                "url": "http://api.example.com/login",
                "headers": {"Content-Type": "application/json"},
                "body": {"username": "test_user", "password": "123456"}
            },
            "response": {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"code": 0, "message": "success", "token": "abc123"}
            },
            "log": "请求发送成功<br>响应状态码: 200",
            "status": 0,
            "during": 150,
            "screenShotList": []
        },
        {
            "id": "api_002",
            "name": "获取用户信息",
            "description": "获取用户基本信息",
            "request": {
                "method": "GET",
                "url": "http://api.example.com/user/info",
                "headers": {"Authorization": "Bearer abc123"}
            },
            "response": {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"code": 0, "name": "测试用户", "email": "test@example.com"}
            },
            "log": "",
            "status": 0,
            "during": 80,
            "screenShotList": []
        }
    ]


@pytest.fixture
def sample_api_list():
    """
    Fixture: 示例API列表

    Returns:
        List[Dict]: API列表数据
    """
    return [
        {
            "apiId": "api_login",
            "apiName": "登录接口",
            "method": "POST",
            "path": "/api/login",
            "url": "http://test.com"
        },
        {
            "apiId": "api_userinfo",
            "apiName": "获取用户信息",
            "method": "GET",
            "path": "/api/user/info",
            "url": "http://test.com"
        }
    ]


@pytest.fixture
def temp_json_file(tmp_path):
    """
    Fixture: 创建临时JSON测试文件

    Args:
        tmp_path: pytest的tmp_path fixture

    Returns:
        Path: JSON文件路径
    """
    test_data = {
        "caseId": "test_001",
        "caseName": "测试用例",
        "apiList": [
            {
                "apiId": "api_001",
                "apiName": "测试接口",
                "method": "GET",
                "path": "/test"
            }
        ]
    }

    json_file = tmp_path / "test_case_001.json"
    json_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding='utf-8')

    return json_file


@pytest.fixture
def temp_invalid_json_file(tmp_path):
    """
    Fixture: 创建临时无效JSON文件

    Args:
        tmp_path: pytest的tmp_path fixture

    Returns:
        Path: 无效JSON文件路径
    """
    # 无效的JSON内容（缺少必要的字段）
    invalid_data = {
        "caseId": "test_002"
        # 缺少 apiList 字段
    }

    json_file = tmp_path / "test_invalid.json"
    json_file.write_text(json.dumps(invalid_data), encoding='utf-8')

    return json_file


@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Fixture: 创建临时测试目录

    包含多个JSON测试文件。

    Args:
        tmp_path: pytest的tmp_path fixture

    Returns:
        Path: 测试目录路径
    """
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()

    # 创建多个测试文件
    for i in range(3):
        case_data = {
            "caseId": f"test_case_{i:03d}",
            "caseName": f"测试用例{i}",
            "apiList": [
                {
                    "apiId": f"api_{i}",
                    "apiName": f"接口{i}",
                    "method": "GET",
                    "path": f"/api/{i}"
                }
            ]
        }
        json_file = test_dir / f"test_case_{i:03d}.json"
        json_file.write_text(json.dumps(case_data, ensure_ascii=False), encoding='utf-8')

    return test_dir


@pytest.fixture
def mock_api_response():
    """
    Fixture: 模拟API响应

    用于测试ApiTestCase的响应处理逻辑。

    Returns:
        Dict: 模拟的HTTP响应
    """
    class MockResponse:
        """模拟响应对象"""
        def __init__(self):
            self.status_code = 200
            self.headers = {"Content-Type": "application/json"}
            self.text = '{"code": 0, "message": "success"}'
            self.elapsed = type('obj', (object,), {'total_seconds': lambda: 0.5})()

        def json(self):
            return {"code": 0, "message": "success"}

    return MockResponse()


@pytest.fixture
def mock_case_context():
    """
    Fixture: 模拟用例上下文

    Returns:
        Dict: 模拟的用例上下文数据
    """
    return {
        "task_id": "task_001",
        "test_type": "API",
        "test_class": "class_test",
        "test_case": "case_001",
        "test_data": "path/to/test_data.json",
        "driver": None,
        "session": None,
        "context": {},
        "run_index": 1
    }
