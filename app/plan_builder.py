from __future__ import annotations

"""
API 执行 descriptor 构建器。

用途：
- 将 task_analysis 产物转换为可执行 descriptor
- 构建 casePath -> descriptor 索引供 pytest 收集插件过滤
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CaseDescriptor:
    """
    单条用例描述（运行时索引基本单位）。

    字段来源：
    - task_id/collection_id/case_id/index/case_type 来自平台调度解析结果
    - case_path 指向真实用例 json 文件
    """

    task_id: str
    collection_id: str
    case_id: str
    index: int
    case_type: str
    case_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为可执行 descriptor。"""
        return {
            "taskId": self.task_id,
            "collectionId": self.collection_id,
            "caseId": self.case_id,
            "index": int(self.index),
            "caseType": self.case_type,
            "casePath": self.case_path,
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


def build_descriptors_from_test_plan(
    test_plan: Dict[str, List[Dict[str, Any]]],
) -> List[CaseDescriptor]:
    """
    将 task_analysis 产物（collection -> cases）映射为 CaseDescriptor 列表。

    test_plan Schema:
        {
            "collectionA": [
                {
                    "task_id": "task_xxx",
                    "test_type": "API",
                    "test_case": "case_7e471c1f_1",
                    "test_data": "D:/task/collectionA/7e471c1f.json"
                }
            ]
        }

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
            )
            result.append(desc)
    return result


def build_descriptor_index(
    descriptors: List[CaseDescriptor],
) -> Dict[str, Dict[str, Any]]:
    """
    构建按 casePath 索引的 descriptor 映射。

    Returns:
        以“标准化后的绝对路径”为 key 的映射，用于 pytest 收集阶段 O(1) 过滤。
    """
    result: Dict[str, Dict[str, Any]] = {}
    for desc in descriptors:
        if not desc.case_path:
            # 关键步骤：忽略缺失 case_path 的 descriptor，避免污染收集索引。
            continue
        key = os.path.normcase(os.path.abspath(str(desc.case_path)))
        result[key] = desc.to_dict()
    return result
