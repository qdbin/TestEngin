# -*- coding: utf-8 -*-
"""
浏览器操作模块

该模块提供了完整的浏览器操作功能，包括：
- 窗口管理：最大化、最小化、全屏、位置和尺寸设置
- 窗口切换：多窗口间的切换和关闭操作
- 页面导航：URL打开、刷新、前进、后退
- 截图功能：页面截图保存
- Cookie管理：添加、删除Cookie
- 脚本执行：同步和异步JavaScript脚本执行
- 等待机制：强制等待和隐式等待
- 自定义操作：支持用户自定义代码执行
"""

import sys  # 系统相关功能模块

from selenium.common.exceptions import NoSuchElementException  # Selenium异常处理

from core.web.driver import Operation  # 基础操作类
from datetime import datetime  # 日期时间处理
from time import sleep  # 时间延迟功能

from tools.utils.utils import url_join  # URL拼接工具


class Browser(Operation):
    """
    浏览器操作类
    
    继承自Operation基类，提供完整的浏览器操作功能，包括窗口管理、
    页面导航、Cookie管理、脚本执行等操作，并提供统一的异常处理和日志记录。
    
    主要功能：
    - 窗口管理：最大化、最小化、全屏、位置和尺寸设置
    - 页面操作：URL导航、刷新、前进、后退
    - 多窗口处理：窗口切换和关闭
    - 数据管理：Cookie增删操作
    - 脚本执行：JavaScript代码执行
    - 等待控制：强制等待和隐式等待
    """

    def max_window(self):
        """
        最大化浏览器窗口
        
        @raises Exception: 当窗口最大化操作失败时抛出异常
        
        Example:
            browser.max_window()  # 最大化当前窗口
        """
        try:
            self.driver.maximize_window()  # 执行窗口最大化操作
            self.test.debugLog("成功执行maximize window")
        except Exception as e:
            self.test.errorLog("无法执行maximize window")
            raise e

    def min_window(self):
        """
        最小化浏览器窗口
        
        @raises Exception: 当窗口最小化操作失败时抛出异常
        
        Example:
            browser.min_window()  # 最小化当前窗口
        """
        try:
            self.driver.minimize_window()  # 执行窗口最小化操作
            self.test.debugLog("成功执行minimize window")
        except Exception as e:
            self.test.errorLog("无法执行minimize window")
            raise e

    def full_window(self):
        """
        全屏显示浏览器窗口
        
        @raises Exception: 当全屏操作失败时抛出异常
        
        Example:
            browser.full_window()  # 全屏显示当前窗口
        """
        try:
            self.driver.fullscreen_window()  # 执行窗口全屏操作
            self.test.debugLog("成功执行full screen window")
        except Exception as e:
            self.test.errorLog("无法执行full screen window")
            raise e

    def set_position_window(self, x, y):
        """
        设置浏览器窗口位置
        
        @param x: 窗口左上角的X坐标（像素）
        @param y: 窗口左上角的Y坐标（像素）
        @raises Exception: 当设置窗口位置失败时抛出异常
        
        Example:
            browser.set_position_window(100, 50)  # 设置窗口位置到(100,50)
        """
        try:
            self.driver.set_window_position(x, y)  # 设置窗口位置到指定坐标
            self.test.debugLog("成功执行set window position")
        except Exception as e:
            self.test.errorLog("无法执行set window position")
            raise e

    def set_size_window(self, width, height):
        """
        设置浏览器窗口尺寸
        
        @param width: 窗口宽度（像素）
        @param height: 窗口高度（像素）
        @raises Exception: 当设置窗口尺寸失败时抛出异常
        
        Example:
            browser.set_size_window(1024, 768)  # 设置窗口尺寸为1024x768
        """
        try:
            self.driver.set_window_size(width, height)  # 设置窗口尺寸
            self.test.debugLog("成功执行set window size")
        except Exception as e:
            self.test.errorLog("无法执行set window size")
            raise e

    def switch_to_window(self, window):
        """
        切换到指定的浏览器窗口
        
        @param window: 目标窗口的句柄（window handle）
        @raises Exception: 当窗口切换失败时抛出异常
        
        Example:
            handles = driver.window_handles
            browser.switch_to_window(handles[1])  # 切换到第二个窗口
        """
        try:
            self.driver.switch_to.window(window)  # 切换到指定窗口
            self.test.debugLog("成功执行switch window")
        except Exception as e:
            self.test.errorLog("无法执行switch window")
            raise e

    def close_window(self):
        """
        关闭当前浏览器窗口
        
        @raises Exception: 当窗口关闭失败时抛出异常
        
        Example:
            browser.close_window()  # 关闭当前活动窗口
        """
        try:
            self.driver.close()  # 关闭当前窗口
            self.test.debugLog("成功执行close window")
        except Exception as e:
            self.test.errorLog("无法执行close window")
            raise e

    def save_screenshot(self, name):
        """
        保存当前页面截图
        
        @param name: 截图文件的名称（不包含扩展名）
        @raises Exception: 当截图操作失败时抛出异常
        
        Example:
            browser.save_screenshot("login_page")  # 保存登录页面截图
        """
        try:
            screenshot = self.driver.get_screenshot_as_png()  # 获取PNG格式截图
            self.test.saveScreenShot(name, screenshot)  # 保存截图到指定位置
            self.test.debugLog("成功执行screen shot")
        except Exception as e:
            self.test.errorLog("无法执行screen shot")
            raise e

    def click_to_new_window(self, element):
        """
        点击元素并切换到新打开的窗口
        
        @param element: 元素定位信息，包含定位方式和定位值
        @raises NoSuchElementException: 当找不到指定元素时抛出
        @raises Exception: 当点击操作或窗口切换失败时抛出异常
        
        Example:
            element = {"by": "id", "value": "new_window_link"}
            browser.click_to_new_window(element)  # 点击链接并切换到新窗口
        """
        try:
            current = self.driver.window_handles  # 记录当前所有窗口句柄
            # 点击元素打开新窗口
            self.find_element(element).click()
            # 等待新窗口出现（最多60秒）
            current_time = datetime.now()
            while (datetime.now()-current_time).seconds < 60:
                if len(self.driver.window_handles) > len(current):  # 检测到新窗口
                    for window_handle in self.driver.window_handles:
                        if window_handle not in current:  # 找到新窗口句柄
                            self.driver.switch_to.window(window_handle)  # 切换到新窗口
                            self.test.debugLog("成功执行click and switch to new window")
                            return
                else:
                    sleep(2)  # 等待2秒后重新检查
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行click and switch to new window")
            raise e

    def back_and_close_window(self, window):
        """
        关闭当前窗口并返回到指定窗口
        
        @param window: 要返回的目标窗口句柄
        @raises Exception: 当关闭窗口或切换窗口失败时抛出异常
        
        Example:
            main_window = driver.window_handles[0]
            browser.back_and_close_window(main_window)  # 关闭当前窗口并返回主窗口
        """
        try:
            self.driver.close()  # 关闭当前窗口
            self.driver.switch_to.window(window)  # 切换到指定窗口
            self.test.debugLog("成功执行back and close window")
        except Exception as e:
            self.test.errorLog("无法执行back and close window")
            raise e

    def open_url(self, domain, path):
        """
        打开指定URL的网页
        
        @param domain: 网站域名（如：https://www.example.com）
        @param path: 页面路径（如：/login 或 /user/profile）
        @raises Exception: 当页面打开失败时抛出异常
        
        Example:
            browser.open_url("https://www.example.com", "/login")  # 打开登录页面
        """
        try:
            url = url_join(domain, path)  # 拼接完整URL
            self.driver.get(url)  # 打开页面
            self.driver.implicitly_wait(2)  # 设置隐式等待
            self.test.debugLog("成功打开 '%s'" % url_join(domain, path))
        except Exception as e:
            self.test.errorLog("无法打开 '%s'" % url_join(domain, path))
            raise e

    def refresh(self):
        """
        刷新当前页面
        
        @raises Exception: 当页面刷新失败时抛出异常
        
        Example:
            browser.refresh()  # 刷新当前页面
        """
        try:
            self.driver.refresh()  # 执行页面刷新
            self.test.debugLog("成功执行refresh")
        except Exception as e:
            self.test.errorLog("无法执行refresh")
            raise e

    def back(self):
        """
        页面后退
        
        @raises Exception: 当页面后退失败时抛出异常
        
        Example:
            browser.back()  # 返回上一页
        """
        try:
            self.driver.back()  # 执行页面后退
            self.test.debugLog("成功执行back")
        except Exception as e:
            self.test.errorLog("无法执行back")
            raise e

    def forward(self):
        """
        页面前进
        
        @raises Exception: 当页面前进失败时抛出异常
        
        Example:
            browser.forward()  # 前进到下一页
        
            
        Note:
            - 只有在执行过后退操作后才能前进
            - 如果没有可前进的历史记录，操作无效果
            - 前进到的页面可能需要重新加载
            - 操作成功时会记录调试日志
        """
        try:
            self.driver.forward()  # 执行页面前进
            self.test.debugLog("成功执行forward")
        except Exception as e:
            self.test.errorLog("无法执行forward")
            raise e

    def add_cookie(self, name, value):
        """
        添加Cookie到当前域名
        @param name: Cookie的名称
        @param value: Cookie的值
        @raises Exception: 当添加Cookie失败时抛出异常
        
        Example:
            browser.add_cookie("session_id", "abc123")  # 添加会话Cookie
        """
        try:
            self.driver.add_cookie({'name': name, 'value': value})  # 添加Cookie
            self.test.debugLog("成功执行add cookie: %s:%s" % (name, value))
        except Exception as e:
            self.test.errorLog("无法执行add cookie: %s:%s" % (name, value))
            raise e

    def delete_cookie(self, name):
        """
        删除指定名称的Cookie
        @param name: 要删除的Cookie名称
        @raises Exception: 当删除Cookie失败时抛出异常
        
        Example:
            browser.delete_cookie("session_id")  # 删除会话Cookie
        """
        try:
            self.driver.delete_cookie(name)  # 删除指定Cookie
            self.test.debugLog("成功执行delete cookie:%s" % name)
        except Exception as e:
            self.test.errorLog("无法执行delete cookie:%s" % name)
            raise e

    def delete_cookies(self):
        """
        删除当前域名下的所有Cookie
        @raises Exception: 当删除所有Cookie失败时抛出异常
        
        Example:
            browser.delete_cookies()  # 清除所有Cookie
        """
        try:
            self.driver.delete_all_cookies()  # 删除所有Cookie
            self.test.debugLog("成功执行delete cookies")
        except Exception as e:
            self.test.errorLog("无法执行delete cookies")
            raise e

    def execute_script(self, script, arg:tuple):
        """
        执行同步JavaScript脚本
        @param script: 要执行的JavaScript代码字符串
        @param arg: 传递给脚本的参数元组
        @return: 脚本的返回值
        @raises NoSuchElementException: 当脚本中引用的元素不存在时抛出
        @raises Exception: 当脚本执行失败时抛出异常
        
        Example:
            result = browser.execute_script("return document.title;", ())  # 获取页面标题
        """
        try:
            result = self.driver.execute_script(script, *arg)  # 执行JavaScript脚本
            self.test.debugLog("成功执行execute script:%s" % script)
            return result
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行execute script:%s" % script)
            raise e

    def execute_async_script(self, script, arg:tuple):
        """
        执行异步JavaScript脚本
        @param script: 要执行的异步JavaScript代码字符串
        @param arg: 传递给脚本的参数元组
        @return: 脚本的返回值，通过callback函数传递
        @raises NoSuchElementException: 当脚本中引用的元素不存在时抛出
        @raises Exception: 当脚本执行失败时抛出异常
        
        Example:
            result = browser.execute_async_script("var callback = arguments[0]; setTimeout(function(){callback('done');}, 1000);", ())  # 异步等待1秒
        """
        try:
            result = self.driver.execute_async_script(script, *arg)  # 执行异步JavaScript脚本
            self.test.debugLog("成功执行execute async script:%s" % script)
            return result
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行execute async script:%s" % script)
            raise e

    def sleep(self, second):
        """
        强制等待指定时间
        @param second: 等待的秒数，支持小数
        @raises Exception: 当等待操作失败时抛出异常
        
        Example:
            browser.sleep(2)  # 等待2秒
        """
        try:
            sleep(second)  # 强制等待指定秒数
            self.test.debugLog("成功执行sleep %ds" % second)
        except Exception as e:
            self.test.errorLog("无法执行sleep %ds" % second)
            raise e

    def implicitly_wait(self, second):
        """
        设置隐式等待时间
        @param second: 隐式等待的秒数
        @raises Exception: 当设置隐式等待失败时抛出异常
        
        Example:
            browser.implicitly_wait(10)  # 设置隐式等待10秒
        """
        try:
            self.driver.implicitly_wait(second)  # 设置隐式等待时间
            self.test.debugLog("成功执行implicitly wait %ds" % second)
        except Exception as e:
            self.test.errorLog("无法执行implicitly wait %ds" % second)
            raise e

    def custom(self, **kwargs):
        """
        执行自定义Python脚本
        @param kwargs: 关键字参数，包含code、element、data、trans等
        @raises NoSuchElementException: 当脚本中引用的元素不存在时抛出
        @raises Exception: 当脚本执行失败时抛出异常
        
        Example:
            browser.custom(code="print('Hello World')", element={}, data={}, trans="自定义脚本")  # 执行自定义代码
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

            exec(code)  # 执行自定义Python脚本
            self.test.debugLog("成功执行 %s" % kwargs["trans"])
        except NoSuchElementException as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
