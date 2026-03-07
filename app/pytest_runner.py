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

    参数约束：
    - queue: 与 LMReport.monitor_result 同协议（put(case_info) / put(control_message)）
    - shared_by_collection: 与原引擎一致的 session/context 共享结构
    - default_result: 作为 create_thread 的结果聚合容器（用于 reRun 重跑判定）

    返回：
    - pytest exit code（0 表示执行过程未出现 pytest 级别错误）
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
