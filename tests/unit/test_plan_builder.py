"""
plan_builder 单元测试。

覆盖点：
- test_plan -> CaseDescriptor 的转换
- descriptor 索引（casePath -> descriptor）构建稳定性
"""

import pytest

from app.plan_builder import build_descriptors_from_test_plan, build_descriptor_index
from app.setting import LMSession


@pytest.mark.unit
def test_build_descriptors_and_index():
    """确保 descriptor 索引可被 pytest 收集插件稳定消费。"""
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
    index = build_descriptor_index(descriptors)
    assert len(index) == 1
    only = list(index.values())[0]
    assert only["taskId"] == "t1"
    assert only["collectionId"] == "c1"
    assert only["caseId"] == "100"
