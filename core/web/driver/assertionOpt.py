#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web自动化测试断言操作模块

该模块提供了Web自动化测试中的各种断言操作功能，包括：
- 页面级断言：页面标题、URL、源码等
- 元素级断言：元素文本、属性、状态、位置、尺寸等
- 窗口级断言：窗口位置、大小等
- Cookie断言：Cookie值验证
- 自定义断言：支持用户自定义断言逻辑

所有断言操作都基于LMAssert断言引擎，支持多种比较方式，
并提供详细的断言结果和错误信息。
"""

import sys  # 系统模块，用于自定义断言中的参数传递

from selenium.common.exceptions import NoSuchElementException  # Selenium元素未找到异常

from core.assertion import LMAssert  # LiuMa断言引擎
from core.web.driver import Operation  # Web操作基础类


class Assertion(Operation):
    """
    Web自动化测试断言操作类
    
    提供页面、元素、窗口、Cookie等多维度的断言功能，
    所有断言方法都返回(result, msg)元组格式的结果。
    
    使用示例：
        assertion = Assertion()
        result, msg = assertion.assert_page_title('eq', '首页')
    """

    def assert_page_title(self, assertion, expect):
        """
        断言页面标题
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {str} expect - 期望的页面标题值
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前页面标题并与期望值进行比较
        
        assert_page_title('eq', '首页')
        """
        try:
            actual = self.driver.title  # 获取当前页面标题
            self.test.debugLog("成功获取title:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取title")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_page_url(self, assertion, expect):
        """
        断言页面URL
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {str} expect - 期望的页面URL值
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前页面URL并与期望值进行比较
        
        assert_page_url('contains', '/login')
        """
        try:
            actual = self.driver.current_url  # 获取当前页面URL
            self.test.debugLog("成功获取url:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取url")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_page_source(self, assertion, expect):
        """
        断言页面源码
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {str} expect - 期望的页面源码内容
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前页面HTML源码并与期望值进行比较
        
        assert_page_source('contains', '<div class="content">')
        """
        try:
            actual = self.driver.page_source  # 获取页面HTML源码
            self.test.debugLog("成功获取page source: 源码过长不予展示")
        except Exception as e:
            self.test.errorLog("无法获取page source")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_text(self, element, assertion, expect):
        """
        断言元素文本内容
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {str} expect - 期望的元素文本内容
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的文本内容并与期望值进行比较
        
        assert_ele_text(('id', 'username'), 'eq', '用户名')
        """
        try:
            actual = self.find_element(element).text  # 获取元素文本内容
            self.test.debugLog("成功获取元素text:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素text")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_tag(self, element, assertion, expect):
        """
        断言元素标签名
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {str} expect - 期望的元素标签名
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的HTML标签名并与期望值进行比较
        
        assert_ele_tag(('id', 'submit'), 'eq', 'button')
        """
        try:
            actual = self.find_element(element).tag_name  # 获取元素标签名
            self.test.debugLog("成功获取元素tag name:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素tag name")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_size(self, element, assertion, expect):
        """
        断言元素尺寸
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/regex等）
        @param {dict} expect - 期望的元素尺寸，格式为{'width': 宽度, 'height': 高度}
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的尺寸信息并与期望值进行比较
        
        assert_ele_size(('id', 'banner'), 'eq', {'width': 800, 'height': 200})
        """
        try:
            actual = self.find_element(element).size  # 获取元素尺寸信息
            self.test.debugLog("成功获取元素size:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素size")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_height(self, element, assertion, expect):
        """
        断言元素高度
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int/float} expect - 期望的元素高度值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的高度值并与期望值进行比较
        
        assert_ele_height(('id', 'banner'), 'ge', 200)
        """
        try:
            actual = self.find_element(element).size.get("height")  # 获取元素高度
            self.test.debugLog("成功获取元素height:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素height")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_width(self, element, assertion, expect):
        """
        断言元素宽度
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int/float} expect - 期望的元素宽度值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的宽度值并与期望值进行比较
        
        assert_ele_width(('id', 'banner'), 'eq', 800)
        """
        try:
            actual = self.find_element(element).size.get("width")  # 获取元素宽度
            self.test.debugLog("成功获取元素width:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素width")
            raise e
        else:
            # 使用LMAssert进行断言比较
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_location(self, element, assertion, expect):
        """
        断言元素位置
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {dict} expect - 期望的元素位置，格式为{'x': X坐标, 'y': Y坐标}
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素在页面中的位置坐标并与期望值进行比较
        
        assert_ele_location(('id', 'logo'), 'eq', {'x': 100, 'y': 50})
        """
        try:
            actual = self.find_element(element).location
            self.test.debugLog("成功获取元素location:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素location")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_x(self, element, assertion, expect):
        """
        断言元素X坐标
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {int} expect - 期望的X坐标值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素在页面中的X坐标并与期望值进行比较
        
        assert_ele_x(('id', 'logo'), 'eq', 100)
        """
        try:
            actual = self.find_element(element).location.get("x")
            self.test.debugLog("成功获取元素location x:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素location x")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_y(self, element, assertion, expect):
        """
        断言元素Y坐标
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {int} expect - 期望的Y坐标值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素在页面中的Y坐标并与期望值进行比较
        
        assert_ele_y(('id', 'logo'), 'eq', 50)
        """
        try:
            actual = self.find_element(element).location.get("y")
            self.test.debugLog("成功获取元素location y:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素location y")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_attribute(self, element, name, assertion, expect):
        """
        断言元素属性
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} name - 要获取的属性名称（如id、class、value、href等）
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {str} expect - 期望的属性值
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的指定属性值并与期望值进行比较
        
        assert_ele_attribute(('id', 'link'), 'href', 'contains', 'example.com')
        """
        try:
            actual = self.find_element(element).get_attribute(name)
            self.test.debugLog("成功获取元素attribute:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素attribute")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_selected(self, element, assertion, expect):
        """
        断言元素选中状态
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne等）
        @param {bool} expect - 期望的选中状态，True表示选中，False表示未选中
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的选中状态并与期望值进行比较，主要用于复选框、单选按钮等
        
        assert_ele_selected(('id', 'checkbox1'), 'eq', True)
        """
        try:
            actual = self.find_element(element).is_selected()
            self.test.debugLog("成功获取元素selected:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素selected")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_enabled(self, element, assertion, expect):
        """
        断言元素启用状态
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne等）
        @param {bool} expect - 期望的启用状态，True表示启用，False表示禁用
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的启用状态并与期望值进行比较，主要用于表单元素的可用性验证
        
        assert_ele_enabled(('id', 'submit_btn'), 'eq', True)
        """
        try:
            actual = self.find_element(element).is_enabled()
            self.test.debugLog("成功获取元素enabled:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素enabled")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_displayed(self, element, assertion, expect):
        """
        断言元素显示状态
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne等）
        @param {bool} expect - 期望的显示状态，True表示显示，False表示隐藏
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的显示状态并与期望值进行比较，验证元素的可见性
        
        assert_ele_displayed(('id', 'modal'), 'eq', True)
        """
        try:
            actual = self.find_element(element).is_displayed()
            self.test.debugLog("成功获取元素displayed:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素displayed")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_css(self, element, name, assertion, expect):
        """
        断言元素CSS样式
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} name - 要获取的CSS属性名称（如color、background-color、font-size等）
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {str} expect - 期望的CSS属性值
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定元素的指定CSS属性值并与期望值进行比较
        
        assert_ele_css(('id', 'title'), 'color', 'contains', 'rgb(255, 0, 0)')
        """
        try:
            actual = self.find_element(element).value_of_css_property(name)
            self.test.debugLog("成功获取元素css %s:%s" % (name, str(actual)))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素css %s" % name)
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_ele_existed(self, element, assertion, expect):
        """
        断言元素存在性
        
        @param {tuple} element - 元素定位信息，格式为(定位方式, 定位值)
        @param {str} assertion - 断言类型（eq/ne等）
        @param {bool} expect - 期望的存在状态，True表示存在，False表示不存在
        @return {tuple} (result, msg) 断言结果和描述信息
        检查指定元素是否存在于DOM中并与期望值进行比较
        
        assert_ele_existed(('id', 'dynamic_content'), 'eq', True)
        """
        try:
            try:
                self.find_elements(element)
                actual = True
            except NoSuchElementException:
                actual = False
            self.test.debugLog("成功获取元素existed:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取元素existed")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_position(self, assertion, expect):
        """
        断言窗口位置
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {dict} expect - 期望的窗口位置，格式为{'x': X坐标, 'y': Y坐标}
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的位置坐标并与期望值进行比较
        
        assert_window_position('eq', {'x': 100, 'y': 50})
        """
        try:
            actual = self.driver.get_window_position()
            self.test.debugLog("成功获取窗口position:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_x(self, assertion, expect):
        """
        断言窗口X坐标
        
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int} expect - 期望的X坐标值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的X坐标并与期望值进行比较
        
        assert_window_x('eq', 100)
        """
        try:
            actual = self.driver.get_window_position().get("x")
            self.test.debugLog("成功获取窗口position x:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position x")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_y(self, assertion, expect):
        """
        断言窗口Y坐标
        
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int} expect - 期望的Y坐标值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的Y坐标并与期望值进行比较
        
        assert_window_y('eq', 50)
        """
        try:
            actual = self.driver.get_window_position().get("y")
            self.test.debugLog("成功获取窗口position y:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position y")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_size(self, assertion, expect):
        """
        断言窗口尺寸
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {dict} expect - 期望的窗口尺寸，格式为{'width': 宽度, 'height': 高度}
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的尺寸信息并与期望值进行比较
        
        assert_window_size('eq', {'width': 1920, 'height': 1080})
        """
        try:
            actual = self.driver.get_window_size()
            self.test.debugLog("成功获取窗口size:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口size")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_width(self, assertion, expect):
        """
        断言窗口宽度
        
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int} expect - 期望的窗口宽度值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的宽度值并与期望值进行比较
        
        assert_window_width('eq', 1920)
        """
        try:
            actual = self.driver.get_window_size().get("width")
            self.test.debugLog("成功获取窗口width:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口width")
            raise e        
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_window_height(self, assertion, expect):
        """
        断言窗口高度
        
        @param {str} assertion - 断言类型（eq/ne/gt/lt/ge/le等）
        @param {int} expect - 期望的窗口高度值（像素）
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前浏览器窗口的高度值并与期望值进行比较
        
        assert_window_height('eq', 1080)
        """
        try:
            actual = self.driver.get_window_size().get("height")
            self.test.debugLog("成功获取窗口height:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口height")
            raise e        
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_cookies(self, assertion, expect):
        """
        断言所有Cookies
        
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains等）
        @param {list} expect - 期望的Cookie列表，每个Cookie为字典格式
        @return {tuple} (result, msg) 断言结果和描述信息
        获取当前页面的所有Cookie信息并与期望值进行比较
        
        assert_cookies('contains', [{'name': 'session_id', 'value': 'abc123'}])
        """
        try:
            actual = self.driver.get_cookies()
            self.test.debugLog("成功获取cookies:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取cookies")
            raise e        
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def assert_cookie(self, name, assertion, expect):
        """
        断言指定Cookie
        
        @param {str} name - Cookie的名称
        @param {str} assertion - 断言类型（eq/ne/contains/not_contains/is_none/is_not_none等）
        @param {dict/None} expect - 期望的Cookie信息，包含name、value、domain等属性
        @return {tuple} (result, msg) 断言结果和描述信息
        获取指定名称的Cookie信息并与期望值进行比较
        
        assert_cookie('session_id', 'eq', {'name': 'session_id', 'value': 'abc123'})
        """
        try:
            actual = self.driver.get_cookie(name)
            self.test.debugLog("成功获取cookie %s:%s" % (name, str(actual)))
        except Exception as e:
            self.test.errorLog("无法获取cookie %s" % name)
            raise e        
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def custom(self, **kwargs):
        """
        自定义断言操作
        
        @param {dict} kwargs - 关键字参数，包含code、element、data、trans等字段
        @return {tuple} (result, msg) 断言结果和描述信息
        执行用户自定义的Python代码来实现特殊的断言逻辑
        
        支持的内置函数：
        - print(*args): 输出信息到测试日志
        - sys_return(value): 返回要被断言的值（必须调用）
        - sys_get(name): 获取公共参数或关联变量
        - sys_put(name, value, ps=False): 设置关联变量或公共参数
        
        ⚠️ 安全警告：该方法会执行任意Python代码，存在安全风险！
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["driver"] = self.driver
        names["test"] = self.test
        try:
            """断言操作需要返回被断言的值 以sys_return(value)返回"""
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
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
        else:
            result, msg = LMAssert(kwargs["data"]["assertion"], names["_exec_result"], kwargs["data"]["expect"]).compare()
            return result, msg

