import sys
from uiautomator2 import UiObjectNotFoundError
from core.assertion import LMAssert
from core.app.device import Operation


class Assertion(Operation):
    """
    断言类操作
    
    提供各种UI元素和系统状态的断言功能，用于自动化测试中的验证操作。
    继承自Operation基类，具备元素查找和设备操作能力。
    
    主要功能：
        - 元素存在性断言
        - 元素文本内容断言
        - 元素属性值断言
        - 元素位置坐标断言
        - 弹框状态断言（iOS专属）
        - 自定义断言逻辑
    
    支持的断言类型：
        - 相等性断言（==、!=）
        - 包含性断言（in、not in）
        - 比较断言（>、<、>=、<=）
        - 正则表达式匹配
        - 自定义断言逻辑
    
    平台兼容性：
        - Android：支持所有断言功能
        - iOS：支持所有断言功能，额外支持弹框断言
    
    使用示例：
        >>> assertion = Assertion(device, test)
        >>> result, msg = assertion.assert_ele_exists({"text": "登录"}, "==", True)
        >>> result, msg = assertion.assert_ele_text("android", {"id": "username"}, "==", "admin")
    """

    def assert_ele_exists(self, element, assertion, expect):
        """
        断言元素存在
        
        验证指定元素是否存在于当前界面中。
        
        Args:
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "登录", "resourceId": "com.app:id/login"}
                - XPath定位：{"xpath": "//button[@text='登录']"}
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、"in"、"not in"等
            expect (bool): 期望值
                True表示期望元素存在，False表示期望元素不存在
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素定位失败或断言执行异常时抛出
        
        Note:
            - 两个平台通用
            - 使用exists属性检查元素存在性
            - 不会等待元素出现，仅检查当前状态
            - 常用于验证界面跳转和元素显示状态
        
        使用场景：
            - 验证登录后是否显示用户信息
            - 检查错误提示是否出现
            - 确认按钮是否可见
            - 验证界面元素加载状态
        
        使用示例：
            >>> # 验证登录按钮存在
            >>> result, msg = assertion.assert_ele_exists({"text": "登录"}, "==", True)
            >>> 
            >>> # 验证错误提示不存在
            >>> result, msg = assertion.assert_ele_exists({"id": "error_msg"}, "==", False)
        """
        try:
            # 获取元素的存在状态
            actual = self.find_element(element).exists
            self.test.debugLog("成功获取元素exists:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素exists")
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_text(self, system, element, assertion, expect):
        """
        断言元素文本
        
        验证指定元素的文本内容是否符合期望。
        
        Args:
            system (str): 操作系统类型（"android" 或 "ios"）
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、"in"、"not in"、"startswith"、"endswith"等
            expect (str): 期望的文本内容
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素不存在或文本获取失败时抛出
        
        Note:
            - Android使用get_text()方法获取文本
            - iOS使用text属性获取文本
            - 获取的是元素的显示文本，不包括隐藏文本
            - 对于输入框，获取的是当前输入的内容
        
        使用场景：
            - 验证按钮文本是否正确
            - 检查标签显示内容
            - 确认输入框的默认值
            - 验证错误提示信息
            - 检查动态更新的文本内容
        
        使用示例：
            >>> # 验证按钮文本
            >>> result, msg = assertion.assert_ele_text("android", {"id": "submit"}, "==", "提交")
            >>> 
            >>> # 验证文本包含特定内容
            >>> result, msg = assertion.assert_ele_text("ios", {"name": "title"}, "in", "欢迎")
            >>> 
            >>> # 验证错误信息
            >>> result, msg = assertion.assert_ele_text("android", {"id": "error"}, "==", "用户名不能为空")
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
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_attribute(self, element, attribute, assertion, expect):
        """
        断言元素属性
        
        验证指定元素的特定属性值是否符合期望。
        
        Args:
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            attribute (str): 要检查的属性名称
                常用属性："text"、"resourceId"、"className"、"enabled"、"selected"、
                "checked"、"clickable"、"bounds"、"contentDescription"等
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、"in"、"not in"、">"、"<"等
            expect (any): 期望的属性值
                类型取决于具体属性，可以是字符串、布尔值、数字等
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素不存在或属性获取失败时抛出
            KeyError: 当指定的属性不存在时抛出
        
        Note:
            - 使用元素的info属性获取详细信息
            - 不同平台的属性名称可能有差异
            - 属性值的类型和格式可能因平台而异
            - 某些属性可能在特定状态下才可用
        
        使用场景：
            - 验证元素的启用/禁用状态
            - 检查复选框的选中状态
            - 确认元素的类名或ID
            - 验证元素的可点击性
            - 检查元素的边界信息
        
        使用示例：
            >>> # 验证按钮是否可点击
            >>> result, msg = assertion.assert_ele_attribute({"id": "submit"}, "clickable", "==", True)
            >>> 
            >>> # 验证复选框是否选中
            >>> result, msg = assertion.assert_ele_attribute({"id": "checkbox"}, "checked", "==", True)
            >>> 
            >>> # 验证元素类名
            >>> result, msg = assertion.assert_ele_attribute({"text": "登录"}, "className", "==", "android.widget.Button")
        """
        try:
            # 获取元素的指定属性值
            actual = self.find_element(element).info[attribute]
            self.test.debugLog("成功获取元素%s属性:%s" % (attribute, str(actual)))
        except Exception as e:
            self.test.errorLog("无法获取元素%s属性" % attribute)
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_center(self, system, element, assertion, expect):
        """
        断言元素位置
        
        验证指定元素的中心坐标是否符合期望。
        
        Args:
            system (str): 操作系统类型（"android" 或 "ios"）
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、"in"、"not in"等
            expect (str): 期望的坐标值（字符串格式）
                格式："(x, y)"，例如："(100, 200)"
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素不存在或坐标获取失败时抛出
        
        Note:
            - Android使用center()方法获取中心坐标
            - iOS使用bounds.center属性获取中心坐标
            - 返回的坐标是元素几何中心的屏幕坐标
            - 坐标值会转换为字符串格式进行比较
            - 坐标可能因屏幕分辨率和设备方向而变化
        
        使用场景：
            - 验证元素是否在预期位置
            - 检查布局是否正确
            - 确认元素相对位置
            - 验证动画后的元素位置
            - 检查响应式布局的适配
        
        使用示例：
            >>> # 验证按钮在特定位置
            >>> result, msg = assertion.assert_ele_center("android", {"id": "submit"}, "==", "(540, 960)")
            >>> 
            >>> # 验证元素不在某个位置
            >>> result, msg = assertion.assert_ele_center("ios", {"name": "button"}, "!=", "(0, 0)")
        """
        try:
            if system == "android":
                # Android：使用center()方法获取元素中心坐标
                x, y = self.find_element(element).center()
                actual = (x, y)
            else:
                # iOS：使用bounds.center属性获取元素中心坐标
                x, y = self.find_element(element).bounds.center
                actual = (x, y)
            self.test.debugLog("成功获取元素位置:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素位置")
            raise e
        else:
            # 执行断言比较（转换为字符串格式）
            result, msg = LMAssert(assertion, str(actual), expect).compare()
            return result, msg

    def assert_ele_x(self, system, element, assertion, expect):
        """
        断言元素X坐标
        
        验证指定元素的X坐标（水平位置）是否符合期望。
        
        Args:
            system (str): 操作系统类型（"android" 或 "ios"）
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、">"、"<"、">="、"<="等
            expect (int/float): 期望的X坐标值
                表示元素中心点的水平位置（像素值）
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素不存在或坐标获取失败时抛出
        
        Note:
            - X坐标表示元素中心点的水平位置
            - 坐标原点(0,0)通常在屏幕左上角
            - X坐标值越大，元素越靠右
            - 坐标可能因屏幕分辨率和设备方向而变化
            - 使用数值类型进行精确比较
        
        使用场景：
            - 验证元素的水平对齐
            - 检查元素是否在屏幕特定区域
            - 确认元素的水平位置关系
            - 验证响应式布局的水平适配
            - 检查动画后的水平位置
        
        使用示例：
            >>> # 验证按钮在屏幕中央（假设屏幕宽度1080）
            >>> result, msg = assertion.assert_ele_x("android", {"id": "submit"}, "==", 540)
            >>> 
            >>> # 验证元素在屏幕右半部分
            >>> result, msg = assertion.assert_ele_x("ios", {"name": "button"}, ">", 400)
            >>> 
            >>> # 验证元素不在屏幕边缘
            >>> result, msg = assertion.assert_ele_x("android", {"text": "菜单"}, ">", 50)
        """
        try:
            if system == "android":
                # Android：使用center()方法获取元素中心坐标
                x, y = self.find_element(element).center()
                actual = x
            else:
                # iOS：使用bounds.center属性获取元素中心坐标
                x, y = self.find_element(element).bounds.center
                actual = x
            self.test.debugLog("成功获取元素X坐标:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素X坐标")
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_y(self, system, element, assertion, expect):
        """
        断言元素Y坐标
        
        验证指定元素的Y坐标（垂直位置）是否符合期望。
        
        Args:
            system (str): 操作系统类型（"android" 或 "ios"）
            element (dict): 元素定位信息
                支持的定位方式：
                - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                - XPath定位：{"xpath": "//button[@id='submit']"}
            assertion (str): 断言操作符
                支持的操作符："=="、"!="、">"、"<"、">="、"<="等
            expect (int/float): 期望的Y坐标值
                表示元素中心点的垂直位置（像素值）
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当元素不存在或坐标获取失败时抛出
        
        Note:
            - Y坐标表示元素中心点的垂直位置
            - 坐标原点(0,0)通常在屏幕左上角
            - Y坐标值越大，元素越靠下
            - 坐标可能因屏幕分辨率和设备方向而变化
            - 使用数值类型进行精确比较
        
        使用场景：
            - 验证元素的垂直对齐
            - 检查元素是否在屏幕特定区域
            - 确认元素的垂直位置关系
            - 验证滚动后的元素位置
            - 检查动画后的垂直位置
        
        使用示例：
            >>> # 验证按钮在屏幕中央（假设屏幕高度1920）
            >>> result, msg = assertion.assert_ele_y("android", {"id": "submit"}, "==", 960)
            >>> 
            >>> # 验证元素在屏幕上半部分
            >>> result, msg = assertion.assert_ele_y("ios", {"name": "button"}, "<", 500)
            >>> 
            >>> # 验证元素不在状态栏区域
            >>> result, msg = assertion.assert_ele_y("android", {"text": "标题"}, ">", 100)
        """
        try:
            if system == "android":
                # Android：使用center()方法获取元素中心坐标
                x, y = self.find_element(element).center()
                actual = y
            else:
                # iOS：使用bounds.center属性获取元素中心坐标
                x, y = self.find_element(element).bounds.center
                actual = y
            self.test.debugLog("成功获取元素Y坐标:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素Y坐标")
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_alert_exists(self, assertion, expect):
        """
        断言弹框存在（iOS专属）
        
        验证系统弹框（Alert）是否存在于当前界面中。
        
        Args:
            assertion (str): 断言操作符
                支持的操作符："=="、"!="等
            expect (bool): 期望值
                True表示期望弹框存在，False表示期望弹框不存在
        
        Returns:
            tuple: (result, msg)
                result (bool): 断言结果，True表示断言通过，False表示断言失败
                msg (str): 断言结果描述信息
        
        Raises:
            Exception: 当弹框状态获取失败时抛出
        
        Note:
            - 仅适用于iOS平台
            - 检测的是系统级弹框（UIAlert）
            - 不包括自定义的弹窗组件
            - 常用于处理权限请求、确认对话框等
        
        使用场景：
            - 验证权限请求弹框是否出现
            - 检查确认对话框的显示状态
            - 确认错误提示弹框
            - 验证系统通知弹框
        
        使用示例：
            >>> # 验证弹框存在
            >>> result, msg = assertion.assert_alert_exists("==", True)
            >>> 
            >>> # 验证弹框不存在
            >>> result, msg = assertion.assert_alert_exists("==", False)
        """
        try:
            # 获取弹框的存在状态
            actual = self.device.alert.exists
            self.test.debugLog("成功获取弹框exists:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取弹框exists")
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_alert_text(self, assertion, expect):
        """
            断言弹框文本（iOS专属）
            
            验证系统弹框（Alert）的文本内容是否符合期望。
            
            Args:
                assertion (str): 断言操作符
                    支持的操作符："=="、"!="、"in"、"not in"、"startswith"、"endswith"等
                expect (str): 期望的文本内容
            
            Returns:
                tuple: (result, msg)
                    result (bool): 断言结果，True表示断言通过，False表示断言失败
                    msg (str): 断言结果描述信息
            
            Raises:
                Exception: 当弹框不存在或文本获取失败时抛出
            
            Note:
                - 仅适用于iOS平台
                - 获取的是弹框的完整文本内容
                - 包括标题和消息内容
                - 弹框必须存在才能获取文本
            
            使用场景：
                - 验证权限请求的提示文本
                - 检查确认对话框的消息内容
                - 确认错误提示的具体信息
                - 验证系统通知的文本
            
            使用示例：
                >>> # 验证弹框文本内容
                >>> result, msg = assertion.assert_alert_text("==", "允许访问相机？")
                >>> 
                >>> # 验证弹框包含特定文本
                >>> result, msg = assertion.assert_alert_text("in", "权限")
                >>> 
                >>> # 验证错误提示文本
                >>> result, msg = assertion.assert_alert_text("==", "网络连接失败")
        """
        try:
            # 获取弹框的文本内容
            actual = self.device.alert.text
            self.test.debugLog("成功获取弹框文本:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取弹框文本")
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def custom(self, **kwargs):
        """
            自定义断言
            
            执行用户自定义的Python代码进行复杂断言操作。
            
            Args:
                **kwargs: 关键字参数
                    code (str): 要执行的Python代码
                    element (dict): 元素定位信息（可选）
                    data (dict): 断言数据，包含assertion和expect字段
                    trans (str): 操作描述信息
            
            Returns:
                tuple: (result, msg)
                    result (bool): 断言结果，True表示断言通过，False表示断言失败
                    msg (str): 断言结果描述信息
            
            Raises:
                UiObjectNotFoundError: 当元素不存在时抛出
                Exception: 当代码执行失败时抛出
            
            Note:
                - 支持执行任意Python代码
                - 代码中可以使用device、test、element等预定义变量
                - 必须使用sys_return(value)返回被断言的值
                - 提供sys_get()和sys_put()函数操作公共参数和关联变量
                - 重定向print输出到测试日志
            
            可用函数：
                - sys_return(value): 返回要被断言的值
                - sys_get(name): 获取公共参数或关联变量
                - sys_put(name, value, ps=False): 设置关联变量或公共参数
                - print(): 输出日志信息
            
            可用变量：
                - device: 设备对象
                - test: 测试对象
                - element: 元素定位信息
                - data: 断言数据
            
            使用场景：
                - 复杂的业务逻辑验证
                - 多个元素的组合断言
                - 动态计算期望值
                - 自定义数据处理和验证
                - 与外部系统的集成验证
            
            使用示例：
                >>> # 自定义代码示例
                >>> code = '''
                >>> # 获取多个元素的文本并拼接
                >>> text1 = device.find_element({"id": "title"}).get_text()
                >>> text2 = device.find_element({"id": "subtitle"}).get_text()
                >>> result = text1 + " " + text2
                >>> sys_return(result)
                >>> '''
                >>> 
                >>> data = {"assertion": "==", "expect": "Hello World"}
                >>> result, msg = assertion.custom(code=code, data=data, trans="验证标题拼接")
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["device"] = self.device
        names["test"] = self.test
        try:
            """断言操作需要返回被断言的值 以sys_return(value)返回"""
            def print(*args, sep=' ', end='\n', file=None, flush=False):
                if file is None or file in (sys.stdout, sys.stderr):
                    file = names["test"].stdout_buffer
                self.print(*args, sep=sep, end=end, file=file, flush=flush)

            def sys_return(res):
                """返回要被断言的值"""
                names["_exec_result"] = res

            def sys_get(name):
                """获取公共参数或关联变量"""
                if name in names["test"].context:
                    return names["test"].context[name]
                elif name in names["test"].common_params:
                    return names["test"].common_params[name]
                else:
                    raise KeyError("不存在的公共参数或关联变量: {}".format(name))

            def sys_put(name, val, ps=False):
                """设置关联变量或公共参数"""
                if ps:
                    names["test"].common_params[name] = val
                else:
                    names["test"].context[name] = val

            # 执行用户自定义代码
            exec(code)
            self.test.debugLog("成功执行 %s" % kwargs["trans"])
        except UiObjectNotFoundError as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
        else:
            # 执行断言比较
            result, msg = LMAssert(kwargs["data"]["assertion"], names["_exec_result"], kwargs["data"]["expect"]).compare()
            return result, msg

