# -*- coding: utf-8 -*-
"""条件判断操作模块

提供页面、元素、窗口、Cookie等条件检查功能。
"""

import sys  # 系统模块
import selenium  # Selenium WebDriver
from selenium.common.exceptions import NoSuchElementException  # 元素未找到异常
from core.assertion import LMAssert  # 断言处理类
from core.web.driver import Operation  # 基础操作类


class Condition(Operation):
    """
    条件判断操作类
    
    主要功能:
    - 页面条件检查（标题、URL、源码）
    - 元素条件检查（文本、属性、状态）
    - 窗口条件检查（位置、大小）
    - Cookie条件检查
    """

    def condition_page_title(self, assertion, expect):
        """
        判断页面标题是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的页面标题值或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取页面标题时抛出
        
        使用示例:
            result, msg = condition.condition_page_title('=', '首页')
            result, msg = condition.condition_page_title('in', '管理系统')
        """
        try:
            actual = self.driver.title
            self.test.debugLog("成功获取title:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取title")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_page_url(self, assertion, expect):
        """
        判断页面URL是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的URL值或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取页面URL时抛出
        
        使用示例:
            result, msg = condition.condition_page_url('=', 'https://example.com/login')
            result, msg = condition.condition_page_url('in', '/dashboard')
        """
        try:
            actual = self.driver.current_url
            self.test.debugLog("成功获取url:%s" % str(actual))
        except Exception as e:
            self.test.errorLog("无法获取url")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_page_source(self, assertion, expect):
        """
        判断页面源码是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的源码内容或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取页面源码时抛出
        
        使用示例:
            result, msg = condition.condition_page_source('in', '<div class="content">')
            result, msg = condition.condition_page_source('not in', 'error')
        """
        try:
            actual = self.driver.page_source
            self.test.debugLog("成功获取page source: : 源码过长不予展示")
        except Exception as e:
            self.test.errorLog("无法获取page source")
            raise e
        else:
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_text(self, element, assertion, expect):
        """
        判断元素文本内容是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的文本内容或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素文本时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'username'}
            result, msg = condition.condition_ele_text(element, '=', '用户名')
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
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_tag(self, element, assertion, expect):
        """
        判断元素标签名是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的标签名或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
                
        Raises:
            NoSuchElementException: 当找不到指定元素时抛出
            Exception: 当无法获取元素标签名时抛出异常
            
        Example:
            >>> element = {'by': 'id', 'value': 'submit-btn'}
            >>> result, msg = condition.condition_ele_tag(element, '=', 'button')
            >>> result, msg = condition.condition_ele_tag(element, 'in', 'input')
            
        Note:
            - 返回的标签名始终为小写字母
            - 常见标签名：div, span, input, button, a, img, table等
            - 可用于验证元素类型是否符合预期
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
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_size(self, element, assertion, expect):
        """
        判断元素尺寸是否满足指定条件
        
        获取指定元素的尺寸信息（宽度和高度），并根据断言类型和期望值进行条件判断。
        常用于验证元素显示大小、响应式布局检查等。
        
        Args:
            element (dict): 元素定位信息，包含定位方式和定位值
            assertion (str): 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
            expect (dict): 期望的尺寸值，格式为 {'width': 宽度, 'height': 高度}
            
        Returns:
            tuple: (result, msg)
                - result (bool): 条件判断结果，True表示满足条件，False表示不满足
                - msg (str): 详细的判断结果描述信息
                
        Raises:
            NoSuchElementException: 当找不到指定元素时抛出
            Exception: 当无法获取元素尺寸时抛出异常
            
        Example:
            >>> element = {'by': 'id', 'value': 'banner'}
            >>> result, msg = condition.condition_ele_size(element, '=', {'width': 800, 'height': 200})
            >>> result, msg = condition.condition_ele_size(element, '>', {'width': 500, 'height': 100})
            
        Note:
            - 返回的尺寸单位为像素(px)
            - 对于隐藏元素，尺寸可能为0
            - 尺寸包括元素的padding和border，但不包括margin
            - 可用于验证响应式设计的正确性
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
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_height(self, element, assertion, expect):
        """
        判断元素高度是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的高度值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素高度时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'header'}
            result, msg = condition.condition_ele_height(element, '=', 80)
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
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_width(self, element, assertion, expect):
        """
        判断元素宽度是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的宽度值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素宽度时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'sidebar'}
            result, msg = condition.condition_ele_width(element, '=', 200)
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
            result, msg = LMAssert(assertion, actual, expect).compare()
            return result, msg

    def condition_ele_location(self, element, assertion, expect):
        """
        判断元素位置是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的位置值，格式为 {'x': X坐标, 'y': Y坐标}
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素位置时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'logo'}
            result, msg = condition.condition_ele_location(element, '=', {'x': 10, 'y': 20})
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

    def condition_ele_x(self, element, assertion, expect):
        """
        判断元素X坐标是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的X坐标值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素X坐标时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'menu'}
            result, msg = condition.condition_ele_x(element, '=', 100)
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

    def condition_ele_y(self, element, assertion, expect):
        """
        判断元素Y坐标是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的Y坐标值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素Y坐标时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'footer'}
            result, msg = condition.condition_ele_y(element, '=', 800)

            - 坐标值从页面顶部开始计算，向下递增
            - 可用于验证元素的垂直对齐和布局
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

    def condition_ele_attribute(self, element, name, assertion, expect):
        """
        判断元素属性值是否满足指定条件
        
        获取指定元素的指定属性值，并根据断言类型和期望值进行条件判断。
        常用于验证元素属性设置、状态检查等。
        
        Args:
            element (dict): 元素定位信息，包含定位方式和定位值
            name (str): 要获取的属性名称
            assertion (str): 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
            expect (str): 期望的属性值或匹配模式
            
        Returns:
            tuple: (result, msg)
                - result (bool): 条件判断结果，True表示满足条件，False表示不满足
                - msg (str): 详细的判断结果描述信息
                
        Raises:
            NoSuchElementException: 当找不到指定元素时抛出
            Exception: 当无法获取元素属性时抛出异常
            
        Example:
            >>> element = {'by': 'id', 'value': 'username'}
            >>> result, msg = condition.condition_ele_attribute(element, 'placeholder', '=', '请输入用户名')
            >>> result, msg = condition.condition_ele_attribute(element, 'class', 'in', 'form-control')
            
        Note:
            - 如果属性不存在，返回None
            - 常用属性包括：id, class, name, value, href, src, title等
            - 布尔属性（如disabled, checked）返回字符串'true'或None
            - 可用于验证元素配置和状态
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

    def condition_ele_selected(self, element, assertion, expect):
        """
        判断元素选中状态是否满足指定条件
        
        获取指定元素的选中状态，并根据断言类型和期望值进行条件判断。
        主要用于复选框(checkbox)、单选按钮(radio)、下拉选项(option)等可选择元素。
        
        Args:
            element (dict): 元素定位信息，包含定位方式和定位值
            assertion (str): 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
            expect (bool): 期望的选中状态，True表示选中，False表示未选中
            
        Returns:
            tuple: (result, msg)
                - result (bool): 条件判断结果，True表示满足条件，False表示不满足
                - msg (str): 详细的判断结果描述信息
                
        Raises:
            NoSuchElementException: 当找不到指定元素时抛出
            Exception: 当无法获取元素选中状态时抛出异常
            
        Example:
            >>> element = {'by': 'id', 'value': 'agree_checkbox'}
            >>> result, msg = condition.condition_ele_selected(element, '=', True)
            >>> result, msg = condition.condition_ele_selected(element, '=', False)
            
        Note:
            - 仅适用于可选择的元素类型（checkbox、radio、option等）
            - 对于不支持选中状态的元素，返回False
            - 常用于表单验证和用户交互状态检查
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

    def condition_ele_enabled(self, element, assertion, expect):
        """
        判断元素启用状态是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的启用状态，True表示启用，False表示禁用
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素启用状态时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'submit_button'}
            result, msg = condition.condition_ele_enabled(element, '=', True)
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

    def condition_ele_displayed(self, element, assertion, expect):
        """
        判断元素显示状态是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的显示状态，True表示显示，False表示隐藏
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素显示状态时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'error_message'}
            result, msg = condition.condition_ele_displayed(element, '=', True)
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

    def condition_ele_css(self, element, name, assertion, expect):
        """
        判断元素CSS样式属性值是否满足指定条件
        @param element: 元素定位信息，包含定位方式和定位值
        @param name: 要获取的CSS属性名称（如'color', 'font-size', 'display'等）
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的CSS属性值或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 找不到指定元素时抛出
        @raises Exception: 无法获取元素CSS样式时抛出
        
        使用示例:
            element = {'by': 'id', 'value': 'title'}
            result, msg = condition.condition_ele_css(element, 'color', '=', 'rgba(255, 0, 0, 1)')
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

    def condition_ele_existed(self, element, assertion, expect):
        """
        判断元素是否存在于DOM中
        @param element: 元素定位信息，包含定位方式和定位值
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的存在状态，True表示存在，False表示不存在
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法判断元素是否存在时抛出（不包括NoSuchElementException）
        
        使用示例:
            element = {'by': 'id', 'value': 'loading_spinner'}
            result, msg = condition.condition_ele_existed(element, '=', True)
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

    def condition_window_position(self, assertion, expect):
        """
        判断浏览器窗口位置是否满足指定条件
        
        获取当前浏览器窗口在屏幕上的位置坐标，并根据断言类型和期望值进行条件判断。
        常用于验证窗口布局、多窗口应用的窗口管理等。
        
        Args:
            assertion (str): 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
            expect (dict): 期望的窗口位置，格式为 {'x': X坐标, 'y': Y坐标}
            
        Returns:
            tuple: (result, msg)
                - result (bool): 条件判断结果，True表示满足条件，False表示不满足
                - msg (str): 详细的判断结果描述信息
                
        Raises:
            Exception: 当无法获取窗口位置时抛出异常
            
        Example:
            >>> result, msg = condition.condition_window_position('=', {'x': 100, 'y': 50})
            >>> result, msg = condition.condition_window_position('>', {'x': 0, 'y': 0})
            
        Note:
            - 坐标原点(0,0)位于屏幕左上角
            - 位置坐标单位为像素(px)
            - 不同操作系统的窗口管理可能有差异
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

    def condition_window_x(self, assertion, expect):
        """
        判断浏览器窗口X坐标是否满足指定条件
        
        获取当前浏览器窗口在屏幕上的X坐标（水平位置），并根据断言类型和期望值进行条件判断。
        常用于验证窗口水平位置、多显示器布局等。
        
        Args:
            assertion (str): 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
            expect (int): 期望的X坐标值（像素）
            
        Returns:
            tuple: (result, msg)
                - result (bool): 条件判断结果，True表示满足条件，False表示不满足
                - msg (str): 详细的判断结果描述信息
                
        Raises:
            Exception: 当无法获取窗口X坐标时抛出异常
            
        Example:
            >>> result, msg = condition.condition_window_x('=', 100)
            >>> result, msg = condition.condition_window_x('>', 0)
            
        Note:
            - X坐标表示窗口左边缘距离屏幕左边缘的距离
            - 坐标值从屏幕左边缘开始计算，向右递增
            - 坐标单位为像素(px)
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

    def condition_window_y(self, assertion, expect):
        """
        判断浏览器窗口Y坐标是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的Y坐标值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取窗口Y坐标时抛出
        
        使用示例:
            result, msg = condition.condition_window_y('=', 50)
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

    def condition_window_size(self, assertion, expect):
        """
        判断浏览器窗口尺寸是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的窗口尺寸，格式为 {'width': 宽度, 'height': 高度}
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取窗口尺寸时抛出
        
        使用示例:
            result, msg = condition.condition_window_size('=', {'width': 1920, 'height': 1080})
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

    def condition_window_width(self, assertion, expect):
        """
        判断浏览器窗口宽度是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的窗口宽度值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取窗口宽度时抛出
        
        使用示例:
            result, msg = condition.condition_window_width('=', 1920)
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

    def condition_window_height(self, assertion, expect):
        """
        判断浏览器窗口高度是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的窗口高度值（像素）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取窗口高度时抛出
        
        使用示例:
            result, msg = condition.condition_window_height('=', 1080)
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

    def condition_cookies(self, assertion, expect):
        """
        判断所有Cookies是否满足指定条件
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的Cookies列表或匹配模式
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取Cookies时抛出
        
        使用示例:
            result, msg = condition.condition_cookies('in', [{'name': 'session_id'}])
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

    def condition_cookie(self, name, assertion, expect):
        """
        判断指定名称的Cookie是否满足指定条件
        @param name: 要获取的Cookie名称
        @param assertion: 断言类型，支持 '=', '!=', 'in', 'not in', '>', '<', '>=', '<=', 'regex' 等
        @param expect: 期望的Cookie信息或None（表示Cookie不存在）
        @return: (result, msg) - 条件判断结果和描述信息
        @raises Exception: 无法获取指定Cookie时抛出
        
        使用示例:
            result, msg = condition.condition_cookie('user_id', '!=', None)
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
        执行自定义Python代码进行条件判断
        @param kwargs: 关键字参数，包含code(代码)、element(元素信息)、data(断言数据)、trans(操作描述)
        @return: (result, msg) - 条件判断结果和描述信息
        @raises NoSuchElementException: 代码中找不到指定元素时抛出
        @raises Exception: 代码执行失败时抛出
        
        可用函数:
            sys_return(value) - 返回要断言的值
            sys_get(name) - 获取公共参数或关联变量
            sys_put(name, value, ps=False) - 设置关联变量或公共参数
            
        使用示例:
            code = 'element_text = driver.find_element_by_id("title").text; sys_return(element_text)'
            result, msg = condition.custom(code=code, element={}, data={'assertion': '=', 'expect': 'Hello'})
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["driver"] = self.driver
        names["test"] = self.test
        try:
            """条件操作需要返回被断言的值 以sys_return(value)返回"""
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

