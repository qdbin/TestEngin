# -*- coding: utf-8 -*-
"""
Pytest自定义JSON测试用例收集器

本模块实现pytest的文件收集钩子，使pytest能够识别并执行平台下发的JSON测试文件。
采用自定义Collector模式，将JSON测试数据转换为pytest可执行的测试用例。

核心类：
    - JSONFile: pytest文件收集器，处理JSON文件扫描和解析
    - JSONCaseItem: pytest测试用例项，代表单个测试用例
    - PytestTestCase: 适配器类，桥接pytest和现有ApiTestCase执行逻辑

设计原则：
    - 复用现有core/api/testcase.py的ApiTestCase执行逻辑
    - 保持测试执行逻辑不变
    - 通过item.stash传递trans_list供观察者（Allure）使用
"""

import datetime
import json
import os
import pytest
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from core.api.testcase import ApiTestCase
except ImportError:
    ApiTestCase = None


RUNTIME_CASE_META: Dict[str, Dict[str, Any]] = {}


def _normalize_path(path: Path) -> str:
    return os.path.abspath(str(path))


def configure_runtime_case_meta(case_meta: Dict[str, Dict[str, Any]]):
    global RUNTIME_CASE_META
    normalized_meta = {}
    for file_path, meta in (case_meta or {}).items():
        normalized_meta[_normalize_path(Path(file_path))] = meta or {}
    RUNTIME_CASE_META = normalized_meta


class JSONFile(pytest.File):
    """
    自定义JSON文件收集器

    负责将JSON测试文件转换为pytest可识别的测试用例。
    当pytest扫描目录时，pytest_collect_file钩子会调用此类来收集测试用例。
    """

    def __init__(self, path, parent=None, **kwargs):
        """
        初始化JSON文件收集器

        Args:
            fspath: JSON文件的路径对象（Path类型）
            parent: 父级pytest对象
        """
        super().__init__(path=path, parent=parent, **kwargs)
        self.test_data: Dict[str, Any] = {}

    @classmethod
    def from_parent(cls, parent, *, path):
        """
        创建JSONFile实例的工厂方法（pytest标准方式）

        Args:
            parent: 父级pytest对象
            path: 文件路径

        Returns:
            JSONFile: 实例对象
        """
        return super().from_parent(parent=parent, path=path)

    def collect(self):
        """
        收集测试用例的核心方法

        解析JSON文件，生成一个或多个测试用例项。

        Yields:
            JSONCaseItem: 测试用例项对象
        """
        try:
            # 读取并解析JSON文件
            with open(self.path, "r", encoding="utf-8") as f:
                self.test_data = json.load(f)
        except json.JSONDecodeError as e:
            # JSON解析错误，跳过该文件
            pytest.skip(f"Failed to parse JSON file {self.path}: {e}")
            return
        except Exception as e:
            pytest.skip(f"Failed to read JSON file {self.path}: {e}")
            return

        # 验证必要的字段存在
        if not self._validate_test_data():
            pytest.skip(f"Invalid test data format in {self.path}")
            return

        # 获取用例信息
        case_id = self.test_data.get("caseId", "unknown")
        case_name = self.test_data.get("caseName", f"TestCase_{case_id}")
        case_meta = RUNTIME_CASE_META.get(_normalize_path(self.path), {})
        item_name = f"test_{case_id}_{case_meta.get('index', 0)}"

        # 创建测试用例项 - 使用from_parent方法
        case_item = JSONCaseItem.from_parent(
            parent=self,
            name=item_name,
            case_data=self.test_data,
            case_type="API",
            case_id=case_id,
            case_name=case_name,
            case_meta=case_meta,
        )

        yield case_item

    def _validate_test_data(self) -> bool:
        """
        验证测试数据格式是否有效

        Returns:
            bool: 验证通过返回True，否则返回False
        """
        # 必须包含caseId
        if not self.test_data.get("caseId"):
            return False

        # 必须包含apiList（API测试的核心）
        if not self.test_data.get("apiList"):
            return False

        return True


class JSONCaseItem(pytest.Item):
    """
    自定义测试用例项

    代表一个具体的API测试用例。
    负责调用执行器执行测试，并保存执行结果（trans_list）供后续钩子使用。

    注意：此类不直接继承pytest.Function，而是作为独立类实现runtest方法。
    pytest会通过反射调用此方法。
    """

    def __init__(
        self,
        name: str,
        parent: JSONFile,
        case_data: Dict[str, Any],
        case_type: str = "API",
        case_id: str = "",
        case_name: str = "",
        case_meta: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        初始化测试用例项

        Args:
            name: 测试用例名称
            parent: 父级收集器对象
            case_data: 测试用例数据字典
            case_type: 测试类型
            case_id: 用例ID
            case_name: 用例名称
        """
        super().__init__(name=name, parent=parent, **kwargs)
        self.fspath = parent.path
        self.case_data = case_data
        self.case_type = case_type
        self.case_id = case_id
        self.case_name = case_name
        self.case_meta = case_meta or {}
        self.trans_list: List[Dict[str, Any]] = []
        self.test_case_name = case_name
        self.test_case_desc = self.case_data.get("comment", "")
        self.start_time = None
        self.end_time = None

    @classmethod
    def from_parent(
        cls,
        parent,
        *,
        name: str,
        case_data: Dict[str, Any],
        case_type: str = "API",
        case_id: str = "",
        case_name: str = "",
        case_meta: Optional[Dict[str, Any]] = None,
    ):
        """
        创建JSONCaseItem实例的工厂方法（pytest标准方式）

        Args:
            parent: 父级pytest对象
            name: 测试用例名称
            case_data: 测试用例数据
            case_type: 测试类型
            case_id: 用例ID
            case_name: 用例名称

        Returns:
            JSONCaseItem: 实例对象
        """
        return super().from_parent(
            parent=parent,
            name=name,
            case_data=case_data,
            case_type=case_type,
            case_id=case_id,
            case_name=case_name,
            case_meta=case_meta,
        )

    def runtest(self):
        """
        测试执行入口方法

        调用现有的ApiTestCase执行测试，并保存trans_list供后续钩子使用。
        """
        self.start_time = datetime.datetime.now()
        created_session = None
        test_instance = PytestTestCase(
            case_name=self.name, case_data=self.case_data, case_type=self.case_type
        )

        # 设置必要的属性
        test_instance.case_name = self.case_name
        test_instance.test_case_name = self.case_name
        test_instance.test_case_desc = self.case_data.get("comment", "")

        test_instance.task_id = self.case_meta.get("task_id", "")
        test_instance.run_index = self.case_meta.get("run_times", 1)
        test_instance.context = self.case_meta.get("context") or {}
        test_instance.session = self.case_meta.get("session")
        if test_instance.session is None:
            from requests import Session

            created_session = Session()
            test_instance.session = created_session

        try:
            # 调用现有的ApiTestCase执行逻辑
            if ApiTestCase is not None:
                api_test = ApiTestCase(test_instance)
                api_test.execute()
            else:
                test_instance.trans_list = self._mock_execute()

            # 保存trans_list
            self.trans_list = test_instance.trans_list
            self.stash["trans_list"] = test_instance.trans_list
            self.stash["case_info"] = {
                "case_id": self.case_id,
                "case_name": self.case_name,
                "case_type": self.case_type,
                "case_desc": self.test_case_desc,
                "collection_id": self.case_meta.get(
                    "collection_id", self.parent.path.parent.name
                ),
                "index": int(self.case_meta.get("index", 0)),
                "run_times": int(self.case_meta.get("run_times", 1)),
                "task_id": self.case_meta.get("task_id", ""),
            }

        except Exception as e:
            # 保存错误信息
            error_trans = {
                "id": "error",
                "name": "Test Execution Error",
                "status": 2,
                "log": str(e),
            }
            self.trans_list = [error_trans]
            self.stash["trans_list"] = self.trans_list
            self.stash["case_info"] = {
                "case_id": self.case_id,
                "case_name": self.case_name,
                "case_type": self.case_type,
                "case_desc": self.test_case_desc,
                "collection_id": self.case_meta.get(
                    "collection_id", self.parent.path.parent.name
                ),
                "index": int(self.case_meta.get("index", 0)),
                "run_times": int(self.case_meta.get("run_times", 1)),
                "task_id": self.case_meta.get("task_id", ""),
            }
            raise
        finally:
            self.end_time = datetime.datetime.now()
            if created_session is not None:
                created_session.close()

    def reportinfo(self):
        return self.fspath, 0, self.name

    def _mock_execute(self):
        """模拟执行方法（开发调试用）"""
        self.trans_list = [
            {
                "id": f"api_{i}",
                "name": f"Mock API {i}",
                "status": 0,
                "log": "Mock execution",
                "request": {},
                "response": {},
            }
            for i in range(len(self.case_data.get("apiList", [])))
        ]


class PytestTestCase:
    """
    Pytest测试用例适配器类

    桥接pytest测试用例和现有ApiTestCase执行逻辑。
    """

    def __init__(
        self, case_name: str, case_data: Dict[str, Any], case_type: str = "API"
    ):
        self.case_name = case_name
        self.case_data = case_data
        self.case_type = case_type
        self.session = None
        self.context = {}
        self.trans_list = []
        self.test_data = case_data
        self.test_case_name = case_name
        self.test_case_desc = case_data.get("comment", "")
        self.task_id = ""
        self.driver = None
        self.run_index = 1

    def defineTrans(
        self, trans_id: str, name: str, content: str = "", desc: Optional[str] = None
    ):
        """定义测试事务"""
        trans_dict = {
            "id": trans_id,
            "name": name,
            "content": content,
            "description": desc,
            "log": "",
            "during": 0,
            "status": "",
            "screenShotList": [],
        }
        self.trans_list.append(trans_dict)

    def updateTransStatus(self, status: int):
        """更新当前事务状态"""
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = status

    def debugLog(self, log_info: str):
        """记录调试日志"""
        if len(self.trans_list) > 0:
            self.trans_list[-1]["log"] = self.trans_list[-1].get("log", "") + log_info

    def errorLog(self, log_info: str):
        """记录错误日志"""
        if len(self.trans_list) > 0:
            self.trans_list[-1]["log"] = self.trans_list[-1].get("log", "") + log_info

    def recordTransDuring(self, during: int):
        if len(self.trans_list) > 0:
            self.trans_list[-1]["during"] = during

    def recordFailStatus(self, exc_info=None):
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = 1
            if exc_info is not None:
                self.errorLog(str(exc_info[1]))

    def recordErrorStatus(self, exc_info=None):
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = 2
            if exc_info is not None:
                self.errorLog(str(exc_info[1]))

    def saveScreenShot(self, name: str, screen_shot: bytes):
        """保存截图"""
        if len(self.trans_list) > 0:
            self.trans_list[-1]["screenShotList"].append(name)


def pytest_collect_file(parent, file_path: Path):
    """
    pytest文件收集钩子函数

    当pytest扫描目录时，会为每个.json文件调用此函数。

    Args:
        parent: 父级pytest对象
        file_path: 文件路径对象

    Returns:
        JSONFile: 如果是有效的JSON测试文件，返回收集器；否则返回None
    """
    if file_path.suffix != ".json":
        return None

    normalized_path = _normalize_path(file_path)
    if RUNTIME_CASE_META and normalized_path not in RUNTIME_CASE_META:
        return None

    return JSONFile.from_parent(parent=parent, path=file_path)
