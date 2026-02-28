from __future__ import annotations

"""
Allure 回放（开发旁路能力）。

定位：
- 仅用于开发人员本地查看，不参与平台回传协议、不影响平台调度与上传。
- Allure 不存在/执行失败时应当静默降级（no-op）。

设计原则：
- 只消费 case_info / transactionList，避免侵入业务执行链路
- 仅生成 step/附件，不引入额外的用例状态判定
"""

import json
from typing import Any, Dict


def _try_import_allure():
    """尝试导入 allure；失败则返回 None（旁路能力必须可降级）。"""
    try:
        import allure  # type: ignore

        return allure
    except Exception:
        return None


def replay_case_to_allure(case_info: Dict[str, Any]) -> None:
    """
    将 case_info.transactionList 回放为 Allure step/附件。

    输入：
    - case_info: 平台回传结构（本函数只读取必要字段）

    输出：
    - 无返回值；Allure 缺失或写入失败会被吞掉，不影响主流程
    """
    allure = _try_import_allure()
    if allure is None:
        return

    title = case_info.get("caseName") or f'{case_info.get("caseId")}'
    try:
        allure.dynamic.title(title)
    except Exception:
        pass

    trans_list = case_info.get("transactionList") or []
    for trans in trans_list:
        name = trans.get("name") or trans.get("id") or "step"
        try:
            with allure.step(str(name)):
                log = trans.get("log") or ""
                if log:
                    allure.attach(str(log), name="log", attachment_type=allure.attachment_type.HTML)
                content = trans.get("content")
                if content:
                    allure.attach(str(content), name="content", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            continue

    try:
        allure.attach(
            json.dumps(trans_list, ensure_ascii=False),
            name="transactionList.json",
            attachment_type=allure.attachment_type.JSON,
        )
    except Exception:
        pass
