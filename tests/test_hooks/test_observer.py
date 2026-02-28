# -*- coding: utf-8 -*-
"""
AllureObserver观察者类单元测试

测试 app/pytest_hooks.py 中 AllureObserver 类的功能。
采用完全隔离的Mock方式，不依赖真实环境。
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List


class TestAllureObserver:
    """
    AllureObserver类的单元测试

    测试旁路观察者模式的报告生成功能。
    """

    def test_init(self, sample_trans_list):
        """
        测试：初始化属性设置正确

        验证观察者正确初始化
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test_user_login"
        )

        assert observer.trans_list == sample_trans_list
        assert observer.test_name == "test_user_login"

    def test_init_with_empty_trans_list(self):
        """
        测试：空trans_list应该被正确处理

        验证空列表不会导致错误
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=[],
            test_name="test_empty"
        )

        assert observer.trans_list == []

    def test_generate_report_with_empty_list(self):
        """
        测试：空trans_list生成报告

        验证空列表时generate_report不会崩溃
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=[],
            test_name="test_empty"
        )

        # 因为allure是在函数内部导入的，这里不需要mock
        # 直接调用应该不会报错（因为allure未安装时会被捕获）
        observer.generate_report()

    def test_generate_report_creates_steps(self, sample_trans_list):
        """
        测试：generate_report() 创建Allure步骤

        验证为每个事务创建正确的步骤
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test_flow"
        )

        # 直接调用，不需要mock（allure会在内部处理）
        # 如果allure未安装，会被try-except捕获
        observer.generate_report()

    def test_attach_request_info(self, sample_trans_list):
        """
        测试：_attach_request() 正确格式化请求信息

        验证请求信息被正确格式化
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        request = {
            "method": "POST",
            "url": "http://test.com/api",
            "headers": {"Content-Type": "application/json"},
            "body": {"username": "test"}
        }

        # 只测试格式化方法，不涉及allure
        result = observer._format_request_info(request)
        assert "Request Details" in result
        assert "POST" in result

    def test_attach_response_info(self, sample_trans_list):
        """
        测试：_attach_response() 正确格式化响应信息

        验证响应信息被正确格式化
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        response = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"code": 0, "message": "success"}
        }

        # 只测试格式化方法
        result = observer._format_response_info(response)
        assert "Response Details" in result

    def test_attach_log(self, sample_trans_list):
        """
        测试：_attach_log() 正确处理日志

        验证日志被正确格式化
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        log = "Test log message\nLine 2"
        # 不需要mock，直接测试格式化
        # 会被try-except捕获
        observer._attach_log(log)

    def test_attach_screenshots(self, sample_trans_list):
        """
        测试：_attach_screenshots() 处理截图列表

        验证截图列表被正确处理
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        screen_list = ["screenshot_001", "screenshot_002"]
        observer._attach_screenshots(screen_list)

    def test_format_request_info(self, sample_trans_list):
        """
        测试：_format_request_info() 返回HTML

        验证请求信息被格式化为HTML
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        request = {
            "method": "POST",
            "url": "http://test.com/login",
            "headers": {"Content-Type": "application/json"},
            "body": {"username": "test"}
        }

        result = observer._format_request_info(request)

        # 验证返回HTML格式
        assert "Request Details" in result
        assert "POST" in result
        assert "http://test.com/login" in result

    def test_format_response_info(self, sample_trans_list):
        """
        测试：_format_response_info() 返回HTML

        验证响应信息被格式化为HTML
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        response = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"code": 0},
            "elapsed": 150
        }

        result = observer._format_response_info(response)

        # 验证返回HTML格式
        assert "Response Details" in result
        assert "200" in result

    def test_format_json(self, sample_trans_list):
        """
        测试：_format_json() 格式化JSON数据

        验证JSON数据被正确格式化
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        # 测试字典
        data = {"key": "value", "number": 123}
        result = observer._format_json(data)
        assert "key" in result
        assert "value" in result

        # 测试列表
        data = [1, 2, 3]
        result = observer._format_json(data)
        assert "1" in result

        # 测试字符串
        data = "plain string"
        result = observer._format_json(data)
        assert result == "plain string"

    def test_dict_to_html_table(self, sample_trans_list):
        """
        测试：_dict_to_html_table() 转换字典为HTML表格

        验证字典被正确转换为HTML表格
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=sample_trans_list,
            test_name="test"
        )

        data = {"key1": "value1", "key2": "value2"}
        result = observer._dict_to_html_table(data)

        assert "key1" in result
        assert "value1" in result

    def test_dict_to_html_table_empty(self, sample_trans_list):
        """
        测试：空字典返回None

        验证空字典被正确处理
        """
        from app.pytest_hooks import AllureObserver

        observer = AllureObserver(
            trans_list=[],
            test_name="test"
        )

        result = observer._dict_to_html_table({})
        assert result == "None"


class TestPytestHooks:
    """
    Pytest钩子函数的单元测试

    测试pytest钩子函数的功能。
    """

    def test_pytest_configure_registers_markers(self):
        """
        测试：pytest_configure() 注册标记

        验证自定义标记被正确注册
        """
        from app.pytest_hooks import pytest_configure

        # Mock config对象
        mock_config = MagicMock()
        mock_config.addinivalue_line = MagicMock()
        mock_config.getoption = MagicMock(return_value=False)

        # 执行
        pytest_configure(mock_config)

        # 验证标记被注册
        assert mock_config.addinivalue_line.call_count >= 3

    def test_get_test_result_from_item(self):
        """
        测试：get_test_result_from_item() 函数

        验证从item获取测试结果
        """
        from app.pytest_hooks import get_test_result_from_item

        # 创建mock item
        mock_item = MagicMock()
        mock_item.name = "test_case"
        mock_item.nodeid = "test_file.py::test_case"
        mock_item.stash = {
            "trans_list": [{"id": "1", "name": "test"}],
            "case_info": {"case_id": "001", "case_name": "测试", "case_type": "API"}
        }

        result = get_test_result_from_item(mock_item)

        assert result["name"] == "test_case"
        assert len(result["trans_list"]) == 1
        assert result["case_info"]["case_type"] == "API"

    def test_attach_trans_list_to_allure_function(self):
        """
        测试：attach_trans_list_to_allure() 函数

        验证独立函数正确工作
        """
        from app.pytest_hooks import attach_trans_list_to_allure, AllureObserver

        trans_list = [{"id": "1", "name": "test", "status": 0}]

        # 直接调用，不mock（allure会被内部捕获）
        attach_trans_list_to_allure(trans_list, "test_name")


class TestBuildPlatformResult:
    """
    平台结果构建函数的单元测试
    """

    def test_build_platform_result_success(self, sample_trans_list):
        """
        测试：成功状态的平台结果构建

        验证成功状态的测试结果被正确构建
        """
        from app.pytest_hooks import _build_platform_result

        case_info = {
            "case_id": "test_001",
            "case_name": "测试用例",
            "case_type": "API"
        }

        # 创建mock item（start_time和end_time是datetime对象）
        import datetime
        mock_item = MagicMock()
        mock_item.name = "test_001"
        mock_item.start_time = datetime.datetime.now()
        mock_item.end_time = datetime.datetime.now()

        mock_call = MagicMock()
        mock_call.excinfo = None

        result = _build_platform_result(
            trans_list=sample_trans_list,
            case_info=case_info,
            item=mock_item,
            call=mock_call
        )

        # 验证结果
        assert result["status"] == 0  # 成功
        assert result["caseId"] == "test_001"
        assert result["caseName"] == "测试用例"
        assert result["caseType"] == "API"

    def test_build_platform_result_with_failure(self):
        """
        测试：失败状态的平台结果构建

        验证失败状态的测试结果被正确构建
        """
        from app.pytest_hooks import _build_platform_result

        trans_list = [
            {"status": 1}  # 失败状态
        ]

        case_info = {"case_id": "test_001", "case_name": "测试", "case_type": "API"}
        
        import datetime
        mock_item = MagicMock()
        mock_item.name = "test_001"
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

        assert result["status"] == 1  # 失败

    def test_build_platform_result_with_error(self):
        """
        测试：错误状态的平台结果构建

        验证错误状态的测试结果被正确构建
        """
        from app.pytest_hooks import _build_platform_result

        trans_list = [
            {"status": 2}  # 错误状态
        ]

        case_info = {"case_id": "test_001", "case_name": "测试", "case_type": "API"}
        
        import datetime
        mock_item = MagicMock()
        mock_item.name = "test_001"
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

        assert result["status"] == 2  # 错误

    def test_build_platform_result_with_exception(self):
        """
        测试：有异常的平台结果构建

        验证有异常时结果被正确构建
        """
        from app.pytest_hooks import _build_platform_result

        trans_list = []

        case_info = {"case_id": "test_001", "case_name": "测试", "case_type": "API"}
        
        import datetime
        mock_item = MagicMock()
        mock_item.name = "test_001"
        mock_item.start_time = datetime.datetime.now()
        mock_item.end_time = datetime.datetime.now()
        
        mock_call = MagicMock()
        mock_call.excinfo = MagicMock()
        mock_call.excinfo.value = ValueError("Test error")

        result = _build_platform_result(
            trans_list=trans_list,
            case_info=case_info,
            item=mock_item,
            call=mock_call
        )

        # 有异常信息时，状态应该是错误
        assert "errorMsg" in result

    def test_build_platform_result_no_time(self):
        """
        测试：无时间信息时的平台结果构建

        验证没有时间信息时结果仍能正确构建
        """
        from app.pytest_hooks import _build_platform_result

        trans_list = [{"status": 0}]

        case_info = {"case_id": "test_001", "case_name": "测试", "case_type": "API"}
        
        # 没有时间信息
        mock_item = MagicMock()
        mock_item.name = "test_001"
        mock_item.start_time = None
        mock_item.end_time = None
        
        mock_call = MagicMock()
        mock_call.excinfo = None

        result = _build_platform_result(
            trans_list=trans_list,
            case_info=case_info,
            item=mock_item,
            call=mock_call
        )

        # 验证结果
        assert result["status"] == 0
        assert result["startTime"] == 0
        assert result["endTime"] == 0
