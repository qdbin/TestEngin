from __future__ import annotations

"""
pytest 执行入口封装。

职责：
- 将任务目录交由 pytest 运行
- 注入 ApiPlanPlugin，在 pytest 执行过程中持续产出 case_info 到队列

注意：
- 该模块不触碰平台上传逻辑，上传仍由 LMReport.monitor_result 统一处理。
"""

from typing import Any, Dict, List, Optional

import pytest

from app.pytest_api_plan_plugin import ApiPlanPlugin


def run_api_plan(
    *,
    task_dir: str,
    queue: Any,
    shared_by_collection: Dict[str, Dict[str, Any]],
    run_times: int,
    default_result: List[Dict[str, Any]],
    descriptors_by_path: Dict[str, Dict[str, Any]],
    allure_enabled: bool = False,
    allure_dir: Optional[str] = None,
) -> int:
    """
    执行指定任务目录。

    Args:
        task_dir: 任务根目录（包含 collection 子目录与 case json 文件）。
        queue: 结果通道，协议与 LMReport.monitor_result 一致。
        shared_by_collection: collection 级共享运行时对象映射。
        run_times: 当前执行轮次（首跑=1，重跑=2...）。
        default_result: 当前轮次内存结果容器（供重跑筛选失败用例）。
        descriptors_by_path: casePath -> descriptor 的收集索引。
        allure_enabled: 是否开启 Allure 旁路回放。
        allure_dir: Allure 结果目录（仅在启用时生效）。

    shared_by_collection Schema:
        {
            "collectionId": {
                "session": "<requests.Session>",
                "context": {"k": "v"}
            }
        }

    descriptors_by_path Schema:
        {
            "D:/task/collectionA/case_001.json": {
                "taskId": "task_xxx",
                "collectionId": "collectionA",
                "caseId": "case_001",
                "index": 1,
                "caseType": "API",
                "casePath": "D:/task/collectionA/case_001.json"
            }
        }

    Returns:
        pytest exit code（0 表示执行过程未出现 pytest 级别错误）。
    """
    plugin = ApiPlanPlugin(
        queue=queue,
        shared_by_collection=shared_by_collection,
        run_times=run_times,
        default_result=default_result,
        descriptors_by_path=descriptors_by_path,
        allure_enabled=allure_enabled,
        allure_dir=allure_dir,
    )
    args = [task_dir, "-q"]
    if allure_enabled and allure_dir:
        try:
            # Allure 仅作为开发旁路能力：存在插件则输出结果目录，不存在则静默忽略。
            try:
                __import__("allure_pytest")
            except Exception:
                __import__("pytest_allure")
            args.extend(["--alluredir", allure_dir, "--clean-alluredir"])
        except Exception:
            pass
    return int(pytest.main(args, plugins=[plugin]))
