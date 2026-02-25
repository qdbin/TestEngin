import sys

from uiautomator2 import UiObjectNotFoundError
from uiautomator2.xpath import XPath
from wda import WDAElementNotFoundError
from core.app.device import Operation, ElementNotFoundError, ElementNotDisappearError


class View(Operation):
    """
    视图操作类
    
    继承自Operation基类，提供移动应用UI元素的各种交互操作。
    支持Android和iOS双平台，包括点击、输入、滑动、拖拽、等待等操作。
    
    Inherits:
        Operation: 操作基类，提供元素查找等基础功能
    
    支持的操作类型：
        - 点击操作：单击、双击、长按（支持元素和坐标）
        - 输入操作：文本输入、清空文本
        - 滑动操作：坐标滑动、元素内滑动、滑动到元素
        - 手势操作：缩放（放大/缩小）
        - 拖拽操作：元素拖拽、坐标拖拽
        - 等待操作：等待元素出现/消失
        - 弹框操作：iOS弹框处理
        - 自定义操作：执行自定义代码
    
    平台兼容性：
        - Android：支持所有操作
        - iOS：部分操作有平台特定实现
    
    Note:
        - 所有操作都包含异常处理和日志记录
        - 支持多种元素定位方式（属性、XPath等）
        - 坐标支持百分比和绝对值两种方式
    """

    def click(self, element):
        """
            单击元素
            
            对指定元素执行单击操作，如果元素存在则点击。
            
            Args:
                element (dict): 元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                    - XPath定位：{"xpath": "//android.widget.Button[@text='确定']"}
            
            Raises:
                Exception: 当元素不存在或点击失败时抛出异常
            
            Note:
                - 使用click_exists方法，超时时间为3秒
                - 如果元素不存在，会等待最多3秒
                - 支持所有类型的可点击元素
            
            使用场景：
                - 点击按钮、链接
                - 选择列表项
                - 触发界面交互
            
            使用示例：
                >>> view.click({"text": "登录"})
                >>> view.click({"xpath": "//button[@id='submit']"}) 
        """
        try:
            # 查找元素并执行点击，如果元素存在的话
            self.find_element(element).click_exists(timeout=3)
            self.test.debugLog("成功单击")
        except Exception as e:
            self.test.errorLog("无法单击")
            raise e

    def double_click(self, system, element):
        """
            双击元素
            
            对指定元素执行双击操作，在元素中心位置进行双击。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 元素定位信息
            
            Raises:
                Exception: 当元素不存在或双击失败时抛出异常
            
            Note:
                - Android使用double_click方法
                - iOS使用double_tap方法
                - 双击位置为元素的中心坐标
            
            使用场景：
                - 双击打开文件
                - 双击缩放图片
                - 双击选择文本
            
            使用示例：
                >>> view.double_click("android", {"text": "图片"})
        """
        try:
            if system == "android":
                # Android平台：在元素中心执行双击
                self.device.double_click(*self.find_element(element).center())
            else:
                # iOS平台：在元素中心执行双击
                self.device.double_tap(*self.find_element(element).center())
            self.test.debugLog("成功双击")
        except Exception as e:
            self.test.errorLog("无法双击")
            raise e

    def long_click(self, system, element, second):
        """
            长按元素
            
            对指定元素执行长按操作，持续指定的时间。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 元素定位信息
                second (float): 长按持续时间（秒）
            
            Raises:
                Exception: 当元素不存在或长按失败时抛出异常
            
            Note:
                - Android：XPath定位使用默认时间，属性定位使用指定时间
                - iOS：使用tap_hold方法，支持自定义时间
                - 长按时间影响触发的操作类型
            
            使用场景：
                - 长按显示上下文菜单
                - 长按选择文本
                - 长按触发特殊功能
            
            使用示例：
                >>> view.long_click("android", {"text": "文件"}, 2.0)
        """
        try:
            if system == "android":
                if "xpath" in element:
                    # XPath定位：使用默认长按时间
                    self.find_element(element).long_click()
                else:
                    # 属性定位：使用指定长按时间
                    self.find_element(element).long_click(second)
            else:
                # iOS平台：使用tap_hold方法
                self.find_element(element).tap_hold(second)
            self.test.debugLog("成功长按%sS" % str(second))
        except Exception as e:
            self.test.errorLog("无法长按%sS" % str(second))
            raise e

    def click_coord(self, x, y):
        """
            坐标单击
            
            在指定坐标位置执行单击操作。
            
            Args:
                x (float): X坐标，支持百分比（0-1）或绝对像素值
                y (float): Y坐标，支持百分比（0-1）或绝对像素值
            
            Raises:
                Exception: 当坐标无效或点击失败时抛出异常
            
            Note:
                - 坐标可以是百分比（0-1）或绝对像素值
                - 百分比相对于屏幕尺寸计算
                - 适用于无法通过元素定位的场景
            
            使用场景：
                - 点击动态生成的元素
                - 点击无法定位的区域
                - 精确位置点击
            
            使用示例：
                >>> view.click_coord(0.5, 0.5)    # 屏幕中心点击
                >>> view.click_coord(100, 200)    # 绝对坐标点击
        """
        try:
            # 在指定坐标执行点击操作
            self.device.click(x, y)
            self.test.debugLog("成功坐标单击")
        except Exception as e:
            self.test.errorLog("无法坐标单击")
            raise e

    def double_click_coord(self, system, x, y):
        """
            坐标双击
            
            在指定坐标位置执行双击操作。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                x (float): X坐标，支持百分比（0-1）或绝对像素值
                y (float): Y坐标，支持百分比（0-1）或绝对像素值
            
            Raises:
                Exception: 当坐标无效或双击失败时抛出异常
            
            Note:
                - Android使用double_click方法
                - iOS使用double_tap方法
                - 坐标支持百分比和绝对值
            
            使用场景：
                - 双击缩放特定位置
                - 双击选择文本区域
                - 双击触发特定功能
            
            使用示例：
                >>> view.double_click_coord("android", 0.3, 0.7)
        """
        try:
            if system == "android":
                # Android平台：坐标双击
                self.device.double_click(x, y)
            else:
                # iOS平台：坐标双击
                self.device.double_tap(x, y)
            self.test.debugLog("成功坐标双击")
        except Exception as e:
            self.test.errorLog("无法坐标双击")
            raise e

    def long_click_coord(self, system, x, y, second):
        """
            坐标长按
            
            在指定坐标位置执行长按操作，持续指定时间。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                x (float): X坐标，支持百分比（0-1）或绝对像素值
                y (float): Y坐标，支持百分比（0-1）或绝对像素值
                second (float): 长按持续时间（秒）
            
            Raises:
                Exception: 当坐标无效或长按失败时抛出异常
            
            Note:
                - Android使用long_click方法
                - iOS使用tap_hold方法
                - 长按时间影响触发的操作
            
            使用场景：
                - 长按显示上下文菜单
                - 长按触发特殊操作
                - 模拟用户长按行为
            
            使用示例：
                >>> view.long_click_coord("android", 0.5, 0.5, 2.0)
        """
        try:
            if system == "android":
                # Android平台：坐标长按
                self.device.long_click(x, y, second)
            else:
                # iOS平台：坐标长按
                self.device.tap_hold(x, y, second)
            self.test.debugLog("成功坐标长按%sS" % str(second))
        except Exception as e:
            self.test.errorLog("无法坐标长按%sS" % str(second))
            raise e

    def swipe(self, system, fx, fy, tx, ty, duration=None):
        """
            坐标滑动
            
            从起始坐标滑动到目标坐标，支持自定义滑动时间。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                fx (float): 起始X坐标，支持百分比（0-1）或绝对像素值
                fy (float): 起始Y坐标，支持百分比（0-1）或绝对像素值
                tx (float): 目标X坐标，支持百分比（0-1）或绝对像素值
                ty (float): 目标Y坐标，支持百分比（0-1）或绝对像素值
                duration (float, optional): 滑动持续时间（秒）
            
            Raises:
                Exception: 当坐标无效或滑动失败时抛出异常
            
            Note:
                - Android：duration为None时使用默认时间
                - iOS：duration为None或空字符串时设为0
                - 滑动速度由duration参数控制
            
            使用场景：
                - 页面滚动
                - 手势操作
                - 拖拽移动
                - 滑动解锁
            
            使用示例：
                >>> view.swipe("android", 0.5, 0.8, 0.5, 0.2, 1.0)  # 向上滑动
                >>> view.swipe("ios", 0.1, 0.5, 0.9, 0.5, 0.5)      # 向右滑动
        """
        try:
            if system == "android":
                if duration == "":
                    duration = None
                # Android平台：执行滑动操作
                self.device.swipe(fx, fy, tx, ty, duration)
            else:
                if duration == "" or duration is None:
                    duration = 0
                # iOS平台：执行滑动操作
                self.device.swipe(fx, fy, tx, ty, duration)
            self.test.debugLog("成功执行滑动")
        except Exception as e:
            self.test.errorLog("无法执行滑动")
            raise e

    def input_text(self, element, text):
        """
            输入文本
            
            向指定元素输入文本内容。
            
            Args:
                element (dict): 元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "输入框", "resourceId": "com.app:id/input"}
                    - XPath定位：{"xpath": "//input[@type='text']"}
                text (str): 要输入的文本内容
            
            Raises:
                Exception: 当元素不存在或输入失败时抛出异常
            
            Note:
                - 使用set_text方法进行文本输入
                - 输入前会自动清空原有内容
                - 支持中文、英文、数字、特殊字符
            
            使用场景：
                - 表单填写
                - 搜索框输入
                - 文本编辑
                - 用户名密码输入
            
            使用示例：
                >>> view.input_text({"text": "用户名"}, "testuser")
                >>> view.input_text({"xpath": "//input[@id='password']"}, "123456")
        """
        try:
            # 查找元素并输入文本
            self.find_element(element).set_text(text)
            self.test.debugLog("成功输入%s" % str(text))
        except Exception as e:
            self.test.errorLog("无法输入%s" % str(text))
            raise e

    def clear_text(self, system, element):
        """
            清空文本
            
            清空指定元素中的文本内容。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "输入框", "resourceId": "com.app:id/input"}
                    - XPath定位：{"xpath": "//input[@type='text']"}
            
            Raises:
                Exception: 当元素不存在或清空失败时抛出异常
            
            Note:
                - Android XPath定位使用特殊的快速输入法清空
                - 其他情况使用标准clear_text方法
                - 清空后元素仍保持焦点状态
            
            使用场景：
                - 重新输入前清空原内容
                - 清除搜索框内容
                - 重置表单字段
                - 删除错误输入
            
            使用示例：
                >>> view.clear_text("android", {"text": "搜索框"})
                >>> view.clear_text("ios", {"xpath": "//input[@placeholder='请输入']"})
        """
        try:
            ele = self.find_element(element)
            if system == "android" and len(element) == 1 and "xpath" in element:
                # Android XPath定位：使用快速输入法清空
                xe = ele.get()
                ele._d.set_fastinput_ime()
                xe.click()
                ele._parent._d.set_fastinput_ime()
                ele._parent._d.clear_text()
            else:
                # 标准清空方法
                ele.clear_text()
            self.test.debugLog("成功清空")
        except Exception as e:
            self.test.errorLog("无法清空")
            raise e

    def scroll_to_ele(self, system, element, direction):
        """
            滑动到元素出现
            
            滑动页面直到指定元素可见。支持XPath和属性定位，支持四个方向的滑动。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 目标元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "目标文本", "resourceId": "com.app:id/item"}
                    - XPath定位：{"xpath": "//android.widget.TextView[@text='目标']"}
                direction (str): 滑动方向（"up", "down", "left", "right"）
            
            Raises:
                Exception: 当元素不存在或滑动失败时抛出异常
            
            Note:
                - Android XPath定位：使用XPath.scroll_to方法
                - Android 属性定位：使用scrollable容器的forward/backward方法
                - iOS：使用元素的scroll方法
                - 垂直滑动：up使用forward，down使用backward
                - 水平滑动：left使用horiz.forward，right使用horiz.backward
            
            使用场景：
                - 长列表中查找元素
                - 页面滚动到特定内容
                - 横向滚动到目标区域
                - 自动定位页面元素
            
            使用示例：
                >>> view.scroll_to_ele("android", {"text": "目标文本"}, "down")
                >>> view.scroll_to_ele("ios", {"name": "按钮"}, "up")
                >>> view.scroll_to_ele("android", {"xpath": "//button[@text='确定']"}, "up")
        """
        try:
            if system == "android":
                if "xpath" in element:
                    # Android XPath定位：使用XPath滚动方法
                    XPath(self.device).scroll_to(element["xpath"], direction)
                elif direction == "up":
                    # Android 属性定位：向上滚动（forward）
                    self.device(scrollable=True).forward.to(**element)
                elif direction == "down":
                    # Android 属性定位：向下滚动（backward）
                    self.device(scrollable=True).backward.to(**element)
                elif direction == "left":
                    # Android 属性定位：向左水平滚动
                    self.device(scrollable=True).horiz.forward.to(**element)
                else:
                    # Android 属性定位：向右水平滚动
                    self.device(scrollable=True).horiz.backward.to(**element)
            else:
                # iOS：使用元素的scroll方法
                self.find_element(element).scroll(direction)
            self.test.debugLog("成功滑动到元素出现")
        except Exception as e:
            self.test.errorLog("无法滑动到元素出现")
            raise e

    def pinch_in(self, system, element):
        """
            缩小手势
            
            在指定元素上执行缩小（pinch in）手势操作。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 目标元素定位信息
                    Android仅支持属性定位：{"resourceId": "com.app:id/image"}
                    iOS支持多种定位方式
            
            Raises:
                Exception: 当元素不存在或缩小失败时抛出异常
            
            Note:
                - Android：使用pinch_in()方法，仅支持属性定位
                - iOS：使用pinch(0.5, -1)方法，支持多种定位
                - 缩小操作通常用于图片、地图等可缩放元素
                - Android的XPath定位不支持此操作
            
            使用场景：
                - 图片缩小查看
                - 地图缩小显示
                - 网页内容缩小
                - 文档视图缩放
            
            使用示例：
                >>> view.pinch_in("android", {"resourceId": "imageView"})
                >>> view.pinch_in("ios", {"name": "地图"})
        """
        try:
            if system == "android":
                # Android：在元素上执行缩小手势（仅支持属性定位）
                self.find_element(element).pinch_in()
            else:
                # iOS：执行缩小手势
                self.find_element(element).pinch(0.5, -1)
            self.test.debugLog("成功缩小")
        except Exception as e:
            self.test.errorLog("无法缩小")
            raise e

    def pinch_out(self, system, element):
        """
            放大手势
            
            在指定元素上执行放大（pinch out）手势操作。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 目标元素定位信息
                    Android仅支持属性定位：{"resourceId": "com.app:id/image"}
                    iOS支持多种定位方式
            
            Raises:
                Exception: 当元素不存在或放大失败时抛出异常
            
            Note:
                - Android：使用pinch_out()方法，仅支持属性定位
                - iOS：使用pinch(2, 1)方法，支持多种定位
                - 放大操作通常用于图片、地图等可缩放元素
                - Android的XPath定位不支持此操作
            
            使用场景：
                - 图片放大查看
                - 地图放大显示
                - 网页内容放大
                - 文档细节查看
            
            使用示例：
                >>> view.pinch_out("android", {"resourceId": "imageView"})
                >>> view.pinch_out("ios", {"name": "照片"})
        """
        try:
            if system == "android":
                # Android：在元素上执行放大手势（仅支持属性定位）
                self.find_element(element).pinch_out()
            else:
                # iOS：执行放大手势
                self.find_element(element).pinch(2, 1)
            self.test.debugLog("成功放大")
        except Exception as e:
            self.test.errorLog("无法放大")
            raise e

    def wait(self, element, second):
        """
            等待元素出现
            
            等待指定元素在页面上出现，超时则抛出异常。
            
            Args:
                element (dict): 目标元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "按钮", "resourceId": "com.app:id/btn"}
                    - XPath定位：{"xpath": "//button[@text='确定']"}
                second (float): 等待超时时间（秒）
            
            Raises:
                ElementNotFoundError: 当等待超时元素仍未出现时抛出
            
            Note:
                - 使用find_element方法查找元素
                - 调用元素的wait方法进行等待
                - 等待期间会持续检查元素是否存在
                - 支持所有类型的元素定位方式
            
            使用场景：
                - 等待页面加载完成
                - 等待异步内容显示
                - 等待动画效果结束
                - 等待网络请求完成后的元素显示
            
            使用示例：
                >>> view.wait({"text": "加载完成"}, 10)
                >>> view.wait({"name": "确定按钮"}, 5)
                >>> view.wait({"xpath": "//div[@class='content']"}, 15)
        """
        try:
            if self.find_element(element).wait(timeout=second):
                self.test.debugLog("成功等待元素出现")
            else:
                self.test.errorLog("等待元素出现失败 元素不存在")
                raise ElementNotFoundError("element not exists")
        except ElementNotFoundError as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法等待元素出现")
            raise e

    def wait_gone(self, system, element, second):
        """
            等待元素消失
            
            等待指定元素从页面上消失，超时则抛出异常。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
                element (dict): 目标元素定位信息
                    支持的定位方式：
                    - 属性定位：{"text": "加载中", "resourceId": "com.app:id/loading"}
                    - XPath定位：{"xpath": "//div[@class='loading']"}
                second (float): 等待超时时间（秒）
            
            Raises:
                ElementNotDisappearError: 当等待超时元素仍未消失时抛出
            
            Note:
                - Android：使用wait_gone方法，返回布尔值
                - iOS：使用wait_gone方法，设置raise_error=False
                - 等待期间会持续检查元素是否消失
                - 支持所有类型的元素定位方式
            
            使用场景：
                - 等待加载动画消失
                - 等待弹窗关闭
                - 等待临时提示消失
                - 等待过渡动画结束
            
            使用示例：
                >>> view.wait_gone("android", {"text": "加载中..."}, 10)
                >>> view.wait_gone("ios", {"name": "提示弹窗"}, 5)
                >>> view.wait_gone("android", {"xpath": "//div[@class='spinner']"}, 15)
        """
        try:
            if system == "android":
                res = self.find_element(element).wait_gone(timeout=second)
            else:
                res = self.find_element(element).wait_gone(timeout=second, raise_error=False)
            if res:
                self.test.debugLog("成功等待元素消失")
            else:
                self.test.errorLog("等待元素消失失败 元素仍存在")
                raise ElementNotDisappearError("element exists")
        except ElementNotDisappearError as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法等待元素消失")
            raise e

    def drag_to_ele(self, start_element, end_element):
        """
            拖动到元素
            
            将源元素拖动到目标元素位置。Android专属功能，仅支持属性定位。
            
            Args:
                start_element (dict): 源元素定位信息
                    仅支持属性定位：{"text": "拖拽项", "resourceId": "com.app:id/item"}
                end_element (dict): 目标元素定位信息
                    仅支持属性定位：{"text": "放置区", "resourceId": "com.app:id/drop_zone"}
            
            Raises:
                Exception: 当源元素或目标元素不存在，或拖拽失败时抛出异常
            
            Note:
                - Android专属功能，iOS不支持
                - 仅支持属性定位，不支持XPath定位
                - 使用**end_element解包参数传递
                - 需要确保源元素支持拖拽操作
                - 需要确保目标元素支持放置操作
            
            使用场景：
                - 文件拖拽到文件夹
                - 列表项重新排序
                - 拖拽式界面操作
                - Android应用内的拖拽功能
            
            使用示例：
                >>> view.drag_to_ele({"text": "文件A"}, {"text": "文件夹B"})
                >>> view.drag_to_ele({"resourceId": "item1"}, {"resourceId": "dropzone"})
        """
        try:
            self.find_element(start_element).drag_to(**end_element)
            self.test.debugLog("成功拖动到元素")
        except Exception as e:
            self.test.errorLog("无法拖动到元素")
            raise e

    def drag_to_coord(self, element, x, y):
        """
            拖动到坐标
            
            将元素拖动到指定坐标位置。Android专属功能，仅支持属性定位。
            
            Args:
                element (dict): 源元素定位信息
                    仅支持属性定位：{"text": "拖拽项", "resourceId": "com.app:id/item"}
                x (float): 目标X坐标，支持百分比（0-1）或绝对像素值
                y (float): 目标Y坐标，支持百分比（0-1）或绝对像素值
            
            Raises:
                Exception: 当源元素不存在或拖拽失败时抛出异常
            
            Note:
                - Android专属功能，iOS不支持
                - 仅支持属性定位，不支持XPath定位
                - 坐标支持百分比和绝对值
                - 拖拽轨迹是直线路径
                - 拖拽速度由系统默认设置决定
            
            使用场景：
                - 精确位置拖拽
                - 拖拽到空白区域
                - 坐标定位的拖拽操作
                - Android应用内的精确拖拽
            
            使用示例：
                >>> view.drag_to_coord({"text": "图标"}, 0.5, 0.3)    # 拖拽到屏幕中央偏上
                >>> view.drag_to_coord({"resourceId": "slider"}, 200, 300)  # 拖拽到绝对坐标
        """
        try:
            self.find_element(element).drag_to(x, y)
            self.test.debugLog("成功拖动到坐标")
        except Exception as e:
            self.test.errorLog("无法拖动到坐标")
            raise e

    def drag_coord(self, fx, fy, tx, ty):
        """
            坐标拖动
            
            从起始坐标拖动到目标坐标。Android专属功能。
            
            Args:
                fx (float): 起始X坐标，支持百分比（0-1）或绝对像素值
                fy (float): 起始Y坐标，支持百分比（0-1）或绝对像素值
                tx (float): 目标X坐标，支持百分比（0-1）或绝对像素值
                ty (float): 目标Y坐标，支持百分比（0-1）或绝对像素值
            
            Raises:
                Exception: 当坐标无效或拖拽失败时抛出异常
            
            Note:
                - Android专属功能，iOS不支持
                - 不依赖具体元素，纯坐标操作
                - 坐标支持百分比和绝对值
                - 拖拽速度由系统默认设置决定
                - 拖拽轨迹是直线路径
            
            使用场景：
                - 无法定位元素的拖拽
                - 精确坐标拖拽
                - 自定义手势操作
                - 屏幕区域拖拽
                - 复杂拖拽路径的起始操作
            
            使用示例：
                >>> view.drag_coord(0.2, 0.5, 0.8, 0.5)    # 水平拖拽（百分比）
                >>> view.drag_coord(100, 200, 300, 400)     # 对角拖拽（绝对坐标）
        """
        try:
            self.device.drag(fx, fy, tx, ty)
            self.test.debugLog("成功坐标拖动")
        except Exception as e:
            self.test.errorLog("无法坐标拖动")
            raise e

    def swipe_ele(self, element, direction):
        """
            元素内滑动
            
            在指定元素内部进行滑动操作。Android专属功能，仅支持属性定位。
            
            Args:
                element (dict): 目标元素定位信息
                    仅支持属性定位：{"text": "列表容器", "resourceId": "com.app:id/list"}
                direction (str): 滑动方向
                    支持的方向："up"（向上）、"down"（向下）、"left"（向左）、"right"（向右）
            
            Raises:
                Exception: 当元素不存在或滑动失败时抛出异常
            
            Note:
                - Android专属功能，iOS不支持
                - 仅支持属性定位，不支持XPath定位
                - 滑动范围限制在元素内部
                - 适用于可滚动的容器元素
                - 滑动距离由系统默认设置决定
            
            使用场景:
                - 列表或网格内容滚动
                - 可滚动视图的导航
                - 容器内部的内容浏览
                - 分页或无限滚动列表
            
            使用示例:
                >>> view.swipe_ele({"resourceId": "recycler_view"}, "up")     # 列表向上滚动
                >>> view.swipe_ele({"text": "内容区域"}, "left")              # 水平滑动
        """
        try:
            # 在元素内执行指定方向的滑动
            self.find_element(element).swipe(direction)
            self.test.debugLog("成功元素内滑动")
        except Exception as e:
            self.test.errorLog("无法元素内滑动")
            raise e

    def alert_wait(self, second):
        """
            等待弹框出现
            
            等待系统弹框或对话框出现。iOS专属功能。
            
            Args:
                second (float): 等待超时时间（秒）
            
            Raises:
                Exception: 当超时时间内弹框未出现时抛出异常
            
            Note:
                - iOS专属功能，Android不支持
                - 适用于系统级弹框和应用内对话框
                - 超时后会抛出异常
                - 弹框出现后立即返回
            
            使用场景:
                - 权限请求弹框
                - 确认对话框
                - 错误提示弹框
                - 系统通知弹框
                - 应用内自定义对话框
            
            使用示例:
                >>> view.alert_wait(5)      # 等待5秒内弹框出现
                >>> view.alert_wait(15)     # 等待15秒内弹框出现
        """
        try:
            # iOS：等待弹框出现
            self.device.alert.wait(second)
            self.test.debugLog("成功等待弹框出现")
        except Exception as e:
            self.test.errorLog("无法等待弹框出现")
            raise e

    def alert_accept(self):
        """
            弹框确认
            
            点击弹框的确认按钮。iOS专属功能。
            
            Raises:
                Exception: 当弹框不存在或确认失败时抛出异常
            
            Note:
                - iOS专属功能，Android不支持
                - 通常对应"确定"、"允许"、"是"等按钮
                - 执行后弹框会消失
                - 需要先确保弹框已经出现
            
            使用场景:
                - 确认权限请求
                - 确认删除操作
                - 接受条款和条件
                - 确认系统提示
                - 同意应用内对话框
            
            使用示例:
                >>> view.alert_wait(5)      # 先等待弹框
                >>> view.alert_accept()     # 然后确认
        """
        try:
            # iOS：点击弹框确认按钮
            self.device.alert.accept()
            self.test.debugLog("成功弹框确认")
        except Exception as e:
            self.test.errorLog("无法弹框确认")
            raise e

    def alert_dismiss(self):
        """
            弹框取消
            
            点击弹框的取消按钮。iOS专属功能。
            
            Raises:
                Exception: 当弹框不存在或取消失败时抛出异常
            
            Note:
                - iOS专属功能，Android不支持
                - 通常对应"取消"、"拒绝"、"否"等按钮
                - 执行后弹框会消失
                - 需要先确保弹框已经出现
            
            使用场景:
                - 拒绝权限请求
                - 取消删除操作
                - 拒绝条款和条件
                - 取消系统提示
                - 关闭应用内对话框
            
            使用示例:
                >>> view.alert_wait(5)      # 先等待弹框
                >>> view.alert_dismiss()    # 然后取消
        """
        try:
            # iOS：点击弹框取消按钮
            self.device.alert.dismiss()
            self.test.debugLog("成功弹框取消")
        except Exception as e:
            self.test.errorLog("无法弹框取消")
            raise e

    def alert_click(self, name):
        """
            弹框点击
            
            点击弹框中指定名称的按钮。iOS专属功能。
            
            Args:
                name (str): 按钮名称或文本
                    例如："确定"、"取消"、"允许"、"拒绝"等
            
            Raises:
                Exception: 当弹框不存在或指定按钮不存在时抛出异常
            
            Note:
                - iOS专属功能，Android不支持
                - 按钮名称需要与弹框中显示的文本完全匹配
                - 执行后弹框会消失
                - 需要先确保弹框已经出现
                - 比accept()和dismiss()更灵活，可以点击任意按钮
            
            使用场景:
                - 点击自定义按钮
                - 多按钮弹框的精确操作
                - 特殊文本的按钮点击
                - 国际化应用的按钮处理
            
            使用示例:
                >>> view.alert_wait(5)           # 先等待弹框
                >>> view.alert_click("允许")      # 点击"允许"按钮
                >>> view.alert_click("稍后再说")   # 点击"稍后再说"按钮
        """
        try:
            # iOS：点击弹框中指定名称的按钮
            self.device.alert.click(name)
            self.test.debugLog("成功弹框点击%s" % name)
        except Exception as e:
            self.test.errorLog("无法弹框点击%s" % name)
            raise e

    def custom(self, **kwargs):
        """
            自定义代码执行
            
            执行用户提供的自定义Python代码，支持丰富的上下文环境和辅助函数。
            
            Args:
                **kwargs: 关键字参数字典，包含以下字段：
                    code (str): 要执行的Python代码字符串
                        支持任何有效的Python代码，包括：
                        - 变量赋值和计算
                        - 函数调用和条件判断
                        - 循环和异常处理
                        - 导入模块
                        - 复杂的业务逻辑
                    element (dict): 元素定位信息，在代码中可直接使用
                    data (any): 自定义数据，在代码中可直接使用
                    trans (str): 操作描述，用于日志记录
            
            Raises:
                UiObjectNotFoundError: Android元素未找到异常
                WDAElementNotFoundError: iOS元素未找到异常
                Exception: 其他代码执行异常，包括语法错误、运行时错误等
            
            Warning:
                - 此方法使用exec()执行任意代码，存在安全风险
                - 应仅在受信任的环境中使用
                - 代码在受控的局部作用域中执行
                - 执行的代码可能影响测试环境的状态
            
            Note:
                - 提供丰富的执行环境，包括device、test、element、data等变量
                - 重定义了print函数，输出会重定向到测试日志
                - 提供sys_get和sys_put函数用于参数和变量管理
                - 支持获取和设置公共参数、关联变量
                - 异常处理区分UI元素异常和其他异常
            
            可用的内置变量和函数：
                - device: 设备操作对象
                - test: 测试实例对象
                - element: 传入的元素定位信息
                - data: 传入的自定义数据
                - print(): 重定向的打印函数
                - sys_get(name): 获取公共参数或关联变量
                - sys_put(name, val, ps=False): 设置变量（ps=True设置公共参数）
            
            使用场景：
                - 复杂的条件判断和业务逻辑
                - 动态生成测试数据和参数
                - 调用第三方API和服务
                - 自定义验证和断言逻辑
                - 临时调试和问题排查
                - 扩展测试框架功能
                - 数据处理和转换
                - 参数传递和状态管理
            
            使用示例：
                >>> # 简单计算和变量操作
                >>> view.custom(code="result = 1 + 1; sys_put('result', result)", 
                ...             trans="计算结果")
                >>> 
                >>> # 条件判断和元素操作
                >>> view.custom(code='''
                ... if device(text="登录").exists:
                ...     print("登录按钮存在")
                ...     device(text="登录").click()
                ... else:
                ...     print("登录按钮不存在")
                ... ''', trans="条件登录")
                >>> 
                >>> # 循环操作和数据处理
                >>> view.custom(code='''
                ... for i in range(3):
                ...     device.click(0.5, 0.5)
                ...     test.sleep(1)
                ...     print(f"第{i+1}次点击完成")
                ... ''', trans="循环点击")
                >>> 
                >>> # 参数获取和设置
                >>> view.custom(code='''
                ... username = sys_get("username")
                ... device(resourceId="username").set_text(username)
                ... sys_put("login_time", time.time())
                ... ''', trans="参数化登录")
        """
        code = kwargs["code"]
        names = locals()
        names["element"] = kwargs["element"]
        names["data"] = kwargs["data"]
        names["device"] = self.device
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
        except UiObjectNotFoundError as e:
            raise e
        except WDAElementNotFoundError as e:
            raise e
        except Exception as e:
            self.test.errorLog("无法执行 %s" % kwargs["trans"])
            raise e
