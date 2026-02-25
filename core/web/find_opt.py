# -*- coding: utf-8 -*-
"""
    Web操作查找模块

    该模块负责根据操作名称查找对应的Web操作函数，是Web自动化测试框架的核心路由模块。
    主要功能包括：
    - 浏览器操作查找：窗口管理、页面导航、等待控制等
    - 页面操作查找：元素交互、鼠标键盘操作、frame切换等
    - 断言操作查找：页面断言、元素断言、窗口断言等
    - 关联操作查找：数据提取、变量保存等
    - 条件操作查找：条件判断、流程控制等
    - 场景操作查找：自定义场景操作

    通过装饰器模式实现操作名称与函数的映射关系，支持中文操作名称。
"""

from core.web.driver.browserOpt import Browser  # 浏览器操作类
from core.web.driver.pageOpt import Page  # 页面操作类
from core.web.driver.scenarioOpt import Scenario  # 场景操作类
from core.web.driver.assertionOpt import Assertion  # 断言操作类
from core.web.driver.relationOpt import Relation  # 关联操作类
from core.web.driver.conditionOpt import Condition  # 条件操作类


def find_browser_opt(operate_name: str):
    """
        查找浏览器操作函数
        
        根据操作名称查找对应的浏览器操作函数，支持窗口管理、页面导航、等待控制等操作。
        
        Args:
            operate_name (str): 操作名称，支持中文操作名称
            
        Returns:
            function: 匹配的操作函数，如果未找到则返回None
            
        支持的操作类型：
            - 窗口操作：最大化、最小化、全屏、设置位置和大小、切换、关闭
            - 页面导航：打开网页、刷新、前进、后退
            - 等待控制：强制等待、隐式等待
            - Cookie管理：添加、删除Cookie
            - 脚本执行：同步和异步JavaScript脚本执行
            - 截图功能：保存屏幕截图
            - 自定义操作：支持扩展自定义功能
    """
    function = None  # 初始化函数变量

    def keywords(name):
        """
            装饰器工厂函数，用于注册操作名称与函数的映射关系
            
            Args:
                name (str): 操作名称
                
            Returns:
                function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则保存对应的函数
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("最大化窗口")
    def max_window(test, driver, **kwargs):
        """最大化浏览器窗口"""
        Browser(test, driver).max_window()

    @keywords("最小化窗口")
    def min_window(test, driver, **kwargs):
        """最小化浏览器窗口"""
        Browser(test, driver).min_window()

    @keywords("全屏窗口")
    def full_window(test, driver, **kwargs):
        """设置浏览器窗口为全屏模式"""
        Browser(test, driver).full_window()

    @keywords("设置窗口位置")
    def set_position_window(test, driver, **kwargs):
        """设置浏览器窗口位置，需要提供x和y坐标"""
        Browser(test, driver).set_position_window(kwargs["data"]["x"], kwargs["data"]["y"])

    @keywords("设置窗口大小")
    def set_size_window(test, driver, **kwargs):
        """设置浏览器窗口大小，需要提供宽度和高度"""
        Browser(test, driver).set_size_window(kwargs["data"]["width"], kwargs["data"]["height"])

    @keywords("切换窗口")
    def switch_to_window(test, driver, **kwargs):
        """切换到指定的浏览器窗口"""
        Browser(test, driver).switch_to_window(kwargs["data"]["window"])

    @keywords("关闭窗口")
    def close_window(test, driver, **kwargs):
        """关闭当前浏览器窗口"""
        Browser(test, driver).close_window()

    @keywords("屏幕截图")
    def save_screenshot(test, driver, **kwargs):
        """保存当前页面的屏幕截图，需要提供截图文件名"""
        Browser(test, driver).save_screenshot(kwargs["data"]["name"])

    @keywords("单击跳转新窗口")
    def click_to_new_window(test, driver, **kwargs):
        """点击元素并跳转到新打开的窗口"""
        Browser(test, driver).click_to_new_window(kwargs["element"]["element"])

    @keywords("返回并关闭当前窗口")
    def back_and_close_window(test, driver, **kwargs):
        """关闭当前窗口并返回到指定窗口"""
        Browser(test, driver).back_and_close_window(kwargs["data"]["window"])

    @keywords("打开网页")
    def open_url(test, driver, **kwargs):
        """打开指定的网页URL，需要提供域名和路径"""
        Browser(test, driver).open_url(kwargs["data"]["domain"], kwargs["data"]["path"])

    @keywords("刷新")
    def refresh(test, driver, **kwargs):
        """刷新当前页面"""
        Browser(test, driver).refresh()

    @keywords("后退")
    def back(test, driver, **kwargs):
        """浏览器后退到上一页"""
        Browser(test, driver).back()

    @keywords("前进")
    def forward(test, driver, **kwargs):
        """浏览器前进到下一页"""
        Browser(test, driver).forward()

    @keywords("强制等待")
    def sleep(test, driver, **kwargs):
        """强制等待指定的秒数，阻塞执行"""
        Browser(test, driver).sleep(kwargs["data"]["second"])

    @keywords("隐式等待")
    def implicitly_wait(test, driver, **kwargs):
        """设置隐式等待时间，等待元素出现"""
        Browser(test, driver).implicitly_wait(kwargs["data"]["second"])

    @keywords("添加cookie")
    def add_cookie(test, driver, **kwargs):
        """向当前页面添加Cookie，需要提供名称和值"""
        Browser(test, driver).add_cookie(kwargs["data"]["name"], kwargs["data"]["value"])

    @keywords("删除cookie")
    def delete_cookie(test, driver, **kwargs):
        """删除指定名称的Cookie"""
        Browser(test, driver).delete_cookie(kwargs["data"]["name"])

    @keywords("删除cookies")
    def delete_cookies(test, driver, **kwargs):
        """删除当前页面的所有Cookie"""
        Browser(test, driver).delete_cookies()

    @keywords("执行脚本")
    def execute_script(test, driver, **kwargs):
        """执行同步JavaScript脚本，可传递参数"""
        Browser(test, driver).execute_script(kwargs["data"]["script"], tuple(kwargs["data"]["arg"]))

    @keywords("执行异步脚本")
    def execute_async_script(test, driver, **kwargs):
        """执行异步JavaScript脚本，可传递参数"""
        Browser(test, driver).execute_async_script(kwargs["data"]["script"], tuple(kwargs["data"]["arg"]))

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        """执行自定义浏览器操作"""
        Browser(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None


def find_page_opt(operate_name: str):
    """
        查找页面元素操作函数
        
        根据操作名称查找对应的页面元素操作函数，支持frame切换、弹出框处理、
        元素交互（点击、输入、拖拽）、键盘鼠标操作等。
        
        Args:
            operate_name (str): 操作名称，如"点击"、"输入"、"切换frame"等
            
        Returns:
            function: 对应的页面操作函数，如果找不到则返回None
            
        支持的操作类型：
            - Frame操作：切换frame、返回默认frame、返回父级frame
            - 弹出框操作：确认、取消、输入文本
            - 元素交互：点击、双击、右键、输入、清空、提交
            - 鼠标操作：拖拽、移动、按下保持、释放
            - 键盘操作：按键按下、按键释放
            - 等待操作：等待元素出现、等待元素消失
            - 自定义操作：支持扩展自定义功能
    """
    function = None

    def keywords(name):
        """
            装饰器工厂函数，用于注册操作名称与函数的映射关系
            
            Args:
                name (str): 操作名称
                
            Returns:
                function: 装饰器函数
        """
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func
        return back

    @keywords("切换frame")
    def switch_frame(test, driver, **kwargs):
        """切换到指定的iframe或frame元素"""
        Page(test, driver).switch_frame(kwargs["element"]["frame"])

    @keywords("返回默认frame")
    def switch_content(test, driver, **kwargs):
        """切换回默认的主frame（顶级frame）"""
        Page(test, driver).switch_content()

    @keywords("返回父级frame")
    def switch_parent(test, driver, **kwargs):
        """切换到当前frame的父级frame"""
        Page(test, driver).switch_parent()

    @keywords("弹出框确认")
    def alert_accept(test, driver, **kwargs):
        """确认（接受）当前的弹出框（alert、confirm、prompt）"""
        Page(test, driver).alert_accept()

    @keywords("弹出框输入")
    def alert_input(test, driver, **kwargs):
        """向prompt弹出框输入文本内容"""
        Page(test, driver).alert_input(kwargs["data"]["text"])

    @keywords("弹出框取消")
    def alert_cancel(test, driver, **kwargs):
        """取消（拒绝）当前的弹出框（confirm、prompt）"""
        Page(test, driver).alert_cancel()

    @keywords("鼠标单击")
    def click_and_hold(test, driver, **kwargs):
        """执行鼠标自由点击操作"""
        Page(test, driver).free_click()

    @keywords("清空")
    def clear(test, driver, **kwargs):
        """清空指定输入元素的内容"""
        Page(test, driver).clear(kwargs["element"]["element"])

    @keywords("输入")
    def input(test, driver, **kwargs):
        """向指定元素输入文本内容"""
        Page(test, driver).input_text(kwargs["element"]["element"], kwargs["data"]["text"])

    @keywords("单击")
    def click(test, driver, **kwargs):
        """点击指定的页面元素"""
        Page(test, driver).click(kwargs["element"]["element"])

    @keywords("提交")
    def submit(test, driver, **kwargs):
        """提交指定的表单元素"""
        Page(test, driver).submit(kwargs["element"]["element"])

    @keywords("单击保持")
    def click_and_hold(test, driver, **kwargs):
        """点击并保持按下状态，不释放鼠标按键"""
        Page(test, driver).click_and_hold(kwargs["element"]["element"])

    @keywords("右键点击")
    def context_click(test, driver, **kwargs):
        """右键点击指定的页面元素"""
        Page(test, driver).context_click(kwargs["element"]["element"])

    @keywords("双击")
    def double_click(test, driver, **kwargs):
        """双击指定的页面元素"""
        Page(test, driver).double_click(kwargs["element"]["element"])

    @keywords("拖拽")
    def drag_and_drop(test, driver, **kwargs):
        """将源元素拖拽到目标元素位置"""
        Page(test, driver).drag_and_drop(kwargs["element"]["startElement"], kwargs["element"]["endElement"])

    @keywords("偏移拖拽")
    def drag_and_drop_by_offset(test, driver, **kwargs):
        """将元素拖拽到指定的坐标偏移位置"""
        Page(test, driver).drag_and_drop_by_offset(kwargs["element"]["element"], kwargs["data"]["x"], kwargs["data"]["y"])

    @keywords("按下键位")
    def key_down(test, driver, **kwargs):
        """按下指定的键盘按键（不释放）"""
        Page(test, driver).key_down(kwargs["element"]["element"], kwargs["data"]["value"])

    @keywords("释放键位")
    def key_up(test, driver, **kwargs):
        """释放指定的键盘按键"""
        Page(test, driver).key_up(kwargs["element"]["element"], kwargs["data"]["value"])

    @keywords("鼠标移动到坐标")
    def move_by_offset(test, driver, **kwargs):
        """将鼠标移动到指定的坐标偏移位置"""
        Page(test, driver).move_by_offset(kwargs["data"]["x"], kwargs["data"]["y"])

    @keywords("鼠标移动到元素")
    def move_to_element(test, driver, **kwargs):
        """将鼠标移动到指定元素上"""
        Page(test, driver).move_to_element(kwargs["element"]["element"])

    @keywords("鼠标元素内偏移")
    def move_to_element_with_offset(test, driver, **kwargs):
        """将鼠标移动到元素内的指定偏移位置"""
        Page(test, driver).move_to_element_with_offset(kwargs["element"]["element"], kwargs["data"]["x"], kwargs["data"]["y"])

    @keywords("释放点击保持状态")
    def release(test, driver, **kwargs):
        """释放鼠标按键（结束点击保持状态）"""
        Page(test, driver).release(kwargs["element"]["element"])

    @keywords("等待元素出现")
    def web_driver_wait(test, driver, **kwargs):
        """等待指定元素出现在页面上，超时则抛出异常"""
        Page(test, driver).wait_element_appear(kwargs["element"]["element"], kwargs["data"]["second"])

    @keywords("等待元素消失")
    def web_driver_wait(test, driver, **kwargs):
        """等待指定元素从页面上消失，超时则抛出异常"""
        Page(test, driver).wait_element_disappear(kwargs["element"]["element"], kwargs["data"]["second"])

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        Page(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None


def find_assertion_opt(operate_name: str):
    """
        查找断言操作函数
        
        根据操作名称查找对应的断言操作函数，支持页面断言、元素断言、窗口断言、Cookie断言等。
        断言失败时会抛出AssertionError异常，用于验证测试结果是否符合预期。
        
        Args:
            operate_name (str): 断言操作名称，如"断言页面标题"、"断言元素文本"等
            
        Returns:
            function: 对应的断言操作函数，如果找不到则返回None
            
        支持的断言类型：
            - 页面断言：标题、URL、源码内容
            - 元素断言：文本、标签、尺寸、位置、属性、状态
            - 窗口断言：位置、尺寸信息
            - Cookie断言：Cookie存在性和值
    """
    function = None

    def keywords(name):
        """
            装饰器工厂函数，用于注册断言操作名称与函数的映射关系
            
            Args:
                name (str): 断言操作名称
                
            Returns:
                function: 装饰器函数
        """
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("断言页面标题")
    def assert_page_title(test, driver, **kwargs):
        return Assertion(test, driver).assert_page_title(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言页面url")
    def assert_page_url(test, driver, **kwargs):
        return Assertion(test, driver).assert_page_url(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言页面源码")
    def assert_page_source(test, driver, **kwargs):
        """断言页面源码内容是否符合预期"""
        return Assertion(test, driver).assert_page_source(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素文本")
    def assert_ele_text(test, driver, **kwargs):
        """断言元素的文本内容是否符合预期"""
        return Assertion(test, driver).assert_ele_text(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                       kwargs["data"]["expect"])

    @keywords("断言元素tag")
    def assert_ele_tag(test, driver, **kwargs):
        """断言元素的HTML标签名称是否符合预期"""
        return Assertion(test, driver).assert_ele_tag(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                      kwargs["data"]["expect"])

    @keywords("断言元素尺寸")
    def assert_ele_size(test, driver, **kwargs):
        """断言元素的尺寸（宽度和高度）是否符合预期"""
        return Assertion(test, driver).assert_ele_size(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                       kwargs["data"]["expect"])

    @keywords("断言元素高度")
    def assert_ele_height(test, driver, **kwargs):
        return Assertion(test, driver).assert_ele_height(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                         kwargs["data"]["expect"])

    @keywords("断言元素宽度")
    def assert_ele_width(test, driver, **kwargs):
        return Assertion(test, driver).assert_ele_width(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                        kwargs["data"]["expect"])

    @keywords("断言元素位置")
    def assert_ele_location(test, driver, **kwargs):
        return Assertion(test, driver).assert_ele_location(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                           kwargs["data"]["expect"])

    @keywords("断言元素X坐标")
    def assert_ele_x(test, driver, **kwargs):
        """断言元素的X坐标是否符合预期"""
        return Assertion(test, driver).assert_ele_x(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                    kwargs["data"]["expect"])

    @keywords("断言元素Y坐标")
    def assert_ele_y(test, driver, **kwargs):
        """断言元素的Y坐标是否符合预期"""
        return Assertion(test, driver).assert_ele_y(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                    kwargs["data"]["expect"])

    @keywords("断言元素属性")
    def assert_ele_attribute(test, driver, **kwargs):
        """断言元素的指定属性值是否符合预期"""
        return Assertion(test, driver).assert_ele_attribute(kwargs["element"]["element"], kwargs["data"]["name"],
                                                            kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素是否选中")
    def assert_ele_selected(test, driver, **kwargs):
        """断言元素是否处于选中状态"""
        return Assertion(test, driver).assert_ele_selected(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                           kwargs["data"]["expect"])

    @keywords("断言元素是否启用")
    def assert_ele_enabled(test, driver, **kwargs):
        """断言元素是否处于启用状态"""
        return Assertion(test, driver).assert_ele_enabled(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                          kwargs["data"]["expect"])

    @keywords("断言元素是否显示")
    def assert_ele_displayed(test, driver, **kwargs):
        """断言元素是否在页面上可见"""
        return Assertion(test, driver).assert_ele_displayed(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                            kwargs["data"]["expect"])

    @keywords("断言元素css样式")
    def assert_ele_css(test, driver, **kwargs):
        """断言元素的CSS样式属性值是否符合预期"""
        return Assertion(test, driver).assert_ele_css(kwargs["element"]["element"], kwargs["data"]["name"],
                                                      kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素是否存在")
    def assert_ele_existed(test, driver, **kwargs):
        """断言元素是否存在于页面DOM中"""
        return Assertion(test, driver).assert_ele_existed(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                          kwargs["data"]["expect"])

    @keywords("断言窗口位置")
    def assert_window_position(test, driver, **kwargs):
        """断言浏览器窗口的位置坐标是否符合预期"""
        return Assertion(test, driver).assert_window_position(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言窗口X坐标")
    def assert_window_x(test, driver, **kwargs):
        """断言浏览器窗口的X坐标是否符合预期"""
        return Assertion(test, driver).assert_window_x(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言窗口Y坐标")
    def assert_window_y(test, driver, **kwargs):
        """断言浏览器窗口的Y坐标是否符合预期"""
        return Assertion(test, driver).assert_window_y(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言窗口尺寸")
    def assert_window_size(test, driver, **kwargs):
        """断言浏览器窗口的尺寸（宽度和高度）是否符合预期"""
        return Assertion(test, driver).assert_window_size(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言窗口宽度")
    def assert_window_width(test, driver, **kwargs):
        """断言浏览器窗口的宽度是否符合预期"""
        return Assertion(test, driver).assert_window_width(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言窗口高度")
    def assert_window_height(test, driver, **kwargs):
        """断言浏览器窗口的高度是否符合预期"""
        return Assertion(test, driver).assert_window_height(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言cookies")
    def assert_cookies(test, driver, **kwargs):
        """断言指定名称的Cookie值是否符合预期"""
        return Assertion(test, driver).assert_cookies(kwargs["data"]["name"], kwargs["data"]["assertion"],
                                                      kwargs["data"]["expect"])

    @keywords("断言cookie")
    def assert_cookie(test, driver, **kwargs):
        return Assertion(test, driver).assert_cookie(kwargs["data"]["name"], kwargs["data"]["assertion"],
                                                     kwargs["data"]["expect"])

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        return Assertion(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None


def find_relation_opt(operate_name: str):
    """
        查找关联操作函数（数据提取操作）
        
        根据操作名称查找对应的数据提取操作函数，用于从页面、元素、窗口等获取各种信息，
        提取的数据可用于后续的断言、条件判断或数据传递。
        
        Args:
            operate_name (str): 关联操作名称，如"提取页面标题"、"提取元素文本"等
            
        Returns:
            function: 对应的数据提取操作函数，如果找不到则返回None
            
        支持的提取类型：
            - 页面信息：标题、URL
            - 元素信息：文本、标签、尺寸、位置、属性、CSS样式
            - 窗口信息：位置、尺寸、句柄
            - Cookie信息：Cookie值
    """
    function = None

    def keywords(name):
        """
            装饰器工厂函数，用于注册关联操作名称与函数的映射关系
            
            Args:
                name (str): 关联操作名称
                
            Returns:
                function: 装饰器函数
        """
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("提取页面标题")
    def get_page_title(test, driver, **kwargs):
        """提取当前页面的标题并保存到指定变量"""
        Relation(test, driver).get_page_title(kwargs["data"]["save_name"])

    @keywords("提取页面url")
    def get_page_url(test, driver, **kwargs):
        """提取当前页面的URL地址并保存到指定变量"""
        Relation(test, driver).get_page_url(kwargs["data"]["save_name"])

    @keywords("提取元素文本")
    def get_ele_text(test, driver, **kwargs):
        """提取指定元素的文本内容并保存到指定变量"""
        Relation(test, driver).get_ele_text(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素tag")
    def get_ele_tag(test, driver, **kwargs):
        """提取指定元素的HTML标签名称并保存到指定变量"""
        Relation(test, driver).get_ele_tag(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素尺寸")
    def get_ele_size(test, driver, **kwargs):
        """提取指定元素的尺寸（宽度和高度）并保存到指定变量"""
        Relation(test, driver).get_ele_size(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素高度")
    def get_ele_height(test, driver, **kwargs):
        """提取指定元素的高度并保存到指定变量"""
        Relation(test, driver).get_ele_height(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素宽度")
    def get_ele_width(test, driver, **kwargs):
        """提取指定元素的宽度并保存到指定变量"""
        Relation(test, driver).get_ele_width(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素位置")
    def get_ele_location(test, driver, **kwargs):
        """提取指定元素的位置坐标并保存到指定变量"""
        Relation(test, driver).get_ele_location(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素X坐标")
    def get_ele_x(test, driver, **kwargs):
        """提取指定元素的X坐标并保存到指定变量"""
        Relation(test, driver).get_ele_x(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素Y坐标")
    def get_ele_y(test, driver, **kwargs):
        """提取指定元素的Y坐标并保存到指定变量"""
        Relation(test, driver).get_ele_y(kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素属性")
    def get_ele_attribute(test, driver, **kwargs):
        """提取指定元素的指定属性值并保存到指定变量"""
        Relation(test, driver).get_ele_attribute(kwargs["element"]["element"], kwargs["data"]["name"], kwargs["data"]["save_name"])

    @keywords("提取元素css样式")
    def get_ele_css(test, driver, **kwargs):
        """提取指定元素的CSS样式属性值并保存到指定变量"""
        Relation(test, driver).get_ele_css(kwargs["element"]["element"], kwargs["data"]["name"],
                                           kwargs["data"]["save_name"])

    @keywords("提取窗口位置")
    def get_window_position(test, driver, **kwargs):
        """提取浏览器窗口的位置坐标并保存到指定变量"""
        Relation(test, driver).get_window_position(kwargs["data"]["save_name"])

    @keywords("提取窗口X坐标")
    def get_window_x(test, driver, **kwargs):
        """提取浏览器窗口的X坐标并保存到指定变量"""
        Relation(test, driver).get_window_x(kwargs["data"]["save_name"])

    @keywords("提取窗口Y坐标")
    def get_window_y(test, driver, **kwargs):
        """提取浏览器窗口的Y坐标并保存到指定变量"""
        Relation(test, driver).get_window_y(kwargs["data"]["save_name"])

    @keywords("提取窗口尺寸")
    def get_window_size(test, driver, **kwargs):
        """提取浏览器窗口的尺寸（宽度和高度）并保存到指定变量"""
        Relation(test, driver).get_window_size(kwargs["data"]["save_name"])

    @keywords("提取窗口宽度")
    def get_window_width(test, driver, **kwargs):
        """提取浏览器窗口的宽度并保存到指定变量"""
        Relation(test, driver).get_window_width(kwargs["data"]["save_name"])

    @keywords("提取窗口高度")
    def get_window_height(test, driver, **kwargs):
        """提取浏览器窗口的高度并保存到指定变量"""
        Relation(test, driver).get_window_height(kwargs["data"]["save_name"])

    @keywords("提取当前窗口句柄")
    def get_current_handle(test, driver, **kwargs):
        """提取当前浏览器窗口的句柄并保存到指定变量"""
        Relation(test, driver).get_current_handle(kwargs["data"]["save_name"])

    @keywords("提取所有窗口句柄")
    def get_all_handle(test, driver, **kwargs):
        """提取所有浏览器窗口的句柄列表并保存到指定变量"""
        Relation(test, driver).get_all_handle(kwargs["data"]["save_name"])

    @keywords("提取cookies")
    def get_cookies(test, driver, **kwargs):
        """提取当前页面的所有Cookie并保存到指定变量"""
        Relation(test, driver).get_cookies(kwargs["data"]["save_name"])

    @keywords("提取cookie")
    def get_cookie(test, driver, **kwargs):
        """提取指定名称的Cookie值并保存到指定变量"""
        Relation(test, driver).get_cookie(kwargs["data"]["name"], kwargs["data"]["save_name"])

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        """执行自定义关联操作"""
        Relation(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None


def find_condition_opt(operate_name: str):
    """
        查找条件操作函数（条件判断操作）
        
        根据操作名称查找对应的条件判断操作函数，用于判断页面、元素、窗口等的状态或属性，
        返回布尔值结果，常用于流程控制和条件分支。
        
        Args:
            operate_name (str): 条件操作名称，如"判断页面标题"、"判断元素存在"等
            
        Returns:
            function: 对应的条件判断操作函数，如果找不到则返回None
            
        支持的判断类型：
            - 页面状态：标题、URL、源码
            - 元素状态：文本、标签、尺寸、位置、属性、选中、启用、显示、CSS样式、存在性
            - 窗口状态：位置、尺寸
            - Cookie状态：Cookie值
    """
    function = None

    def keywords(name):
        """
        装饰器工厂函数，用于注册条件操作名称与函数的映射关系
        
        Args:
            name (str): 条件操作名称
            
        Returns:
            function: 装饰器函数
        """
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("判断页面标题")
    def condition_page_title(test, driver, **kwargs):
        """判断当前页面标题是否符合预期条件"""
        return Condition(test, driver).condition_page_title(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断页面url")
    def condition_page_url(test, driver, **kwargs):
        """判断当前页面URL是否符合预期条件"""
        return Condition(test, driver).condition_page_url(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断页面源码")
    def condition_page_source(test, driver, **kwargs):
        """判断当前页面源码是否包含指定内容"""
        return Condition(test, driver).condition_page_source(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素文本")
    def condition_ele_text(test, driver, **kwargs):
        """判断指定元素的文本内容是否符合预期条件"""
        return Condition(test, driver).condition_ele_text(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                          kwargs["data"]["expect"])

    @keywords("判断元素tag")
    def condition_ele_tag(test, driver, **kwargs):
        """判断指定元素的HTML标签名称是否符合预期条件"""
        return Condition(test, driver).condition_ele_tag(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                         kwargs["data"]["expect"])

    @keywords("判断元素尺寸")
    def condition_ele_size(test, driver, **kwargs):
        """判断指定元素的尺寸（宽度和高度）是否符合预期条件"""
        return Condition(test, driver).condition_ele_size(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                          kwargs["data"]["expect"])

    @keywords("判断元素高度")
    def condition_ele_height(test, driver, **kwargs):
        """判断指定元素的高度是否符合预期条件"""
        return Condition(test, driver).condition_ele_height(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                            kwargs["data"]["expect"])

    @keywords("判断元素宽度")
    def condition_ele_width(test, driver, **kwargs):
        """判断指定元素的宽度是否符合预期条件"""
        return Condition(test, driver).condition_ele_width(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                           kwargs["data"]["expect"])

    @keywords("判断元素位置")
    def condition_ele_location(test, driver, **kwargs):
        """判断指定元素的位置坐标是否符合预期条件"""
        return Condition(test, driver).condition_ele_location(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                              kwargs["data"]["expect"])

    @keywords("判断元素X坐标")
    def condition_ele_x(test, driver, **kwargs):
        """判断指定元素的X坐标是否符合预期条件"""
        return Condition(test, driver).condition_ele_x(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                       kwargs["data"]["expect"])

    @keywords("判断元素Y坐标")
    def condition_ele_y(test, driver, **kwargs):
        """判断指定元素的Y坐标是否符合预期条件"""
        return Condition(test, driver).condition_ele_y(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                       kwargs["data"]["expect"])

    @keywords("判断元素属性")
    def condition_ele_attribute(test, driver, **kwargs):
        """判断指定元素的指定属性值是否符合预期条件"""
        return Condition(test, driver).condition_ele_attribute(kwargs["element"]["element"], kwargs["data"]["name"],
                                                               kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素是否选中")
    def condition_ele_selected(test, driver, **kwargs):
        """判断指定元素是否处于选中状态"""
        return Condition(test, driver).condition_ele_selected(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                              kwargs["data"]["expect"])

    @keywords("判断元素是否启用")
    def condition_ele_enabled(test, driver, **kwargs):
        """判断指定元素是否处于启用状态"""
        return Condition(test, driver).condition_ele_enabled(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                             kwargs["data"]["expect"])

    @keywords("判断元素是否显示")
    def condition_ele_displayed(test, driver, **kwargs):
        """判断指定元素是否在页面上可见"""
        return Condition(test, driver).condition_ele_displayed(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                               kwargs["data"]["expect"])

    @keywords("判断元素css样式")
    def condition_ele_css(test, driver, **kwargs):
        """判断指定元素的CSS样式属性值是否符合预期条件"""
        return Condition(test, driver).condition_ele_css(kwargs["element"]["element"], kwargs["data"]["name"],
                                                         kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素是否存在")
    def condition_ele_existed(test, driver, **kwargs):
        """判断指定元素是否存在于页面DOM中"""
        return Condition(test, driver).condition_ele_existed(kwargs["element"]["element"], kwargs["data"]["assertion"],
                                                             kwargs["data"]["expect"])

    @keywords("判断窗口位置")
    def condition_window_position(test, driver, **kwargs):
        """判断浏览器窗口的位置坐标是否符合预期条件"""
        return Condition(test, driver).condition_window_position(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断窗口X坐标")
    def condition_window_x(test, driver, **kwargs):
        """判断浏览器窗口的X坐标是否符合预期条件"""
        return Condition(test, driver).condition_window_x(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断窗口Y坐标")
    def condition_window_y(test, driver, **kwargs):
        """判断浏览器窗口的Y坐标是否符合预期条件"""
        return Condition(test, driver).condition_window_y(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断窗口尺寸")
    def condition_window_size(test, driver, **kwargs):
        """判断浏览器窗口的尺寸（宽度和高度）是否符合预期条件"""
        return Condition(test, driver).condition_window_size(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断窗口宽度")
    def condition_window_width(test, driver, **kwargs):
        """判断浏览器窗口的宽度是否符合预期条件"""
        return Condition(test, driver).condition_window_width(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断窗口高度")
    def condition_window_height(test, driver, **kwargs):
        """判断浏览器窗口的高度是否符合预期条件"""
        return Condition(test, driver).condition_window_height(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断cookies")
    def condition_cookies(test, driver, **kwargs):
        """判断当前页面的所有Cookie是否符合预期条件"""
        return Condition(test, driver).condition_cookies(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断cookie")
    def condition_cookie(test, driver, **kwargs):
        """判断指定名称的Cookie值是否符合预期条件"""
        return Condition(test, driver).condition_cookie(kwargs["data"]["name"], kwargs["data"]["assertion"],
                                                        kwargs["data"]["expect"])

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        """执行自定义条件判断操作"""
        return Condition(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None


def find_scenario_opt(operate_name: str):
    """
        查找场景操作函数（自定义场景操作）
        
        根据操作名称查找对应的场景操作函数，用于执行复杂的自定义测试场景，
        通常包含多个步骤的组合操作或特定业务逻辑的封装。
        
        Args:
            operate_name (str): 场景操作名称，如"自定义"等
            
        Returns:
            function: 对应的场景操作函数，如果找不到则返回None
            
        支持的场景类型：
            - 自定义场景：执行用户定义的复杂测试场景
    """
    function = None

    def keywords(name):
        """
            装饰器工厂函数，用于注册场景操作名称与函数的映射关系
            
            Args:
                name (str): 场景操作名称
                
            Returns:
                function: 装饰器函数
        """
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("自定义")
    def custom(test, driver, **kwargs):
        """
            执行自定义场景操作
            
            根据传入的参数执行用户定义的复杂测试场景，
            可以包含多个操作步骤的组合或特定的业务逻辑。
        """
        return Scenario(test, driver).custom(**kwargs)

    try:
        return function
    except:
        return None
