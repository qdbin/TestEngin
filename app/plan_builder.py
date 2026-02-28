from __future__ import annotations

"""
API 计划文件（.plan.json）构建器。

用途：
- 将任务解析产物（test_plan）转换为可执行的 plan.json
- 交由 pytest 动态收集插件读取并执行

约束：
- plan.json 仅在执行进程内部流转，不属于平台回传协议的一部分
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from app.config import DATA_PATH


@dataclass
class CaseDescriptor:
    """
    单条用例描述（写入 plan.json 的基本单位）。

    字段来源：
    - task_id/collection_id/case_id/index/case_type 来自平台调度解析结果
    - case_path/debug_data 二选一：正常任务走 case_path，debug 任务走 debug_data
    """
    task_id: str
    collection_id: str
    case_id: str
    index: int
    case_type: str
    case_path: Optional[str] = None
    debug_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为 plan.json 可写入的 dict。"""
        return {
            "taskId": self.task_id,
            "collectionId": self.collection_id,
            "caseId": self.case_id,
            "index": int(self.index),
            "caseType": self.case_type,
            "casePath": self.case_path,
            "debugData": self.debug_data,
        }


def parse_case_identity(test_case_name: str) -> Tuple[str, int]:
    """
    从 unittest 风格 test_case 名称中提取 caseId 与 index。

    输入：case_<caseId>_<index>
    输出：(<caseId>, <index>)
    """
    parts = (test_case_name or "").split("_")
    if len(parts) >= 3 and parts[0] == "case":
        return parts[1], int(parts[2])
    raise ValueError(f"invalid test_case name: {test_case_name}")


def build_descriptors_from_test_plan(test_plan: Dict[str, List[Dict[str, Any]]]) -> List[CaseDescriptor]:
    """
    将 task_analysis 产物（collection -> cases）映射为 CaseDescriptor 列表。

    说明：
    - 输出顺序保持与输入一致，便于平台侧 index 展示与重跑定位
    """
    result: List[CaseDescriptor] = []
    for collection_id, cases in test_plan.items():
        for c in cases:
            case_id, index = parse_case_identity(c["test_case"])
            desc = CaseDescriptor(
                task_id=str(c["task_id"]),
                collection_id=str(collection_id),
                case_id=str(case_id),
                index=int(index),
                case_type=str(c["test_type"]),
                case_path=c["test_data"] if isinstance(c["test_data"], str) else None,
                debug_data=c["test_data"] if isinstance(c["test_data"], dict) else None,
            )
            result.append(desc)
    return result


def write_plan_file(task_id: str, run_times: int, descriptors: List[CaseDescriptor]) -> str:
    """
    写入 plan.json 并返回文件路径。

    目录结构：data/{task_id}/{task_id}.run{n}.plan.json
    """
    task_dir = os.path.join(DATA_PATH, str(task_id))
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)
    plan_path = os.path.join(task_dir, f"{task_id}.run{int(run_times)}.plan.json")
    payload = {
        "taskId": str(task_id),
        "runTimes": int(run_times),
        "cases": [d.to_dict() for d in descriptors],
    }
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return plan_path
