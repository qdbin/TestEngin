# -*- coding: utf-8 -*-
"""
Pytest钩子函数与Allure报告生成器

本模块实现pytest钩子函数，采用旁路观察者模式生成测试报告。

核心功能：
    1. 平台推送（核心功能）：确保测试结果能正确回传给平台
    2. Allure报告（可选功能）：独立生成，仅供开发人员查看，不影响主流程

设计原则：
    - 平台推送是核心功能，必须保证正确性
    - Allure是旁路观察者，完全解耦，不影响测试执行
    - Allure可以独立开启/关闭，不影响平台推送

核心钩子函数：
    - pytest_configure: pytest初始化配置
    - pytest_runtest_makereport: 测试结果处理钩子
"""

import os
import pytest
from typing import Any, Dict, List


# 全局配置：通过环境变量或pytest参数传入
ALLURE_ENABLED = (
    os.environ.get("ALLURE_ENABLED", "false").lower() == "true"
)  # 默认关闭Allure
PYTEST_RESULT_QUEUE = None  # 用于平台推送的队列
PYTEST_DEFAULT_RESULT = None
PYTEST_DEFAULT_LOCK = None


def configure_runtime_result_channel(queue, default_result, default_lock):
    global PYTEST_RESULT_QUEUE, PYTEST_DEFAULT_RESULT, PYTEST_DEFAULT_LOCK
    PYTEST_RESULT_QUEUE = queue
    PYTEST_DEFAULT_RESULT = default_result
    PYTEST_DEFAULT_LOCK = default_lock


class AllureObserver:
    """
    Allure报告观察者类

    采用旁路观察者模式，负责将trans_list转换为Allure测试报告。
    该类是纯观察者，不参与测试执行，只负责报告生成。

    注意：这个类是完全可选的，默认不启用。
    开启方式：设置环境变量 ALLURE_ENABLED=true 或 --allure-enabled
    """

    def __init__(self, trans_list: List[Dict[str, Any]], test_name: str):
        """
        初始化Allure观察者

        Args:
            trans_list: 事务列表，包含每个API步骤的执行结果
            test_name: 测试名称
        """
        self.trans_list = trans_list or []
        self.test_name = test_name

    def generate_report(self):
        """
        生成Allure报告的核心方法

        遍历trans_list，把每个事务转换为Allure step。
        同时添加请求、响应、日志、截图等附件信息。
        """
        try:
            import allure
        except ImportError:
            # Allure未安装，跳过
            return

        if not self.trans_list:
            with allure.step(f"Test: {self.test_name}"):
                allure.dynamic.description("No transaction data available")
            return

        # 遍历事务列表，为每个事务创建Allure步骤
        for index, trans in enumerate(self.trans_list):
            step_name = trans.get("name", f"Step {index + 1}")

            with allure.step(f"Step {index + 1}: {step_name}"):
                if trans.get("description"):
                    allure.dynamic.description(trans["description"])

                if trans.get("request"):
                    self._attach_request(trans["request"])

                if trans.get("response"):
                    self._attach_response(trans["response"])

                if trans.get("log"):
                    self._attach_log(trans["log"])

                if trans.get("screenShotList"):
                    self._attach_screenshots(trans["screenShotList"])

    def _attach_request(self, request: Dict[str, Any]):
        """添加请求详情附件"""
        try:
            import allure

            request_info = self._format_request_info(request)
            allure.attach(
                request_info,
                name="Request",
                attachment_type=allure.attachment_type.HTML,
            )
        except ImportError:
            pass

    def _attach_response(self, response: Dict[str, Any]):
        """添加响应详情附件"""
        try:
            import allure

            response_info = self._format_response_info(response)
            allure.attach(
                response_info,
                name="Response",
                attachment_type=allure.attachment_type.HTML,
            )
        except ImportError:
            pass

    def _attach_log(self, log: str):
        """添加日志附件"""
        try:
            import allure

            log_html = log.replace("\n", "<br>").replace("\\n", "<br>")
            allure.attach(
                log_html,
                name="Execution Log",
                attachment_type=allure.attachment_type.HTML,
            )
        except ImportError:
            pass

    def _attach_screenshots(self, screen_list: List[str]):
        """添加截图附件"""
        try:
            import allure

            if screen_list:
                screen_info = "<br>".join([f"Screenshot: {s}" for s in screen_list])
                allure.attach(
                    screen_info,
                    name="Screenshots",
                    attachment_type=allure.attachment_type.TEXT,
                )
        except ImportError:
            pass

    def _format_request_info(self, request: Dict[str, Any]) -> str:
        """格式化请求信息为HTML"""
        method = request.get("method", "N/A")
        url = request.get("url", "N/A")
        headers = request.get("headers", {})
        body = request.get("body", "")

        headers_str = self._dict_to_html_table(headers)

        return f"""
        <h4>Request Details</h4>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 8px; border: 1px solid #ddd; text-align:left;">Field</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align:left;">Value</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Method</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{method}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>URL</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd; word-break: break-all;">{url}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Headers</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{headers_str}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Body</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;"><pre>{self._format_json(body)}</pre></td>
            </tr>
        </table>
        """

    def _format_response_info(self, response: Dict[str, Any]) -> str:
        """格式化响应信息为HTML"""
        status_code = response.get("status_code", "N/A")
        headers = response.get("headers", {})
        body = response.get("body", "")
        elapsed = response.get("elapsed", 0)

        if isinstance(status_code, int):
            if 200 <= status_code < 300:
                status_color = "green"
            elif 400 <= status_code < 500:
                status_color = "orange"
            else:
                status_color = "red"
        else:
            status_color = "black"

        headers_str = self._dict_to_html_table(headers)

        return f"""
        <h4>Response Details</h4>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 8px; border: 1px solid #ddd; text-align:left;">Field</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align:left;">Value</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status Code</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd; color: {status_color};"><strong>{status_code}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Response Time</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{elapsed} ms</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Headers</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{headers_str}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Body</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;"><pre>{self._format_json(body)}</pre></td>
            </tr>
        </table>
        """

    def _dict_to_html_table(self, data: Dict[str, Any]) -> str:
        """将字典转换为HTML表格"""
        if not data:
            return "None"

        rows = []
        for key, value in data.items():
            rows.append(
                f"<tr><td style='padding:4px;border:1px solid #ddd;'>{key}</td><td style='padding:4px;border:1px solid #ddd;'><pre>{value}</pre></td></tr>"
            )

        return f"<table style='width:100%;border-collapse:collapse;'>{''.join(rows)}</table>"

    def _format_json(self, data: Any) -> str:
        """格式化JSON数据"""
        import json

        if isinstance(data, (dict, list)):
            try:
                return json.dumps(data, indent=2, ensure_ascii=False)
            except:
                return str(data)
        return str(data)


def pytest_configure(config):
    """
    pytest配置钩子函数

    在pytest启动时调用，用于初始化配置和注册自定义标记。
    """
    global ALLURE_ENABLED, PYTEST_RESULT_QUEUE

    # 注册自定义标记
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "web: mark test as WEB test")
    config.addinivalue_line("markers", "app: mark test as APP test")

    # 从命令行参数获取配置
    ALLURE_ENABLED = config.getoption("--allure-enabled", default=ALLURE_ENABLED)

    option_queue = config.getoption("--result-queue", default=None)
    if option_queue is not None:
        PYTEST_RESULT_QUEUE = option_queue


def pytest_addoption(parser):
    """
    添加自定义命令行选项
    """
    parser.addoption(
        "--allure-enabled",
        action="store",
        default=False,
        help="Enable Allure report generation (default: disabled)",
    )
    parser.addoption(
        "--result-queue",
        action="store",
        default=None,
        help="Result queue for platform push",
    )


def pytest_runtest_makereport(item, call):
    """
    测试结果钩子函数 - 核心！

    这是实现测试结果处理的关键钩子：
        1. 收集测试结果数据（trans_list）
        2. 平台推送（核心功能）
        3. Allure报告（可选功能，默认关闭）

    采用旁路观察者模式，不影响测试执行流程。
    """
    # 只在测试执行阶段处理结果
    if call.when != "call":
        return

    # ===== 获取测试数据 =====
    trans_list = item.stash.get("trans_list", [])
    case_info = item.stash.get("case_info", {})

    if not trans_list and call.excinfo is None:
        return

    # ===== 核心功能：平台推送 =====
    # 构建平台结果格式（与result.py保持一致）
    platform_result = _build_platform_result(
        trans_list=trans_list, case_info=case_info, item=item, call=call
    )

    # 推送结果到平台
    _push_to_platform(platform_result)

    # ===== 可选功能：Allure报告（默认关闭）=====
    # 只有明确开启时才生成Allure报告
    if ALLURE_ENABLED:
        try:
            observer = AllureObserver(trans_list=trans_list, test_name=item.name)
            observer.generate_report()
        except Exception:
            # Allure报告生成失败不影响主流程
            pass


def _build_platform_result(
    trans_list: List[Dict[str, Any]], case_info: Dict[str, Any], item, call
) -> Dict[str, Any]:
    """
    构建平台结果数据

    将trans_list转换为平台要求的格式，与result.py保持一致。

    Args:
        trans_list: 事务列表
        case_info: 用例信息
        item: pytest测试项
        call: pytest调用阶段

    Returns:
        Dict: 平台结果数据
    """
    # 计算总体状态：0=成功, 1=失败, 2=错误, 3=跳过
    overall_status = 0
    has_failure = False
    has_error = False

    for trans in trans_list:
        status = trans.get("status", 0)
        if status == 1:
            has_failure = True
        elif status == 2:
            has_error = True

    if has_error:
        overall_status = 2
    elif has_failure:
        overall_status = 1
    else:
        overall_status = 0

    # 获取时间信息
    start_time = getattr(item, "start_time", None)
    end_time = getattr(item, "end_time", None)

    # 构建结果（与result.py的stopTest方法保持格式一致）
    result = {
        "status": overall_status,
        "caseId": case_info.get("case_id", ""),
        "caseName": case_info.get("case_name", item.name),
        "caseType": case_info.get("case_type", "API"),
        "caseDesc": case_info.get("case_desc", None),
        "collectionId": case_info.get("collection_id", ""),
        "index": int(case_info.get("index", 0)),
        "runTimes": int(case_info.get("run_times", 1)),
        "startTime": int(start_time.timestamp() * 1000) if start_time else 0,
        "endTime": int(end_time.timestamp() * 1000) if end_time else 0,
        "transactionList": trans_list,
    }

    # 如果有异常信息
    if call.excinfo is not None:
        result["errorMsg"] = str(call.excinfo.value)
        exc_type = getattr(call.excinfo, "type", None)
        if (
            overall_status == 0
            and isinstance(exc_type, type)
            and issubclass(exc_type, AssertionError)
        ):
            result["status"] = 1
        elif overall_status == 0:
            result["status"] = 2

    return result


def _push_to_platform(platform_result: Dict[str, Any]):
    """
    推送结果到平台

    通过全局队列将结果推送给平台的report进程。
    这个函数是平台推送的核心通道。

    Args:
        platform_result: 平台格式的测试结果
    """
    global PYTEST_RESULT_QUEUE, PYTEST_DEFAULT_RESULT, PYTEST_DEFAULT_LOCK

    if PYTEST_RESULT_QUEUE is not None:
        try:
            if PYTEST_DEFAULT_LOCK is not None and PYTEST_DEFAULT_LOCK.acquire():
                try:
                    if PYTEST_DEFAULT_RESULT is not None:
                        PYTEST_DEFAULT_RESULT.append(platform_result)
                    PYTEST_RESULT_QUEUE.put(platform_result)
                finally:
                    PYTEST_DEFAULT_LOCK.release()
            else:
                PYTEST_RESULT_QUEUE.put(platform_result)
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """
    pytest会话结束钩子

    在所有测试执行完成后调用。
    """
    pass


# ===== 辅助函数 =====


def get_test_result_from_item(item) -> Dict[str, Any]:
    """
    从pytest测试项获取测试结果
    """
    return {
        "trans_list": item.stash.get("trans_list", []),
        "case_info": item.stash.get("case_info", {}),
        "name": item.name,
        "nodeid": item.nodeid,
    }


def attach_trans_list_to_allure(trans_list: List[Dict[str, Any]], test_name: str):
    """
    将trans_list附加到Allure报告（独立函数）

    手动调用生成Allure报告的辅助函数。
    """
    observer = AllureObserver(trans_list=trans_list, test_name=test_name)
    observer.generate_report()
