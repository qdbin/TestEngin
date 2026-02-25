# -*- coding: utf-8 -*-
"""
Web场景操作模块

提供自定义场景操作功能，支持执行复杂的测试场景和业务逻辑。
"""

import sys

from selenium.common.exceptions import NoSuchElementException
from core.web.driver import Operation


class Scenario(Operation):
    """
    场景操作类
    
    提供自定义场景操作功能，支持执行用户定义的复杂测试场景。
    """

    def custom(self, **kwargs):
        """
        执行自定义代码场景
        
        @param kwargs: 包含自定义代码和相关参数的字典
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 执行自定义代码失败时抛出异常
        
        Example:
            scenario.custom(code="print('Hello World')", trans="打印消息")
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["driver"] = self.driver
        names["test"] = self.test
        try:
            def print(*args, sep=' ', end='\n', file=None, flush=False):
                if file is None or file in (sys.stdout, sys.stderr):
                    file = names["test"].stdout_buffer
                self.print(*args, sep=sep, end=end, file=file, flush=flush)

            def sys_get(name):
                if name in names["test"].context:
                    return names["test"].context[name]
                elif name in names["test"].common_params:
                    return names["test"].common_params[name]
                else:
                    raise KeyError("不存在的公共参数或关联变量: {}".format(name))

            def sys_put(name, val, ps=False):
                if ps:
                    names["test"].common_params[name] = val
                else:
                    names["test"].context[name] = val

            exec(code)
            self.test.debugLog("成功执行 %s" % kwargs["trans"])
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
