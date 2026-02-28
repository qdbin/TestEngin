"""
ApiRuntime 单元测试。

覆盖点：
- success/fail/error 三种状态计算分支
- 与平台 status 语义对齐：0/1/2
"""

import pytest

from app.api_runtime import ApiRuntime


@pytest.mark.unit
def test_runtime_success_status():
    """无异常时应返回 success(0)。"""
    rt = ApiRuntime(
        task_id="t1",
        collection_id="c1",
        case_id="100",
        index=1,
        run_times=1,
        test_data={},
        session=object(),
        context={},
    )
    rt.defineTrans("1", "step1")
    rt.start()
    rt.stop()
    assert rt.handleResult() == 0


@pytest.mark.unit
def test_runtime_fail_status():
    """记录 AssertionError 后应返回 fail(1)。"""
    rt = ApiRuntime(
        task_id="t1",
        collection_id="c1",
        case_id="100",
        index=1,
        run_times=1,
        test_data={},
        session=object(),
        context={},
    )
    rt.defineTrans("1", "step1")
    rt.recordFailStatus((AssertionError, AssertionError("x"), None))
    assert rt.handleResult() == 1


@pytest.mark.unit
def test_runtime_error_status():
    """记录非 AssertionError 异常后应返回 error(2)。"""
    rt = ApiRuntime(
        task_id="t1",
        collection_id="c1",
        case_id="100",
        index=1,
        run_times=1,
        test_data={},
        session=object(),
        context={},
    )
    rt.defineTrans("1", "step1")
    rt.recordErrorStatus((RuntimeError, RuntimeError("boom"), None))
    assert rt.handleResult() == 2
