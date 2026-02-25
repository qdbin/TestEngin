# -*- coding: utf-8 -*-
"""
页面操作模块

提供Web页面交互操作功能，包括框架切换、弹出框处理、鼠标键盘操作、
表单操作、等待机制和自定义操作等。
"""

import sys

from selenium.common.exceptions import NoSuchElementException  # Selenium元素未找到异常
from selenium.webdriver import ActionChains  # Selenium动作链，用于复杂交互操作
from selenium.webdriver.common.keys import Keys  # Selenium键盘按键常量
from selenium.webdriver.support import wait, expected_conditions  # Selenium等待条件
from selenium.webdriver.support.wait import WebDriverWait  # Selenium显式等待

from core.web.driver import Operation  # 导入基础操作类


class Page(Operation):
    """
    页面操作类
    
    提供Web页面交互操作功能，包括框架切换、弹出框处理、鼠标键盘操作、
    表单操作、等待机制和自定义操作等。
    """

    def switch_frame(self, frame):
        """
        切换到指定的iframe框架
        @param frame: 框架元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的框架元素不存在时抛出
        @raises Exception: 切换框架失败时抛出
        
        使用示例:
            page.switch_frame(("id", "myframe"))
        """
        try:
            frame_reference = self.find_element(frame)  # 查找框架元素
            self.driver.switch_to.frame(frame_reference)  # 切换到指定框架
            self.test.debugLog("成功切换frame:%s" % frame[1])
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法切换frame:%s" % frame[1])
            raise e

    def switch_content(self):
        """
        返回到页面的默认内容（主框架）
        @raises Exception: 切换到默认内容失败时抛出
        
        使用示例:
            page.switch_content()
        """
        try:
            self.driver.switch_to.default_content()  # 切换到默认内容
            self.test.debugLog("成功切换default content")
        except Exception as e:
            self.test.errorLog("无法切换default content")
            raise e

    def switch_parent(self):
        """
        返回到父级框架
        @raises Exception: 切换到父框架失败时抛出
        
        使用示例:
            page.switch_parent()
        """
        try:
            self.driver.switch_to.parent_frame()  # 切换到父框架
            self.test.debugLog("成功切换parent content")
        except Exception as e:
            self.test.errorLog("无法切换parent content")
            raise e

    def alert_accept(self):
        """
        确认弹出框（Alert对话框）
        @raises Exception: 弹出框不存在或确认操作失败时抛出
        
        使用示例:
            page.alert_accept()
        """
        try:
            # 等待弹出框出现，最多等待30秒
            alert = wait.WebDriverWait(self.driver, timeout=30).until(expected_conditions.alert_is_present())
            alert.accept()  # 点击确认按钮
            self.test.debugLog("成功执行alert accept")
        except Exception as e:
            self.test.errorLog("无法执行alert accept")
            raise e

    def alert_input(self, text):
        """
        在弹出框中输入文本
        @param text: 要输入的文本内容
        @raises Exception: 弹出框不存在或输入操作失败时抛出
        
        使用示例:
            page.alert_input("Hello World")
        """
        try:
            # 等待弹出框出现，最多等待30秒
            alert = wait.WebDriverWait(self.driver, timeout=30).until(expected_conditions.alert_is_present())
            alert.send_keys(text)  # 在弹出框中输入文本
            self.test.debugLog("成功执行alert input")
        except Exception as e:
            self.test.errorLog("无法执行alert input")
            raise e

    def alert_cancel(self):
        """
        取消弹出框（Alert对话框）
        @raises Exception: 弹出框不存在或取消操作失败时抛出
        
        使用示例:
            page.alert_cancel()
            - 取消后弹出框会自动关闭
            - 适用于confirm、prompt类型的弹出框
            - 对于alert类型弹出框，取消和确认效果相同
            - 取消操作通常会让JavaScript返回false或null
            - 如果30秒内没有弹出框出现会抛出超时异常
        """
        try:
            # 等待弹出框出现，最多等待30秒
            alert = wait.WebDriverWait(self.driver, timeout=30).until(expected_conditions.alert_is_present())
            alert.dismiss()  # 点击取消按钮
            self.test.debugLog("成功执行alert cancel")
        except Exception as e:
            self.test.errorLog("无法执行alert cancel")
            raise e

    def free_click(self):
        """
        执行自由鼠标单击操作
        
        该方法在当前鼠标位置执行单击操作，不依赖于具体的页面元素。
        适用于需要在鼠标当前位置进行点击的场景。
        
        Raises:
            NoSuchElementException: 当操作涉及的元素不存在时抛出
            Exception: 当点击操作失败时抛出异常
            
        Note:
            - 点击位置为鼠标当前所在位置
            - 建议在调用前先使用move相关方法定位鼠标位置
            - 该操作不会自动移动鼠标到特定元素
        """
        try:
            ActionChains(self.driver).click().perform()
            self.test.debugLog("成功执行free click")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行free click")
            raise e

    def clear(self, element):
        """
        清除输入框内容
        
        该方法清除指定输入框或文本区域中的所有文本内容，
        通常用于在输入新内容前清空原有数据。
        
        Args:
            element (tuple): 要清除内容的元素定位信息，格式为(定位方式, 定位值)
            
        Raises:
            NoSuchElementException: 当指定的元素不存在时抛出
            Exception: 当元素不支持清除操作或其他操作失败时抛出异常
            
        Note:
            - 主要适用于input、textarea等可编辑元素
            - 清除操作会移除元素中的所有文本内容
            - 对于某些特殊的输入控件，可能需要特殊处理
            - 建议在输入新内容前先执行清除操作
        """
        try:
            self.find_element(element).clear()
            self.test.debugLog("成功执行clear")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行clear")
            raise e

    def input_text(self, element, text):
        """
        向输入框输入文本
        @param element: 输入框元素的定位信息，格式为(定位方式, 定位值)
        @param text: 要输入的文本内容
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 元素不支持文本输入或其他操作失败时抛出
        
        使用示例:
            page.input_text(("id", "username"), "admin")
        """
        try:
            self.find_element(element).send_keys(text)
            self.test.debugLog("成功执行文本输入:'%s'" % text)
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行文本输入:'%s'" % text)
            raise e

    def click(self, element):
        """
        点击指定的页面元素
        @param element: 元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 元素不可点击或其他点击操作失败时抛出
        
        使用示例:
            page.click(("id", "submit-btn"))
        """
        try:
            self.find_element(element).click()
            self.test.debugLog("成功执行click")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行click")
            raise e

    def submit(self, element):
        """
        提交表单
        @param element: 表单内任意元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 表单提交失败或其他操作失败时抛出
        
        使用示例:
            page.submit(("id", "login-form"))
        """
        try:
            self.find_element(element).submit()
            self.test.debugLog("成功执行submit")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行submit")
            raise e

    def click_and_hold(self, element):
        """
        点击并保持按住指定元素
        @param element: 要点击并保持的元素定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 元素不可点击或其他操作失败时抛出
        
        使用示例:
            page.click_and_hold(("id", "drag-item"))
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).click_and_hold(ele).perform()
            self.test.debugLog("成功执行click and hold")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行click and hold")
            raise e

    def context_click(self, element):
        """
        右键点击指定元素
        @param element: 要右键点击的元素定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 元素不可点击或其他右键操作失败时抛出
        
        使用示例:
            page.context_click(("id", "menu-item"))
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).context_click(ele).perform()
            self.test.debugLog("成功执行context click")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行context click")
            raise e

    def double_click(self, element):
        """
        双击指定元素
        @param element: 要双击的元素定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 元素不可点击或其他双击操作失败时抛出
        
        使用示例:
            page.double_click(("id", "file-item"))
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).double_click(ele).perform()
            self.test.debugLog("成功执行double click")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行double click")
            raise e

    def drag_and_drop(self, start_element, end_element):
        """
        拖拽元素到目标位置
        @param start_element: 源元素的定位信息，格式为(定位方式, 定位值)
        @param end_element: 目标元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 源元素或目标元素不存在时抛出
        @raises Exception: 拖拽操作失败时抛出
        
        使用示例:
            page.drag_and_drop(("id", "source"), ("id", "target"))
        """
        try:
            ele = self.find_element(start_element)
            tar_ele = self.find_element(end_element)
            ActionChains(self.driver).drag_and_drop(ele, tar_ele).perform()
            self.test.debugLog("成功执行drag and drop to element")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行drag and drop to element")
            raise e

    def drag_and_drop_by_offset(self, element, x, y):
        """
        拖拽元素到指定偏移位置
        
        该方法将指定元素拖拽到相对于其当前位置的偏移坐标，
        适用于需要精确控制拖拽距离的场景。
        
        Args:
            element (tuple): 要拖拽的元素定位信息，格式为(定位方式, 定位值)
            x (int): X轴偏移量（正数向右，负数向左）
            y (int): Y轴偏移量（正数向下，负数向上）
            
        Raises:
            NoSuchElementException: 当指定的元素不存在时抛出
            Exception: 当拖拽操作失败时抛出异常
            
        Note:
            - 偏移量是相对于元素当前位置的
            - 坐标系以元素中心为起点
            - 确保目标位置在页面可视范围内
            - 某些元素可能对拖拽有限制
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).drag_and_drop_by_offset(ele, x, y).perform()
            self.test.debugLog("成功执行drag and drop to (%s, %s)" % (x,y))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行drag and drop to (%s, %s)" % (x,y))
            raise e

    def key_down(self, element, value):
        """
        按下键盘按键
        
        该方法模拟按下指定的键盘按键，可以是普通字符键或功能键，
        常用于模拟快捷键操作或特殊按键输入。
        
        Args:
            element (tuple): 目标元素的定位信息，格式为(定位方式, 定位值)
            value (str): 要按下的按键名称，必须是Keys类中定义的常量
            
        Raises:
            NoSuchElementException: 当指定的元素不存在时抛出
            Exception: 当按键不存在或按键操作失败时抛出异常
            
        Note:
            - 支持普通字符键和功能键（如Ctrl、Alt、Shift等）
            - 按键名称不区分大小写，会自动转换为大写
            - 按键会保持按下状态，直到调用key_up释放
            - 常用于组合键操作的第一步
            - 必须是selenium.webdriver.common.keys.Keys中定义的有效按键
        """
        try:
            ele = self.find_element(element)
            if hasattr(Keys, value.upper()):
                keys = getattr(Keys, value)
            else:
                raise Exception("键位%s不存在" % value)
            ActionChains(self.driver).key_down(keys, ele).perform()
            self.test.debugLog("成功执行key down %s" % value)
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行key down %s" % value)
            raise e

    def key_up(self, element, value):
        """
        释放键盘按键
        @param element: 目标元素的定位信息，格式为(定位方式, 定位值)
        @param value: 要释放的按键名称
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 按键不存在或按键释放操作失败时抛出
        
        使用示例:
            page.key_up(("id", "input"), "CONTROL")
        """
        try:
            ele = self.find_element(element)
            if hasattr(Keys, value.upper()):
                keys = getattr(Keys, value)
            else:
                raise Exception("键位%s不存在" % value)
            ActionChains(self.driver).key_up(keys, ele).perform()
            self.test.debugLog("成功执行key up %s" % value)
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行key up %s" % value)
            raise e

    def move_by_offset(self, x, y):
        """
        鼠标移动到指定偏移位置
        @param x: X轴偏移量（正数向右，负数向左）
        @param y: Y轴偏移量（正数向下，负数向上）
        @raises Exception: 鼠标移动操作失败时抛出
        
        使用示例:
            page.move_by_offset(100, 50)
        """
        try:
            ActionChains(self.driver).move_by_offset(x, y).perform()
            self.test.debugLog("成功执行move mouse to (%s, %s)" % (x,y))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行move mouse to (%s, %s)" % (x,y))
            raise e

    def move_to_element(self, element):
        """
        鼠标移动到指定元素
        @param element: 目标元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 鼠标移动操作失败时抛出
        
        使用示例:
            page.move_to_element(("id", "menu"))
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).move_to_element(ele).perform()
            self.test.debugLog("成功执行move mouse to element")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行move mouse to element")
            raise e

    def move_to_element_with_offset(self, element, x, y):
        """
        鼠标移动到元素的指定偏移位置
        @param element: 目标元素的定位信息，格式为(定位方式, 定位值)
        @param x: 相对于元素左上角的X轴偏移量
        @param y: 相对于元素左上角的Y轴偏移量
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 鼠标移动操作失败时抛出
        
        使用示例:
            page.move_to_element_with_offset(("id", "canvas"), 50, 30)
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).move_to_element_with_offset(ele, x, y).perform()
            self.test.debugLog("成功执行move mouse to element with (%s, %s)" % (x,y))
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行move mouse to element with (%s, %s)" % (x,y))
            raise e

    def release(self, element):
        """
        释放鼠标按键
        @param element: 目标元素的定位信息，格式为(定位方式, 定位值)
        @raises NoSuchElementException: 指定的元素不存在时抛出
        @raises Exception: 鼠标释放操作失败时抛出
        
        使用示例:
            page.release(("id", "drop_target"))
        """
        try:
            ele = self.find_element(element)
            ActionChains(self.driver).release(ele).perform()
            self.test.debugLog("成功执行release mouse")
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行release mouse")
            raise e

    def wait_element_appear(self, element, second):
        """
        等待元素出现
        @param element: 要等待的元素定位信息，格式为(定位方式, 定位值)
        @param second: 最大等待时间（秒）
        @raises Exception: 等待超时或其他等待操作失败时抛出
        
        使用示例:
            page.wait_element_appear(("id", "loading_content"), 15)
        """
        try:
            WebDriverWait(self.driver, second, 0.2).until(expected_conditions.presence_of_element_located(element))
            self.test.debugLog("成功执行wait %ds until element appear" % second)
        except Exception as e:
            self.test.errorLog("无法执行wait %ds until element appear" % second)
            raise e

    def wait_element_disappear(self, element, second):
        """
        等待元素消失
        @param element: 要等待消失的元素定位信息，格式为(定位方式, 定位值)
        @param second: 最大等待时间（秒）
        @raises Exception: 等待超时或其他等待操作失败时抛出
        
        使用示例:
            page.wait_element_disappear(("class", "loading_spinner"), 20)
        """
        try:
            WebDriverWait(self.driver, second, 0.2).until_not(expected_conditions.presence_of_element_located(element))
            self.test.debugLog("成功执行wait %ds until element disappear" % second)
        except Exception as e:
            self.test.errorLog("无法执行wait %ds until element disappear" % second)
            raise e

    def custom(self, **kwargs):
        """
        执行自定义Python脚本操作
        @param kwargs: 关键字参数，包含code、element、data、trans等
        @raises NoSuchElementException: 脚本中涉及的元素不存在时抛出
        @raises Exception: 脚本执行失败或其他错误时抛出
        
        使用示例:
            page.custom(code="print('Hello')", element=("id", "test"), data={}, trans="自定义操作")
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
