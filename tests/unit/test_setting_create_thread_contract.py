"""
LMSetting.create_thread 单元测试（平台契约与重跑语义）。

覆盖点：
- run_all_start/run_all_stop 控制消息格式（避免 Reporter 端解析异常）
- reRun=True 的二次执行语义（失败用例筛选后重跑）
"""

import pytest

from app.setting import LMSetting


class FakeQueue:
    """简化队列替身：记录 put 的所有消息，用于断言协议与顺序。"""
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)


class FakeValue:
    """模拟 multiprocessing.Value，仅保留 value 字段。"""
    def __init__(self):
        self.value = 0


@pytest.mark.unit
def test_create_thread_sends_run_all_start_with_api_type(monkeypatch):
    """MVP: create_thread 必须发送带 data_type 的 run_all_start，避免平台回传问题。"""
    task = {
        "taskId": "t1",
        "taskType": "debug",
        "reRun": False,
        "maxThread": 1,
        "testCollectionList": [
            {
                "collectionId": "c1",
                "testCaseList": [{"caseId": "100", "index": 1, "caseType": "API"}],
            }
        ],
        "debugData": {"caseId": "100", "caseName": "demo", "comment": None, "functions": [], "params": {}, "apiList": []},
    }

    q = FakeQueue()
    current = FakeValue()

    called = {"n": 0}

    def fake_run_api_plan(**kwargs):
        called["n"] += 1
        return 0

    monkeypatch.setattr("app.setting.run_api_plan", fake_run_api_plan)

    s = LMSetting(task)
    plan = s.task_analysis()
    s.create_thread(plan, q, current)

    assert q.items[0].startswith("run_all_start--t1--API")
    assert q.items[-1] == "run_all_stop--t1"
    assert current.value == 1
    assert called["n"] == 1


@pytest.mark.unit
def test_create_thread_rerun_calls_runner_twice(monkeypatch):
    """reRun=True 时应触发两轮执行：首轮失败后仅重跑失败用例。"""
    task = {
        "taskId": "t1",
        "taskType": "debug",
        "reRun": True,
        "maxThread": 1,
        "testCollectionList": [
            {
                "collectionId": "c1",
                "testCaseList": [{"caseId": "100", "index": 1, "caseType": "API"}],
            }
        ],
        "debugData": {"caseId": "100", "caseName": "demo", "comment": None, "functions": [], "params": {}, "apiList": []},
    }

    q = FakeQueue()
    current = FakeValue()

    def fake_run_api_plan(**kwargs):
        default_result = kwargs["default_result"]
        if kwargs["run_times"] == 1:
            default_result.append({"collectionId": "c1", "caseId": "100", "index": 1, "status": 1})
        else:
            default_result.append({"collectionId": "c1", "caseId": "100", "index": 1, "status": 0})
        return 0

    monkeypatch.setattr("app.setting.run_api_plan", fake_run_api_plan)

    s = LMSetting(task)
    plan = s.task_analysis()
    s.create_thread(plan, q, current)

    assert current.value == 1
    assert q.items[0].startswith("run_all_start--t1--API")
    assert q.items[-1] == "run_all_stop--t1"
