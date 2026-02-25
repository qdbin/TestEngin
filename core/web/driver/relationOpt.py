# -*- coding: utf-8 -*-
"""
    Web关联操作模块
    
    提供Web自动化测试中的数据提取和关联操作功能。
"""

import sys

from selenium.common.exceptions import NoSuchElementException

from core.web.driver import Operation


class Relation(Operation):
    """Web关联操作类，用于提取页面、元素、窗口等信息并保存到测试上下文中"""
    def get_page_title(self, save_name):
        """
        获取当前页面标题并保存到指定变量
        
        @param save_name: 保存标题的变量名
        @raises Exception: 获取标题失败时抛出异常
        
        Example:
            relation.get_page_title("page_title")
        """
        try:
            actual = self.driver.title
            self.test.debugLog("成功获取title:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取title")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_page_url(self, save_name):
        """
        获取当前页面URL并保存到指定变量
        
        @param save_name: 保存URL的变量名
        @raises Exception: 获取URL失败时抛出异常
        
        Example:
            relation.get_page_url("current_url")
        """
        try:
            actual = self.driver.current_url
            self.test.debugLog("成功获取url:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取url")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_text(self, element, save_name):
        """
        获取指定元素的文本内容并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存文本的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取文本失败时抛出异常
        
        Example:
            relation.get_ele_text({"by": "id", "value": "username"}, "user_text")
        """
        try:
            actual = self.find_element(element).text
            self.test.debugLog("成功获取元素text:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素text")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_tag(self, element, save_name):
        """
        获取指定元素的标签名并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存标签名的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取标签名失败时抛出异常
        
        Example:
            relation.get_ele_tag({"by": "id", "value": "submit"}, "tag_name")
        """
        try:
            actual = self.find_element(element).tag_name
            self.test.debugLog("成功获取元素tag name:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素tag name")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_size(self, element, save_name):
        """
        获取指定元素的尺寸信息并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存尺寸信息的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取尺寸失败时抛出异常
        
        Example:
            relation.get_ele_size({"by": "class", "value": "button"}, "element_size")
        """
        try:
            actual = self.find_element(element).size
            self.test.debugLog("成功获取元素size:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素size")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_height(self, element, save_name):
        """
        获取指定元素的高度并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存高度的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取高度失败时抛出异常
        
        Example:
            relation.get_ele_height({"by": "id", "value": "content"}, "element_height")
        """
        try:
            actual = self.find_element(element).size.get("height")
            self.test.debugLog("成功获取元素height:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素height")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_width(self, element, save_name):
        """
        获取指定元素的宽度并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存宽度的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取宽度失败时抛出异常
        
        Example:
            relation.get_ele_width({"by": "name", "value": "search"}, "element_width")
        """
        try:
            actual = self.find_element(element).size.get("width")
            self.test.debugLog("成功获取元素width:%s" % str(actual))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法获取元素width")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_ele_location(self, element, save_name):
        """
        获取指定元素的位置坐标并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存位置坐标的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取位置失败时抛出异常
        
        Example:
            relation.get_ele_location({"by": "xpath", "value": "//button"}, "button_location")
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
            self.test.context[save_name] = actual

    def get_ele_x(self, element, save_name):
        """
        获取指定元素的X坐标并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存X坐标的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取X坐标失败时抛出异常
        
        Example:
            relation.get_ele_x({"by": "id", "value": "menu"}, "menu_x")
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
            self.test.context[save_name] = actual

    def get_ele_y(self, element, save_name):
        """
        获取指定元素的Y坐标并保存到指定变量
        
        @param element: 元素定位信息
        @param save_name: 保存Y坐标的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取Y坐标失败时抛出异常
        
        Example:
            relation.get_ele_y({"by": "class", "value": "header"}, "header_y")
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
            self.test.context[save_name] = actual

    def get_ele_attribute(self, element, name, save_name):
        """
        获取指定元素的属性值并保存到指定变量
        
        @param element: 元素定位信息
        @param name: 属性名称
        @param save_name: 保存属性值的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取属性失败时抛出异常
        
        Example:
            relation.get_ele_attribute({"by": "id", "value": "link"}, "href", "link_url")
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
            self.test.context[save_name] = actual

    def get_ele_css(self, element, name, save_name):
        """
        获取指定元素的CSS样式属性值并保存到指定变量
        
        @param element: 元素定位信息
        @param name: CSS属性名称
        @param save_name: 保存CSS属性值的变量名
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 获取CSS属性失败时抛出异常
        
        Example:
            relation.get_ele_css({"by": "id", "value": "button"}, "color", "button_color")
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
            self.test.context[save_name] = actual

    def get_window_position(self, save_name):
        """
        获取浏览器窗口位置并保存到指定变量
        
        @param save_name: 保存窗口位置的变量名
        @raises Exception: 获取窗口位置失败时抛出异常
        
        Example:
            relation.get_window_position("window_pos")
        """
        try:
            actual = self.driver.get_window_position()
            self.test.debugLog("成功获取窗口position:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_window_x(self, save_name):
        """
        获取浏览器窗口X坐标并保存到指定变量
        
        @param save_name: 保存窗口X坐标的变量名
        @raises Exception: 获取窗口X坐标失败时抛出异常
        
        Example:
            relation.get_window_x("window_x")
        """
        try:
            actual = self.driver.get_window_position().get("x")
            self.test.debugLog("成功获取窗口position x:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position x")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_window_y(self, save_name):
        """
        获取浏览器窗口Y坐标并保存到指定变量
        
        @param save_name: 保存窗口Y坐标的变量名
        @raises Exception: 获取窗口Y坐标失败时抛出异常
        
        Example:
            relation.get_window_y("window_y")
        """
        try:
            actual = self.driver.get_window_position().get("y")
            self.test.debugLog("成功获取窗口position y:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口position y")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_window_size(self, save_name):
        """
        获取浏览器窗口大小并保存到指定变量
        
        @param save_name: 保存窗口大小的变量名
        @raises Exception: 获取窗口大小失败时抛出异常
        
        Example:
            relation.get_window_size("window_size")
        """
        try:
            actual = self.driver.get_window_size()
            self.test.debugLog("成功获取窗口size:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口size")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_window_width(self, save_name):
        """
        获取浏览器窗口宽度并保存到指定变量
        
        @param save_name: 保存窗口宽度的变量名
        @raises Exception: 获取窗口宽度失败时抛出异常
        
        Example:
            relation.get_window_width("window_width")
        """
        try:
            actual = self.driver.get_window_size().get("width")
            self.test.debugLog("成功获取窗口width:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口width")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_window_height(self, save_name):
        """
        获取浏览器窗口高度并保存到指定变量
        
        @param save_name: 保存窗口高度的变量名
        @raises Exception: 获取窗口高度失败时抛出异常
        
        Example:
            relation.get_window_height("window_height")
        """
        try:
            actual = self.driver.get_window_size().get("height")
            self.test.debugLog("成功获取窗口height:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取窗口height")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_current_handle(self, save_name):
        """
        获取当前浏览器窗口句柄并保存到指定变量
        
        @param save_name: 保存当前窗口句柄的变量名
        @raises Exception: 获取当前窗口句柄失败时抛出异常
        
        Example:
            relation.get_current_handle("current_handle")
        """
        try:
            actual = self.driver.current_window_handle
            self.test.debugLog("成功获取当前窗口handle:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取当前窗口handle")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_all_handle(self, save_name):
        """
        获取所有浏览器窗口句柄并保存到指定变量
        
        @param save_name: 保存所有窗口句柄的变量名
        @raises Exception: 获取所有窗口句柄失败时抛出异常
        
        Example:
            relation.get_all_handle("all_handles")
        """
        try:
            actual = self.driver.window_handles
            self.test.debugLog("成功获取所有窗口handle:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取所有窗口handle")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_cookies(self, save_name):
        """
        获取所有cookies并保存到指定变量
        
        @param save_name: 保存cookies的变量名
        @raises Exception: 获取cookies失败时抛出异常
        
        Example:
            relation.get_cookies("all_cookies")
        """
        try:
            actual = self.driver.get_cookies()
            self.test.debugLog("成功获取cookies:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取cookies")
            raise e
        else:
            self.test.context[save_name] = actual

    def get_cookie(self, name, save_name):
        """
        获取指定名称的cookie并保存到指定变量
        
        @param name: cookie名称
        @param save_name: 保存cookie的变量名
        @raises Exception: 获取cookie失败时抛出异常
        
        Example:
            relation.get_cookie("session_id", "session_cookie")
        """
        try:
            actual = self.driver.get_cookie(name)
            self.test.debugLog("成功获取cookie %s:%s" % (name, str(actual)))
        except Exception as e:
            self.test.errorLog("无法获取cookie:%s" % name)
            raise e
        else:
            self.test.context[save_name] = actual

    def custom(self, **kwargs):
        """
        执行自定义代码并保存结果到指定变量
        
        @param kwargs: 包含自定义代码和相关参数的字典
        @raises NoSuchElementException: 元素未找到时抛出异常
        @raises Exception: 执行自定义代码失败时抛出异常
        
        Example:
            relation.custom(code="return element.text", element={"by": "id", "value": "text"}, data={"save_name": "element_text"})
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["driver"] = self.driver
        names["test"] = self.test
        try:
            """关联操作需要返回被断言的值 以sys_return(value)返回"""

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
            self.test.context[kwargs["data"]["save_name"]] = names["_exec_result"]

