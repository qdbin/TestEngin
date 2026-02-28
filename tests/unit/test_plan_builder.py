"""
plan_builder 单元测试。

覆盖点：
- test_plan -> CaseDescriptor 的转换
- plan.json 写入结构与关键字段（taskId/runTimes/cases）稳定性
"""

import json

import pytest

from app.plan_builder import build_descriptors_from_test_plan, write_plan_file
from app.setting import LMSession


@pytest.mark.unit
def test_build_descriptors_and_write_plan(tmp_data_dir):
    """确保 plan.json 的最小字段齐全且可被 pytest 插件消费。"""
    plan = {
        "c1": [
            {
                "driver": None,
                "session": LMSession(),
                "context": {},
                "task_id": "t1",
                "test_type": "API",
                "test_class": "class_c1",
                "test_case": "case_100_1",
                "test_data": "data/t1/c1/100.json",
            }
        ]
    }

    descriptors = build_descriptors_from_test_plan(plan)
    assert len(descriptors) == 1
    assert descriptors[0].case_id == "100"
    assert descriptors[0].index == 1

    plan_path = write_plan_file(task_id="t1", run_times=1, descriptors=descriptors)
    with open(plan_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["taskId"] == "t1"
    assert payload["runTimes"] == 1
    assert len(payload["cases"]) == 1
