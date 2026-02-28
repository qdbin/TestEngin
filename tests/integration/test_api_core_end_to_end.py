"""
API Core 集成测试（不依赖平台/不发真实网络）。

目标：
- 尽可能覆盖 core/api 的关键执行分支（useSession/saveSession、条件跳过、断言失败）
- 通过强断言提高变异体杀死率（确保走到目标分支，否则直接失败）

约束：
- 所有网络/DB/平台调用均通过 monkeypatch 替换为 fake
"""

import pytest


class _FakeCookies:
    """模拟 requests.cookies，用于 save_response 中 cookies.items() 遍历。"""
    def __init__(self, data=None):
        self._data = dict(data or {})

    def items(self):
        return self._data.items()


class _FakeResponse:
    """模拟 requests.Response，仅实现本项目会用到的最小接口。"""
    def __init__(self, *, status_code=200, headers=None, json_data=None, text="OK", content=b"OK"):
        self.status_code = status_code
        self.headers = dict(headers or {})
        self._json_data = json_data
        self.text = text
        self.content = content
        self.cookies = _FakeCookies({"sid": "abc"})
        self.request = object()

    def json(self):
        if self._json_data is None:
            raise ValueError("not json")
        return self._json_data


class _SessionHolder:
    """对齐 LMSession：持有一个 .session 对象供 ApiTestStep 调用。"""
    def __init__(self, inner):
        self.session = inner


def _make_case(*, controller, assertions=None, relations=None):
    """构造最小可执行的 case_message（与 get_case_message 格式兼容）。"""
    return {
        "comment": None,
        "caseId": "100",
        "caseName": "demo",
        "functions": [],
        "params": {},
        "apiList": [
            {
                "apiId": "api-1",
                "apiName": "demo-api",
                "apiDesc": None,
                "url": "http://127.0.0.1:8080",
                "path": "/demo",
                "method": "GET",
                "protocol": "HTTP",
                "headers": {"content-type": "application/json"},
                "proxies": None,
                "body": None,
                "query": {},
                "rest": {},
                "assertions": assertions,
                "relations": relations,
                "controller": controller,
            }
        ],
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "use_session,save_session",
    [
        ("true", "true"),
        ("true", "false"),
        ("false", "true"),
        ("false", "false"),
    ],
)
def test_api_core_session_branches_execute_without_network(monkeypatch, fake_queue, use_session, save_session):
    """
    覆盖 ApiTestStep.execute 中 useSession/saveSession 的四种分支：
    - use+save: self.session.session.request
    - use only: deepcopy(session).request
    - save only: Session().request 且回写 self.session.session
    - none: requests.request
    同时确保全程不发生真实网络访问。
    """
    from app.pytest_api_plan_plugin import ApiPlanPlugin
    import core.api.teststep as step_mod

    call = {"use_save": 0, "use_only": 0, "save_only": 0, "none": 0}

    class _Inner:
        def request(self, method, url, **kwargs):
            # useSession=true & saveSession=true 分支会走到这里
            call["use_save"] += 1
            return _FakeResponse(status_code=200, json_data={"ok": True}, content=b'{"ok":true}')

    class _InnerCopy:
        def request(self, method, url, **kwargs):
            # useSession=true & saveSession=false 分支会走到这里（deepcopy 后请求）
            call["use_only"] += 1
            return _FakeResponse(status_code=200, json_data={"ok": True}, content=b'{"ok":true}')

    def _fake_deepcopy(obj):
        return _InnerCopy()

    class _NewSession:
        def request(self, method, url, **kwargs):
            # useSession=false & saveSession=true 分支会走到这里，并回写 holder.session
            call["save_only"] += 1
            return _FakeResponse(status_code=200, headers={"Content-Disposition": "attachment"}, content=b"x" * 10)

    def _fake_request(method, url, **kwargs):
        # useSession=false & saveSession=false 分支会走到这里（requests.request）
        call["none"] += 1
        return _FakeResponse(status_code=200, text="OK", content=b"OK")

    monkeypatch.setattr(step_mod, "deepcopy", _fake_deepcopy)
    monkeypatch.setattr(step_mod, "Session", lambda: _NewSession())
    monkeypatch.setattr(step_mod, "request", _fake_request)

    holder = _SessionHolder(_Inner())
    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": holder, "context": {}}},
        run_times=1,
        default_result=[],
        allure_enabled=False,
        allure_dir=None,
    )

    case = _make_case(
        controller={
            "sleepBeforeRun": 0,
            "sleepAfterRun": 0,
            "useSession": use_session,
            "saveSession": save_session,
            "pre": None,
            "post": None,
            "errorContinue": "false",
        }
    )

    plugin.execute_case(
        {
            "taskId": "t1",
            "collectionId": "c1",
            "caseId": "100",
            "index": 1,
            "caseType": "API",
            "casePath": None,
            "debugData": case,
        }
    )

    assert plugin.default_result[0]["status"] == 0
    assert len(fake_queue.items) == 1

    if use_session == "true" and save_session == "true":
        assert call["use_save"] == 1 and call["use_only"] == 0 and call["save_only"] == 0 and call["none"] == 0
    elif use_session == "true" and save_session == "false":
        assert call["use_only"] == 1 and call["use_save"] == 0 and call["save_only"] == 0 and call["none"] == 0
    elif use_session == "false" and save_session == "true":
        assert call["save_only"] == 1 and call["use_save"] == 0 and call["use_only"] == 0 and call["none"] == 0
        assert isinstance(holder.session, _NewSession)
    else:
        assert call["none"] == 1 and call["use_save"] == 0 and call["use_only"] == 0 and call["save_only"] == 0


@pytest.mark.integration
def test_api_core_condition_skip_marks_transaction_skip(monkeypatch, fake_queue):
    """
    覆盖 ApiTestCase.loop_execute 中 “条件控制器为否 -> 跳过接口执行” 分支：
    - 该分支应当写入 transaction.status=3
    - case 整体不应失败
    """
    from app.pytest_api_plan_plugin import ApiPlanPlugin
    import core.api.teststep as step_mod

    def _fake_request(method, url, **kwargs):
        raise AssertionError("should not send request when condition is false")

    monkeypatch.setattr(step_mod, "request", _fake_request)

    holder = _SessionHolder(object())
    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": holder, "context": {}}},
        run_times=1,
        default_result=[],
        allure_enabled=False,
        allure_dir=None,
    )

    case = _make_case(
        controller={
            "sleepBeforeRun": 0,
            "sleepAfterRun": 0,
            "useSession": "false",
            "saveSession": "false",
            "pre": None,
            "post": None,
            "errorContinue": "false",
            "whetherExec": '[{"assertion":"相等","target":"1","expect":"2"}]',
        }
    )

    plugin.execute_case(
        {
            "taskId": "t1",
            "collectionId": "c1",
            "caseId": "100",
            "index": 1,
            "caseType": "API",
            "casePath": None,
            "debugData": case,
        }
    )

    assert plugin.default_result[0]["status"] == 0
    trans = plugin.default_result[0]["transactionList"][0]
    assert trans["status"] == 3


@pytest.mark.integration
def test_api_core_assertion_failure_marks_case_failed(monkeypatch, fake_queue):
    """
    覆盖断言失败路径：
    - ApiTestStep.check 生成 assert_result=False
    - ApiTestCase.loop_execute 抛 AssertionError
    - 插件捕获后应当标记 case status=1 并推送到队列
    """
    from app.pytest_api_plan_plugin import ApiPlanPlugin
    import core.api.teststep as step_mod

    def _fake_request(method, url, **kwargs):
        return _FakeResponse(status_code=200, json_data={"code": 0}, content=b'{"code":0}')

    monkeypatch.setattr(step_mod, "request", _fake_request)

    holder = _SessionHolder(object())
    plugin = ApiPlanPlugin(
        queue=fake_queue,
        shared_by_collection={"c1": {"session": holder, "context": {}}},
        run_times=1,
        default_result=[],
        allure_enabled=False,
        allure_dir=None,
    )

    case = _make_case(
        controller={
            "sleepBeforeRun": 0,
            "sleepAfterRun": 0,
            "useSession": "false",
            "saveSession": "false",
            "pre": None,
            "post": None,
            "errorContinue": "false",
        },
        assertions=[
            {"assertion": "相等", "from": "resCode", "method": "jsonpath", "expression": "$", "expect": "201"}
        ],
    )

    with pytest.raises(AssertionError):
        plugin.execute_case(
            {
                "taskId": "t1",
                "collectionId": "c1",
                "caseId": "100",
                "index": 1,
                "caseType": "API",
                "casePath": None,
                "debugData": case,
            }
        )

    assert plugin.default_result[0]["status"] == 1
    assert len(fake_queue.items) == 1
