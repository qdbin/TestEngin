import sys

from uiautomator2 import UiObjectNotFoundError
from core.assertion import LMAssert
from core.app.device import Operation


class Condition(Operation):
    """
    条件判断操作类
    
    提供各种条件判断功能，用于在测试流程中进行条件分支控制。
    与断言操作不同，条件判断不会在失败时中断测试，而是返回判断结果供后续逻辑使用。
    
    继承自Operation基类，具备元素查找和设备操作的基础能力。
    支持Android和iOS双平台的条件判断操作。
    
    主要功能：
        - 元素存在性判断
        - 元素文本内容判断
        - 元素属性值判断
        - 元素位置坐标判断
        - 弹框状态判断（iOS）
        - 自定义条件判断
    
    使用场景：
        - 条件分支控制（if-else逻辑）
        - 循环控制条件
        - 动态测试流程
        - 环境状态检查
        - 业务逻辑验证
    
    Note:
        - 所有方法返回(result, msg)元组
        - result为布尔值，表示条件是否满足
        - msg为描述信息，说明判断结果
        - 支持多种比较操作符
        - 异常会向上抛出，需要调用方处理
    """

    def condition_ele_exists(self, element, assertion, expect):
        """
        判断元素存在性
        
        检查指定元素是否存在于当前界面中。
        
        Args:
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 判断操作符
                支持的操作符："=="、"!="等
            expect (bool): 期望值
                True表示期望元素存在，False表示期望元素不存在
        
        Returns:
            tuple: (result, msg)
                result (bool): 判断结果，True表示条件满足，False表示条件不满足
                msg (str): 判断结果描述信息
        
        Raises:
            Exception: 当元素查找失败时抛出
        
        Note:
            - 使用元素的exists属性进行判断
            - 不会等待元素出现，立即返回当前状态
            - 适用于Android和iOS平台
            - 常用于条件分支控制
        
        使用场景：
            - 检查可选元素是否存在
            - 条件分支控制
            - 界面状态判断
            - 动态元素检测
        
        使用示例：
            >>> # 判断登录按钮是否存在
            >>> result, msg = condition.condition_ele_exists({"id": "login_btn"}, "==", True)
            >>> if result:
            >>>     # 执行登录操作
            >>>     pass
            >>> 
            >>> # 判断错误提示是否不存在
            >>> result, msg = condition.condition_ele_exists({"text": "错误"}, "==", False)
        """
        try:
            # 获取元素的存在状态
            actual = self.find_element(element).exists
            self.test.debugLog("成功获取元素exists:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素exists")
            raise e
        else:
            # 执行条件判断
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_text(self, system, element, assertion, expect):
        """
        判断元素文本内容
        
        检查指定元素的文本内容是否符合条件。
        
        Args:
            system (str): 操作系统类型（"android" 或 "ios"）
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 判断操作符
                支持的操作符："=="、"!="、"in"、"not in"、"startswith"、"endswith"等
            expect (str): 期望的文本内容
        
        Returns:
            tuple: (result, msg)
                result (bool): 判断结果，True表示条件满足，False表示条件不满足
                msg (str): 判断结果描述信息
        
        Raises:
            Exception: 当元素不存在或文本获取失败时抛出
        
        Note:
            - Android使用get_text()方法获取文本
            - iOS使用text属性获取文本
            - 获取的是元素的可见文本内容
            - 支持多种文本比较方式
            - 文本比较通常区分大小写
        
        使用场景：
            - 验证动态文本内容
            - 检查状态文本
            - 条件分支控制
            - 文本内容验证
            - 多语言适配检查
        
        使用示例：
            >>> # 判断按钮文本是否为"登录"
            >>> result, msg = condition.condition_ele_text("android", {"id": "btn"}, "==", "登录")
            >>> 
            >>> # 判断状态文本是否包含"成功"
            >>> result, msg = condition.condition_ele_text("ios", {"name": "status"}, "in", "成功")
            >>> 
            >>> # 判断错误信息是否以"错误"开头
            >>> result, msg = condition.condition_ele_text("android", {"id": "error"}, "startswith", "错误")
        """
        try:
            if system == "android":
                # Android：使用get_text()方法获取元素文本
                actual = self.find_element(element).get_text()
            else:
                # iOS：使用text属性获取元素文本
                actual = self.find_element(element).text
            self.test.debugLog("成功获取元素text:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素text")
            raise e
        else:
            # 执行条件判断
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_attribute(self, element, attribute, assertion, expect):
        """判断元素属性"""
        try:
            actual = self.find_element(element).info[attribute]
            self.test.debugLog("成功获取元素%s属性:%s" % (attribute, str(actual)))
        except Exception as e:
            self.test.errorLog("无法获取元素%s属性" % attribute)
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_center(self, system, element, assertion, expect):
        """判断元素位置"""
        try:
            if system == "android":
                x, y = self.find_element(element).center()
                actual = (x, y)
            else:
                size = self.find_element(element).bounds
                actual = (size.x, size.y)
            self.test.debugLog("成功获取元素位置:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素位置")
            raise e
        else:
            result, msg = LMAssert(assertion, str(actual), expect).compare()
            return result, msg

    def condition_ele_x(self, system, element, assertion, expect):
        """判断元素X坐标"""
        try:
            if system == "android":
                x, y = self.find_element(element).center()
                actual = x
            else:
                x, y = self.find_element(element).bounds.center
                actual = x
            self.test.debugLog("成功获取元素X坐标:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素X坐标")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_y(self, system, element, assertion, expect):
        """判断元素Y坐标"""
        try:
            if system == "android":
                x, y = self.find_element(element).center()
                actual = y
            else:
                x, y = self.find_element(element).bounds.center
                actual = y
            self.test.debugLog("成功获取元素Y坐标:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素Y坐标")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_alert_exists(self, assertion, expect):
        """判断弹框存在 IOS专属"""
        try:
            actual = self.device.alert.exists
            self.test.debugLog("成功获取弹框exists:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取弹框exists")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_alert_text(self, assertion, expect):
        """判断弹框文本 IOS专属"""
        try:
            actual = self.device.alert.text
            self.test.debugLog("成功获取弹框文本:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取弹框文本")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def custom(self, **kwargs):
        """自定义"""
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["device"] = self.device
        names["test"] = self.test
        try:
            """条件操作需要返回被判断的值 以sys_return(value)返回"""
            def print(*args, sep=' ', end='\n', file=None, flush=False):
                if file is None or file in (sys.stdout, sys.stderr):
                    file = names["test"].stdout_buffer
                self.print(*args, sep=sep, end=end, file=file, flush=flush)

            def sys_return(res):
                names["_exec_result"] = res

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
        except UiObjectNotFoundError as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
        else:
            result, msg = LMAssert(kwargs["data"]["assertion"], names["_exec_result"], kwargs["data"]["expect"]).compare()
            return result, msg

