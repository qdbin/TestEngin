"""
pytest 全局测试配置（TestEngin）。

目标：
- 单元测试/集成测试均不依赖真实平台服务、真实网络、真实数据库
- 在开发/沙箱环境缺少三方依赖时提供最小替身，确保 import 与主流程可覆盖
"""

import os
import re
import sys
import types

import pytest


class FakeQueue:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)


@pytest.fixture
def fake_queue():
    return FakeQueue()


@pytest.fixture(autouse=True)
def disable_allure_env(monkeypatch):
    monkeypatch.delenv("TESTENGIN_ALLURE", raising=False)


@pytest.fixture(scope="session", autouse=True)
def ensure_assertpy_available():
    """
    保证测试环境可导入 assertpy。

    该项目的 core/assertion.py 依赖 assertpy；但在部分开发环境/沙箱中可能未预装。
    这里为单元/集成测试提供最小替身，仅实现当前测试覆盖到的断言链路（is_equal_to）。
    """
    try:
        import assertpy  # noqa: F401

        return
    except Exception:
        pass

    class _AssertThat:
        def __init__(self, value):
            self._value = value

        def is_equal_to(self, expected):
            assert self._value == expected
            return self

    class _AssertPyFacade:
        @staticmethod
        def assert_that(value):
            return _AssertThat(value)

    m = types.ModuleType("assertpy")
    m.assertpy = _AssertPyFacade
    sys.modules["assertpy"] = m


@pytest.fixture(scope="session", autouse=True)
def ensure_db_drivers_available():
    """
    保证测试环境可导入数据库驱动模块。

    core/api/teststep.py 会 import tools/utils/sql.py，而该模块依赖多种数据库驱动。
    集成测试不需要真实数据库连接，但需要 import 成功以覆盖主流程分支。
    """

    def _install_stub(name: str):
        if name in sys.modules:
            return
        m = types.ModuleType(name)

        def _connect(*_a, **_k):
            raise RuntimeError(f"db driver '{name}' is not available in test env")

        m.connect = _connect
        sys.modules[name] = m

    for mod_name in ("pymssql", "pymysql", "psycopg2", "cx_Oracle"):
        _install_stub(mod_name)


@pytest.fixture(scope="session", autouse=True)
def ensure_jsonpath_available():
    """
    保证测试环境可导入 jsonpath（第三方库）。

    项目在 tools/utils/utils.py 中依赖 jsonpath.jsonpath；部分环境可能未预装。
    这里提供最小替身以保证 import 成功，避免集成测试因环境缺失而失败。
    """
    try:
        import jsonpath  # noqa: F401

        return
    except Exception:
        pass

    if "jsonpath" in sys.modules:
        return

    m = types.ModuleType("jsonpath")

    def _jsonpath(data, expression):
        if expression == "$":
            return [data]
        if (
            isinstance(expression, str)
            and expression.startswith("$.")
            and isinstance(data, dict)
        ):
            key = expression[2:]
            if key in data:
                return [data[key]]
        return False

    m.jsonpath = _jsonpath
    sys.modules["jsonpath"] = m


@pytest.fixture(scope="session", autouse=True)
def ensure_jsonpath_ng_available():
    try:
        from jsonpath_ng.parser import JsonPathParser  # noqa: F401

        return
    except Exception:
        pass

    if "jsonpath_ng.parser" in sys.modules:
        return

    class _Expr:
        def __init__(self, tokens):
            self.tokens = tokens

        def update(self, data, value):
            if data is None:
                return
            cur = data
            for token in self.tokens[:-1]:
                if isinstance(cur, dict):
                    cur = cur.setdefault(token, {})
                else:
                    return
            if self.tokens and isinstance(cur, dict):
                cur[self.tokens[-1]] = value

    class JsonPathParser:
        def parse(self, expression):
            if expression == "$":
                return _Expr([])
            tokens = re.findall(r"'([^']+)'", str(expression))
            if (
                not tokens
                and isinstance(expression, str)
                and expression.startswith("$.")
            ):
                tokens = [x for x in expression[2:].split(".") if x]
            return _Expr(tokens)

    parser_module = types.ModuleType("jsonpath_ng.parser")
    parser_module.JsonPathParser = JsonPathParser
    pkg_module = types.ModuleType("jsonpath_ng")
    pkg_module.parser = parser_module
    sys.modules["jsonpath_ng"] = pkg_module
    sys.modules["jsonpath_ng.parser"] = parser_module


@pytest.fixture(scope="session", autouse=True)
def ensure_faker_available():
    """
    保证测试环境可导入 faker（Faker 库）。

    该项目的函数库 tools/funclib 依赖 faker；集成测试需要能够 import 并走主流程，
    但不需要真实随机数据生成能力，因此提供最小替身以避免环境差异导致失败。
    """
    try:
        import faker  # noqa: F401

        return
    except Exception:
        pass

    if "faker" in sys.modules:
        return

    providers_mod = types.ModuleType("faker.providers")

    class BaseProvider:
        pass

    providers_mod.BaseProvider = BaseProvider
    sys.modules["faker.providers"] = providers_mod

    faker_mod = types.ModuleType("faker")

    class Faker:
        def __init__(self, *args, **kwargs):
            self._providers = []

        def add_provider(self, provider):
            self._providers.append(provider)

        @classmethod
        def seed(cls, *_args, **_kwargs):
            return None

    faker_mod.Faker = Faker
    faker_mod.providers = providers_mod
    sys.modules["faker"] = faker_mod


@pytest.fixture(scope="session", autouse=True)
def ensure_pypinyin_available():
    """
    保证测试环境可导入 pypinyin。

    tools/funclib/provider/provider.py 依赖 pypinyin.lazy_pinyin；集成测试不需要该能力，
    仅需 import 成功，因此提供最小替身。
    """
    try:
        import pypinyin  # noqa: F401

        return
    except Exception:
        pass

    if "pypinyin" in sys.modules:
        return

    m = types.ModuleType("pypinyin")

    def lazy_pinyin(s):
        return [str(s)]

    m.lazy_pinyin = lazy_pinyin
    sys.modules["pypinyin"] = m


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    return tmp_path
