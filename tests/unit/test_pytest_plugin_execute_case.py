"""
pytest_api_plan_plugin 单元测试。

覆盖点：
- execute_case 的 API 成功路径（产出 case_info 并推送队列）
- Allure 旁路失败不影响主流程
- 非 API case 跳过逻辑与时间戳有效性
"""

import pytest

from app.pytest_api_plan_plugin import ApiPlanPlugin


class FakeApiTestCase:
    def __init__(self, test):
        self.test = test

    def execute(self):
        # 模拟 core/api 执行器最小行为：创建一个 transaction 并写入用例名称。
        self.test.defineTrans("1", "step1")
        print("hello")
        setattr(self.test, "test_case_name", "demo")
        setattr(self.test, "test_case_desc", None)


@pytest.mark.unit
def test_execute_case_success(monkeypatch, fake_queue):
    """成功执行时应产生 status=0，且控制台输出应落入 transaction log。"""
    from app import pytest_api_plan_plugin as mod

    monkeypatch.setattr(mod, "ApiTestCase", FakeApiTestCase)
    monkeypatch.setattr(
        mod,
        "replay_case_to_allure",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("should not be called")
        ),
        raising=False,
    )

    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": object(), "context": {}}},
        run_times=1,
        default_result=[],
        descriptors_by_path={},
        allure_enabled=False,
        allure_dir=None,
    )
    plugin.execute_case(
        {
            "taskId": "t1",
            "collectionId": "c1",
            "caseId": "100",
            "index": 1,
            "caseType": "API",
            "casePath": "{}",
        }
    )
    assert len(plugin.default_result) == 1
    assert plugin.default_result[0]["status"] == 0
    assert "控制台输出" in (plugin.default_result[0]["transactionList"][0]["log"] or "")
    assert len(fake_queue.items) == 1


@pytest.mark.unit
def test_execute_case_allure_failure_does_not_break(monkeypatch, fake_queue):
    """Allure 回放异常必须被吞掉，不能影响平台回传与用例状态。"""
    from app import pytest_api_plan_plugin as mod

    monkeypatch.setattr(mod, "ApiTestCase", FakeApiTestCase)

    import app.allure_replay as ar

    monkeypatch.setattr(
        ar,
        "replay_case_to_allure",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": object(), "context": {}}},
        run_times=1,
        default_result=[],
        descriptors_by_path={},
        allure_enabled=True,
        allure_dir=None,
    )
    plugin.execute_case(
        {
            "taskId": "t1",
            "collectionId": "c1",
            "caseId": "100",
            "index": 1,
            "caseType": "API",
            "casePath": "{}",
        }
    )
    assert plugin.default_result[0]["status"] == 0


@pytest.mark.unit
def test_execute_case_skip_non_api(fake_queue):
    """非 API case 在 MVP 中直接跳过，避免影响 Web/App 旧逻辑。"""
    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": object(), "context": {}}},
        run_times=1,
        default_result=[],
        descriptors_by_path={},
        allure_enabled=False,
        allure_dir=None,
    )
    plugin.execute_case(
        {
            "taskId": "t1",
            "collectionId": "c1",
            "caseId": "100",
            "index": 1,
            "caseType": "WEB",
            "casePath": None,
        }
    )
    assert plugin.default_result[0]["status"] == 3
    assert plugin.default_result[0]["startTime"] > 0
    assert plugin.default_result[0]["endTime"] > 0
