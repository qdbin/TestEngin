from __future__ import annotations

"""
平台回传 case_info 结构构建器。

约束：
- 字段名/结构必须与平台已有协议一致（Reporter 直接透传上传）。
- 该模块只负责拼装数据，不涉及任何上传/调度逻辑，避免引入平台回传风险。
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CaseInfoBuildInput:
    """
    构建 case_info 所需的输入集合。

    说明：
    - transaction_list 允许为任意结构（通常是 List[Dict]），由执行器产生并透传。
    - start_time_ms/end_time_ms 由执行器控制，平台侧用于排序与耗时展示。
    """

    task_id: str
    collection_id: str
    case_id: str
    index: int
    case_type: str
    run_times: int
    start_time_ms: int
    end_time_ms: int
    transaction_list: Any
    case_name: Optional[str] = None
    case_desc: Optional[str] = None


def build_case_info(i: CaseInfoBuildInput, status: int) -> Dict[str, Any]:
    """
    构建平台期望的 case_info 字典。

    字段说明（与平台协议对齐）：
    - status: 0成功/1失败/2错误/3跳过
    - startTime/endTime: 毫秒时间戳
    - transactionList: 事务步骤列表（用于展示与排障）
    """
    return {
        "status": int(status),
        "startTime": int(i.start_time_ms),
        "endTime": int(i.end_time_ms),
        "collectionId": str(i.collection_id),
        "caseId": str(i.case_id),
        "caseType": str(i.case_type),
        "caseName": i.case_name or "未知",
        "caseDesc": i.case_desc,
        "index": int(i.index),
        "runTimes": int(i.run_times),
        "transactionList": i.transaction_list,
    }
