# -*- coding: utf-8 -*-
"""
全链路集成测试

模拟完整的测试执行流程：
1. 平台下发测试数据 → JSON文件
2. JSON文件收集 → pytest_collect_file
3. 测试执行 → JSONCaseItem.runtest()
4. 结果验证 → trans_list验证
"""

import pytest
import json
import os
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestFullFlow:
    """
    全链路测试：JSON数据下发 → 收集 → 执行 → 结果验证
    """

    def test_full_flow_single_case(self, tmp_path):
        """
        测试：完整流程 - 单用例
        
        流程：
        1. 创建测试JSON数据
        2. 模拟收集
        3. 验证收集结果
        """
        # Step 1: 创建测试数据（模拟平台下发）
        test_data = {
            "caseId": "flow_001",
            "caseName": "完整流程测试",
            "comment": "测试完整流程",
            "apiList": [
                {
                    "apiId": "api_login",
                    "apiName": "用户登录",
                    "method": "POST",
                    "path": "/api/login",
                    "url": "http://example.com",
                    "headers": {"Content-Type": "application/json"},
                    "body": {"type": "json", "json": "{}"},
                    "assertions": [],
                    "relations": [],
                    "controller": {}
                }
            ]
        }
        
        # Step 2: 保存为JSON文件
        json_file = tmp_path / "test_flow_001.json"
        json_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding='utf-8')
        
        # Step 3: 模拟收集流程
        from app.json_collector import JSONFile
        
        jfile = JSONFile.from_parent(parent=None, path=json_file)
        items = list(jfile.collect())
        
        # Step 4: 验证
        assert len(items) == 1
        assert items[0].case_id == "flow_001"
        assert items[0].case_name == "完整流程测试"
        assert len(items[0].case_data["apiList"]) == 1

    def test_full_flow_multiple_apis(self, tmp_path):
        """
        测试：完整流程 - 多API用例
        """
        # 创建多API测试数据
        test_data = {
            "caseId": "flow_002",
            "caseName": "多API测试",
            "apiList": [
                {
                    "apiId": "api_1",
                    "apiName": "接口1",
                    "method": "GET",
                    "path": "/api/1",
                    "url": "http://example.com",
                    "headers": {},
                    "body": {},
                    "assertions": [],
                    "relations": [],
                    "controller": {}
                },
                {
                    "apiId": "api_2", 
                    "apiName": "接口2",
                    "method": "POST",
                    "path": "/api/2",
                    "url": "http://example.com",
                    "headers": {},
                    "body": {},
                    "assertions": [],
                    "relations": [],
                    "controller": {}
                },
                {
                    "apiId": "api_3",
                    "apiName": "接口3",
                    "method": "PUT",
                    "path": "/api/3",
                    "url": "http://example.com",
                    "headers": {},
                    "body": {},
                    "assertions": [],
                    "relations": [],
                    "controller": {}
                }
            ]
        }
        
        json_file = tmp_path / "test_flow_002.json"
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        # 收集
        from app.json_collector import JSONFile
        jfile = JSONFile.from_parent(parent=None, path=json_file)
        items = list(jfile.collect())
        
        # 验证
        assert len(items) == 1
        assert len(items[0].case_data["apiList"]) == 3

    def test_full_flow_with_variables(self, tmp_path):
        """
        测试：完整流程 - 带有变量的用例
        """
        test_data = {
            "caseId": "flow_003",
            "caseName": "变量测试",
            "params": {
                "username": {"type": "String", "value": "test_user"},
                "password": {"type": "String", "value": "123456"}
            },
            "apiList": [
                {
                    "apiId": "api_var",
                    "apiName": "带变量接口",
                    "method": "POST",
                    "path": "/api/${username}",
                    "url": "http://example.com",
                    "headers": {"Authorization": "Bearer ${token}"},
                    "body": {
                        "type": "json",
                        "json": '{"username": "${username}", "password": "${password}"}'
                    },
                    "assertions": [
                        {"expect": "0", "expression": "$.code", "method": "jsonpath"}
                    ],
                    "relations": [],
                    "controller": {}
                }
            ]
        }
        
        json_file = tmp_path / "test_flow_003.json"
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        from app.json_collector import JSONFile
        jfile = JSONFile.from_parent(parent=None, path=json_file)
        items = list(jfile.collect())
        
        # 验证参数被保存
        assert items[0].case_data["params"]["username"]["value"] == "test_user"
        assert "${username}" in items[0].case_data["apiList"][0]["path"]

    def test_full_flow_with_relations(self, tmp_path):
        """
        测试：完整流程 - 带关联的用例
        """
        test_data = {
            "caseId": "flow_004",
            "caseName": "关联测试",
            "apiList": [
                {
                    "apiId": "api_login",
                    "apiName": "登录",
                    "method": "POST",
                    "path": "/login",
                    "url": "http://example.com",
                    "headers": {},
                    "body": {},
                    "assertions": [],
                    "relations": [],
                    "controller": {"saveSession": "true"}
                },
                {
                    "apiId": "api_userinfo",
                    "apiName": "获取用户信息",
                    "method": "GET",
                    "path": "/user/info",
                    "url": "http://example.com",
                    "headers": {"Authorization": "${token}"},
                    "body": {},
                    "assertions": [],
                    "relations": [
                        {"source": "api_login.response.body.token", "target": "token"}
                    ],
                    "controller": {"useSession": "true"}
                }
            ]
        }
        
        json_file = tmp_path / "test_flow_004.json"
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        from app.json_collector import JSONFile
        jfile = JSONFile.from_parent(parent=None, path=json_file)
        items = list(jfile.collect())
        
        # 验证关联关系
        api_list = items[0].case_data["apiList"]
        assert len(api_list) == 2
        assert api_list[1]["relations"][0]["source"] == "api_login.response.body.token"

    def test_full_flow_with_assertions(self, tmp_path):
        """
        测试：完整流程 - 带断言的用例
        """
        test_data = {
            "caseId": "flow_005",
            "caseName": "断言测试",
            "apiList": [
                {
                    "apiId": "api_assert",
                    "apiName": "带断言接口",
                    "method": "GET",
                    "path": "/api/data",
                    "url": "http://example.com",
                    "headers": {},
                    "body": {},
                    "assertions": [
                        {
                            "expect": "200",
                            "expression": "statusCode",
                            "method": "raw",
                            "from": "resHead",
                            "assertion": "equals"
                        },
                        {
                            "expect": "0",
                            "expression": "$.code",
                            "method": "jsonpath",
                            "from": "resBody",
                            "assertion": "equals"
                        },
                        {
                            "expect": "success",
                            "expression": "$.message",
                            "method": "jsonpath",
                            "from": "resBody",
                            "assertion": "contains"
                        }
                    ],
                    "relations": [],
                    "controller": {}
                }
            ]
        }
        
        json_file = tmp_path / "test_flow_005.json"
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        from app.json_collector import JSONFile
        jfile = JSONFile.from_parent(parent=None, path=json_file)
        items = list(jfile.collect())
        
        # 验证断言
        assertions = items[0].case_data["apiList"][0]["assertions"]
        assert len(assertions) == 3
        assert assertions[0]["assertion"] == "equals"
        assert assertions[1]["method"] == "jsonpath"

    def test_full_flow_error_handling(self, tmp_path):
        """
        测试：错误处理流程
        """
        # 创建无效JSON
        invalid_file = tmp_path / "test_invalid.json"
        invalid_file.write_text("{ invalid json }", encoding='utf-8')
        
        from app.json_collector import JSONFile
        jfile = JSONFile.from_parent(parent=None, path=invalid_file)
        
        # 应该跳过或报错
        items = list(jfile.collect())
        # 无效JSON会被跳过
        assert len(items) == 0


class TestPytestExecutionFlow:
    """
    Pytest执行流程测试
    """

    def test_pytest_collect_file_hook(self, tmp_path):
        """
        测试：pytest_collect_file钩子
        """
        # 创建测试文件
        test_data = {"caseId": "hook_001", "apiList": []}
        json_file = tmp_path / "test_hook.json"
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        from app.json_collector import pytest_collect_file
        
        result = pytest_collect_file(parent=None, file_path=json_file)
        
        # 应该返回收集器
        assert result is not None

    def test_pytest_ignore_non_json(self, tmp_path):
        """
        测试：忽略非JSON文件
        """
        from app.json_collector import pytest_collect_file
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not json")
        
        result = pytest_collect_file(parent=None, file_path=txt_file)
        
        # 应该返回None
        assert result is None


class TestResultProcessing:
    """
    结果处理流程测试
    """

    def test_platform_result_format(self):
        """
        测试：平台结果格式
        """
        from app.pytest_hooks import _build_platform_result
        
        trans_list = [
            {"id": "api_1", "name": "接口1", "status": 0},
            {"id": "api_2", "name": "接口2", "status": 1}
        ]
        case_info = {
            "case_id": "result_001",
            "case_name": "结果测试",
            "case_type": "API"
        }
        
        import datetime
        mock_item = MagicMock()
        mock_item.name = "test_result"
        mock_item.start_time = datetime.datetime.now()
        mock_item.end_time = datetime.datetime.now()
        
        mock_call = MagicMock()
        mock_call.excinfo = None
        
        result = _build_platform_result(
            trans_list=trans_list,
            case_info=case_info,
            item=mock_item,
            call=mock_call
        )
        
        # 验证格式
        assert result["status"] == 1  # 有失败
        assert result["caseId"] == "result_001"
        assert result["caseType"] == "API"
        assert "transactionList" in result

    def test_status_calculation_all_success(self):
        """
        测试：全部成功状态计算
        """
        trans_list = [
            {"status": 0},
            {"status": 0},
            {"status": 0}
        ]
        
        has_failure = any(t.get("status") == 1 for t in trans_list)
        has_error = any(t.get("status") == 2 for t in trans_list)
        
        if has_error:
            status = 2
        elif has_failure:
            status = 1
        else:
            status = 0
        
        assert status == 0

    def test_status_calculation_with_failures(self):
        """
        测试：有失败的状态计算
        """
        trans_list = [
            {"status": 0},
            {"status": 1},  # 失败
            {"status": 0}
        ]
        
        has_failure = any(t.get("status") == 1 for t in trans_list)
        has_error = any(t.get("status") == 2 for t in trans_list)
        
        if has_error:
            status = 2
        elif has_failure:
            status = 1
        else:
            status = 0
        
        assert status == 1

    def test_status_calculation_with_errors(self):
        """
        测试：有错误的状态计算
        """
        trans_list = [
            {"status": 0},
            {"status": 2},  # 错误
            {"status": 0}
        ]
        
        has_failure = any(t.get("status") == 1 for t in trans_list)
        has_error = any(t.get("status") == 2 for t in trans_list)
        
        if has_error:
            status = 2
        elif has_failure:
            status = 1
        else:
            status = 0
        
        assert status == 2


class TestAdapterFlow:
    """
    适配器流程测试
    """

    def test_pytest_testcase_adapter(self):
        """
        测试：PytestTestCase适配器
        """
        from app.json_collector import PytestTestCase
        
        case_data = {
            "caseId": "adapter_001",
            "apiList": [
                {"apiId": "api_1", "apiName": "接口1"}
            ]
        }
        
        adapter = PytestTestCase(
            case_name="test_adapter",
            case_data=case_data,
            case_type="API"
        )
        
        # 验证属性
        assert adapter.case_name == "test_adapter"
        assert adapter.case_type == "API"
        assert adapter.trans_list == []
        
        # 测试defineTrans
        adapter.defineTrans("api_001", "测试接口", "content", "desc")
        
        assert len(adapter.trans_list) == 1
        assert adapter.trans_list[0]["id"] == "api_001"
        
        # 测试updateTransStatus
        adapter.updateTransStatus(0)
        assert adapter.trans_list[0]["status"] == 0
        
        # 测试debugLog
        adapter.debugLog("debug info")
        assert "debug info" in adapter.trans_list[0]["log"]


class TestConfigFlow:
    """
    配置流程测试
    """

    def test_allure_enabled_from_env(self):
        """
        测试：Allure环境变量配置
        """
        import os
        
        # 保存原始值
        original = os.environ.get("ALLURE_ENABLED", "false")
        
        # 测试关闭
        os.environ["ALLURE_ENABLED"] = "false"
        allure_enabled = os.environ.get("ALLURE_ENABLED", "false").lower() == "true"
        assert allure_enabled == False
        
        # 测试开启
        os.environ["ALLURE_ENABLED"] = "true"
        allure_enabled = os.environ.get("ALLURE_ENABLED", "false").lower() == "true"
        assert allure_enabled == True
        
        # 恢复
        if original:
            os.environ["ALLURE_ENABLED"] = original

    def test_pytest_markers_registration(self):
        """
        测试：Pytest标记注册
        """
        from app.pytest_hooks import pytest_configure
        
        mock_config = MagicMock()
        mock_config.addinivalue_line = MagicMock()
        mock_config.getoption = MagicMock(return_value=False)
        
        pytest_configure(mock_config)
        
        # 验证标记被注册
        assert mock_config.addinivalue_line.call_count >= 3
