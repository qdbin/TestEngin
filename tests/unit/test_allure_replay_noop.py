"""
Allure 回放模块单元测试。

约束：
- 在开发环境未安装 allure 时，必须 no-op 不报错
"""

import pytest

from app.allure_replay import replay_case_to_allure


@pytest.mark.unit
def test_allure_replay_noop():
    """Allure 不存在时调用应当安全返回。"""
    replay_case_to_allure(
        {
            "caseId": "100",
            "caseName": "demo",
            "transactionList": [{"id": "1", "name": "step1", "log": "x", "content": "y"}],
        }
    )
