from __future__ import annotations

"""
Pytest 任务目录执行插件（动态收集 Item）。

职责：
- 在 pytest 收集阶段通过 pytest_collection_file 从任务目录收集 case json
- 在每个 Item 执行时调用 core/api 执行器（ApiTestCase），产出 transactionList
- 组装平台协议 case_info 并通过 queue 实时回传给 Reporter

关键约束：
- 不直接调用平台上传接口（upload_result/complete_task），避免调度/回传风险
- Allure 仅作为开发旁路能力，可开关且失败必须静默降级
"""

import os
import time
import contextlib
from typing import Any, Dict, List, Optional

import pytest

from app.api_runtime import ApiRuntime
from app.case_info_builder import CaseInfoBuildInput, build_case_info

try:
    from core.api.testcase import ApiTestCase  # type: ignore
except Exception:
    ApiTestCase = None


class ApiCaseJsonFile(pytest.File):
    def __init__(self, *args, descriptor: Dict[str, Any], **kwargs):
        super().__init__(*args, **kwargs)
        self.descriptor = descriptor

    def collect(self):
        name = f'{self.descriptor.get("collectionId")}/{self.descriptor.get("caseId")}/{self.descriptor.get("index")}'
        yield ApiCaseItem.from_parent(self, name=name, descriptor=self.descriptor)


class ApiCaseItem(pytest.Item):
    """
    单条 API 用例 Item。

    该 Item 不直接持有业务逻辑，仅把 descriptor 交给 ApiPlanPlugin 执行，
    便于统一维护回传、Allure、共享 session/context 等策略。
    """

    def __init__(self, name, parent, descriptor: Dict[str, Any]):
        super().__init__(name, parent)
        self.descriptor = descriptor

    def runtest(self):
        """pytest 执行入口：定位 ApiPlanPlugin 并委派执行。"""
        plugin = None
        for p in self.config.pluginmanager.get_plugins():
            if isinstance(p, ApiPlanPlugin):
                plugin = p
                break
        if plugin is None:
            raise RuntimeError("pytest plugin missing")
        plugin.execute_case(self.descriptor)

    def reportinfo(self):
        return self.fspath, 0, f"api-case: {self.name}"


class ApiPlanPlugin:
    """
    引擎侧 pytest 插件（带状态回传能力）。

    运行方式：
    - pytest.main(..., plugins=[ApiPlanPlugin(...)] ) 注入
    - pytest_collect_file 负责识别任务目录内被索引的 case json 并触发收集
    - ApiCaseItem.runtest -> execute_case 执行业务逻辑并回传 case_info
    """

    def __init__(
        self,
        *,
        queue: Any,
        shared_by_collection: Dict[str, Dict[str, Any]],
        run_times: int,
        default_result: List[Dict[str, Any]],
        descriptors_by_path: Dict[str, Dict[str, Any]],
        allure_enabled: bool = False,
        allure_dir: Optional[str] = None,
    ):
        self.queue = queue
        self.shared_by_collection = shared_by_collection
        self.run_times = int(run_times)
        self.default_result = default_result
        self.descriptors_by_path = descriptors_by_path
        self.allure_enabled = bool(allure_enabled)
        self.allure_dir = allure_dir

    def pytest_collect_file(self, parent, path):
        file_path = os.path.normcase(os.path.abspath(str(path)))
        if not str(path).lower().endswith(".json"):
            return None
        descriptor = self.descriptors_by_path.get(file_path)
        if descriptor is not None:
            return ApiCaseJsonFile.from_parent(
                parent, fspath=path, descriptor=descriptor
            )
        return None

    def pytest_sessionstart(self, session):
        """会话开始：仅在启用 Allure 时尝试创建输出目录。"""
        if not self.allure_enabled:
            return
        if self.allure_dir is None:
            return
        try:
            os.makedirs(self.allure_dir, exist_ok=True)
        except Exception:
            return

    def execute_case(self, desc: Dict[str, Any]) -> None:
        """
        执行单条用例并回传 case_info。

        注意：
        - 该方法是引擎与 pytest 的“连接点”，负责把核心执行器输出转换为平台协议
        - 失败/错误最终会 raise AssertionError，使 pytest 侧也能体现失败（平台仍以 case_info 为准）
        """
        task_id = str(desc.get("taskId"))
        collection_id = str(desc.get("collectionId"))
        case_id = str(desc.get("caseId"))
        index = int(desc.get("index") or 0)
        case_type = str(desc.get("caseType") or "API")
        if case_type != "API":
            # MVP: 非 API 用例直接跳过，避免影响 Web/App 旧逻辑与平台回传。
            now_ms = int(time.time() * 1000)
            start_ms = now_ms
            end_ms = now_ms
            case_info = build_case_info(
                CaseInfoBuildInput(
                    task_id=task_id,
                    collection_id=collection_id,
                    case_id=case_id,
                    index=index,
                    case_type=case_type,
                    run_times=self.run_times,
                    start_time_ms=start_ms,
                    end_time_ms=end_ms,
                    transaction_list=[],
                    case_name="跳过",
                    case_desc=None,
                ),
                status=3,
            )
            self.default_result.append(case_info)
            self.queue.put(case_info)
            return

        shared = self.shared_by_collection.get(collection_id)
        if shared is None:
            raise RuntimeError(f"collection shared missing: {collection_id}")
        session = shared["session"]  # collection 级共享 session（保持与旧引擎一致）
        context = shared["context"]  # collection 级共享 context（保持与旧引擎一致）
        test_data = desc.get("casePath")

        runtime = ApiRuntime(
            task_id=task_id,
            collection_id=collection_id,
            case_id=case_id,
            index=index,
            run_times=self.run_times,
            test_data=test_data,
            session=session,
            context=context,
        )

        runtime.start()
        try:
            # 对齐原引擎：将 print 输出归档到 transaction log，便于平台排障展示。
            with contextlib.redirect_stdout(runtime.stdout_buffer):
                if ApiTestCase is None:
                    from core.api.testcase import ApiTestCase as _ApiTestCase  # type: ignore

                    _ApiTestCase(test=runtime).execute()
                else:
                    ApiTestCase(test=runtime).execute()
        except AssertionError as e:
            # 断言失败：记录 fail（状态=1），继续完成 case_info 组装与回传。
            runtime.recordFailStatus((AssertionError, e, e.__traceback__))
        except Exception as e:
            # 非断言异常：记录 error（状态=2）。
            runtime.recordErrorStatus((type(e), e, e.__traceback__))
        finally:
            runtime.stop()

        status = runtime.handleResult()
        start_ms = (
            int(runtime.start_time.timestamp() * 1000)
            if runtime.start_time
            else runtime.now_ms()
        )
        end_ms = (
            int(runtime.stop_time.timestamp() * 1000)
            if runtime.stop_time
            else runtime.now_ms()
        )

        case_info = build_case_info(
            CaseInfoBuildInput(
                task_id=task_id,
                collection_id=collection_id,
                case_id=case_id,
                index=index,
                case_type=runtime.case_type,
                run_times=self.run_times,
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                transaction_list=runtime.trans_list,
                case_name=getattr(runtime, "test_case_name", None),
                case_desc=getattr(runtime, "test_case_desc", None),
            ),
            status=status,
        )
        self.default_result.append(case_info)
        self.queue.put(case_info)

        if self.allure_enabled:
            try:
                from app.allure_replay import replay_case_to_allure

                replay_case_to_allure(case_info)
            except Exception:
                pass

        if status in (1, 2):
            raise AssertionError(runtime.error_summary() or "case failed")
