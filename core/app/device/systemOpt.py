import sys
from time import sleep

from uiautomator2 import UiObjectNotFoundError
from wda import WDAElementNotFoundError
from core.app.device import Operation


class System(Operation):
    """
        系统级操作类
        
        继承自Operation基类，提供移动设备的系统级操作功能。
        支持Android和iOS两个平台的系统操作，包括应用管理、手势操作、
        按键控制、屏幕管理、等待操作和自定义代码执行等。
        
        主要功能分类：
            - 应用管理：启动、关闭应用
            - 手势操作：滑动（上下左右）
            - 按键控制：Home键、返回键、系统按键
            - 屏幕管理：截图、亮屏、息屏
            - 等待操作：强制等待、隐式等待
            - 自定义操作：执行自定义Python代码
        
        平台兼容性：
            - Android：基于uiautomator2协议
            - iOS：基于WebDriverAgent协议
            - 自动适配不同平台的API差异
        
        继承关系：
            System -> Operation -> object
        
        使用示例：
            >>> system = System(test, device)
            >>> system.start_app("com.example.app")
            >>> system.swipe_left("android")
            >>> system.screenshot("test_screenshot")
    """

    def start_app(self, app_id):
        """
            启动指定应用
            
            通过应用包名或Bundle ID启动目标应用。
            
            Args:
                app_id (str): 应用标识符
                    - Android: 应用包名，如"com.android.settings"
                    - iOS: Bundle ID，如"com.apple.Preferences"
            
            Raises:
                Exception: 当应用启动失败时抛出异常
            
            Note:
                - 如果应用已经在运行，会将其带到前台
                - 支持系统应用和第三方应用
                - 启动时间取决于应用大小和设备性能
            
            使用示例：
                >>> system.start_app("com.android.settings")
                >>> system.start_app("com.apple.Preferences")
        """
        try:
            # 调用设备驱动器启动应用
            self.device.app_start(app_id)
            self.test.debugLog("成功执行启动应用")
        except Exception as e:
            # 注意：这里的错误日志信息有误，应该是"无法执行启动应用"
            self.test.errorLog("无法执行启动应用")
            raise e

    def close_app(self, app_id):
        """
            关闭指定应用
            
            强制停止目标应用的运行。
            
            Args:
                app_id (str): 应用标识符
                    - Android: 应用包名
                    - iOS: Bundle ID
            
            Raises:
                Exception: 当应用关闭失败时抛出异常
            
            Note:
                - 会强制终止应用进程
                - 应用数据可能会丢失（如未保存的内容）
                - 某些系统应用可能无法关闭
            
            使用示例：
                >>> system.close_app("com.example.app")
        """
        try:
            # 调用设备驱动器停止应用
            self.device.app_stop(app_id)
            self.test.debugLog("成功执行关闭应用")
        except Exception as e:
            self.test.errorLog("无法执行关闭应用")
            raise e

    def swipe_left(self, system):
        """
            执行左滑手势
            
            在屏幕上执行从右向左的滑动手势。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当滑动操作失败时抛出异常
            
            Note:
                - Android使用swipe_ext方法
                - iOS使用swipe_left方法
                - 滑动距离和速度由设备驱动器默认设置
            
            使用场景：
                - 翻页操作（如相册、新闻列表）
                - 切换标签页
                - 侧边栏收起
            
            使用示例：
                >>> system.swipe_left("android")
        """
        try:
            if system == "android":
                # Android平台：使用扩展滑动方法
                self.device.swipe_ext("left")
            else:
                # iOS平台：使用专用左滑方法
                self.device.swipe_left()
            self.test.debugLog("成功执行左滑")
        except Exception as e:
            self.test.errorLog("无法执行左滑")
            raise e

    def swipe_right(self, system):
        """
            执行右滑手势
            
            在屏幕上执行从左向右的滑动手势。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当滑动操作失败时抛出异常
            
            使用场景：
                - 返回上一页
                - 切换到上一个标签页
                - 侧边栏展开
                - 抽屉菜单打开
            
            使用示例：
                >>> system.swipe_right("android")
        """
        try:
            if system == "android":
                # Android平台：使用扩展滑动方法
                self.device.swipe_ext("right")
            else:
                # iOS平台：使用专用右滑方法
                self.device.swipe_right()
            self.test.debugLog("成功执行右滑")
        except Exception as e:
            self.test.errorLog("无法执行右滑")
            raise e

    def swipe_up(self, system):
        """
            执行上滑手势
            
            在屏幕上执行从下向上的滑动手势。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当滑动操作失败时抛出异常
            
            使用场景：
                - 页面向上滚动
                - 打开控制中心（iOS）
                - 显示最近任务（Android）
                - 刷新页面内容
            
            使用示例：
                >>> system.swipe_up("ios")
        """
        try:
            if system == "android":
                # Android平台：使用扩展滑动方法
                self.device.swipe_ext("up")
            else:
                # iOS平台：使用专用上滑方法
                self.device.swipe_up()
            self.test.debugLog("成功执行上滑")
        except Exception as e:
            self.test.errorLog("无法执行上滑")
            raise e

    def swipe_down(self, system):
        """
            执行下滑手势
            
            在屏幕上执行从上向下的滑动手势。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当滑动操作失败时抛出异常
            
            使用场景：
                - 页面向下滚动
                - 打开通知栏（Android）
                - 下拉刷新
                - 显示搜索框
            
            使用示例：
                >>> system.swipe_down("android")
        """
        try:
            if system == "android":
                # Android平台：使用扩展滑动方法
                self.device.swipe_ext("down")
            else:
                # iOS平台：使用专用下滑方法
                self.device.swipe_down()
            self.test.debugLog("成功执行下滑")
        except Exception as e:
            self.test.errorLog("无法执行下滑")
            raise e

    def home(self, system):
        """
            返回系统首页
            
            执行Home键操作，返回到设备的主屏幕。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当Home键操作失败时抛出异常
            
            Note:
                - Android使用keyevent方法模拟Home键
                - iOS使用home方法直接调用
                - 会关闭当前应用并返回桌面
            
            使用场景：
                - 快速返回桌面
                - 退出当前应用
                - 重置应用状态
            
            使用示例：
                >>> system.home("android")
        """
        try:
            if system == "android":
                # Android平台：发送Home键事件
                self.device.keyevent("home")
            else:
                # iOS平台：调用Home方法
                self.device.home()
            self.test.debugLog("成功执行返回系统首页")
        except Exception as e:
            self.test.errorLog("无法执行返回系统首页")
            raise e

    def back(self):
        """
            系统返回操作（Android专用）
            
            执行返回键操作，模拟Android设备的物理返回键。
            
            Raises:
                Exception: 当返回键操作失败时抛出异常
            
            Note:
                - 仅适用于Android设备
                - iOS设备没有物理返回键，需要使用应用内的返回按钮
                - 会触发当前页面的返回逻辑
            
            使用场景：
                - 返回上一个页面
                - 关闭弹框或对话框
                - 退出当前界面
            
            使用示例：
                >>> system.back()  # 仅在Android设备上使用
        """
        try:
            # 发送返回键事件（Android专用）
            self.device.keyevent("back")
            self.test.debugLog("成功执行返回")
        except Exception as e:
            self.test.errorLog("无法执行返回")
            raise e

    def press(self, keycode):
        """
            按下系统按键
            
            执行指定的系统按键操作。
            
            Args:
                keycode (str): 按键代码
                    常用按键：
                    - "home": Home键
                    - "back": 返回键（Android）
                    - "menu": 菜单键
                    - "power": 电源键
                    - "volume_up": 音量加
                    - "volume_down": 音量减
            
            Raises:
                Exception: 当按键操作失败时抛出异常
            
            Note:
                - 不同平台支持的按键可能不同
                - 某些按键可能需要特殊权限
            
            使用示例：
                >>> system.press("volume_up")
                >>> system.press("power")
        """
        try:
            # 执行按键操作
            self.device.press(keycode)
            self.test.debugLog("成功执行按下系统键位: %s" % keycode)
        except Exception as e:
            self.test.errorLog("无法执行按下系统键位: %s" % keycode)
            raise e

    def screenshot(self, name):
        """
            屏幕截图
            
            捕获当前屏幕内容并保存为图片文件。
            
            Args:
                name (str): 截图文件名（不包含扩展名）
            
            Raises:
                Exception: 当截图操作失败时抛出异常
            
            Note:
                - 截图格式为原始格式（raw）
                - 文件保存路径由测试框架管理
                - 截图包含整个屏幕内容
            
            使用场景：
                - 测试结果记录
                - 错误现场保存
                - 界面状态验证
                - 测试报告生成
            
            使用示例：
                >>> system.screenshot("login_page")
                >>> system.screenshot("error_dialog")
        """
        try:
            # 获取屏幕截图（原始格式）
            screenshot = self.device.screenshot(format='raw')
            # 保存截图文件
            self.test.saveScreenShot(name, screenshot)
            self.test.debugLog("成功执行屏幕截图")
        except Exception as e:
            self.test.errorLog("无法执行屏幕截图")
            raise e

    def screen_on(self, system):
        """
            设备亮屏
            
            唤醒设备屏幕，使设备从休眠状态变为活跃状态。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当亮屏操作失败时抛出异常
            
            Note:
                - Android使用screen_on方法
                - iOS使用unlock方法
                - 可能需要额外的解锁操作（如密码、指纹等）
            
            使用场景：
                - 测试开始前确保设备可用
                - 从休眠状态恢复测试
                - 模拟用户唤醒设备的操作
            
            使用示例：
                >>> system.screen_on("android")
        """
        try:
            if system == "android":
                # Android平台：点亮屏幕
                self.device.screen_on()
            else:
                # iOS平台：解锁设备
                self.device.unlock()
            self.test.debugLog("成功执行亮屏")
        except Exception as e:
            self.test.errorLog("无法执行亮屏")
            raise e

    def screen_off(self, system):
        """
            设备息屏
            
            关闭设备屏幕，使设备进入休眠状态。
            
            Args:
                system (str): 操作系统类型（"android" 或 "ios"）
            
            Raises:
                Exception: 当息屏操作失败时抛出异常
            
            Note:
                - Android使用screen_off方法
                - iOS使用lock方法
                - 息屏后设备进入省电模式
            
            使用场景：
                - 模拟用户锁屏操作
                - 测试应用后台行为
                - 节省设备电量
            
            使用示例：
                >>> system.screen_off("ios")
        """
        try:
            if system == "android":
                # Android平台：关闭屏幕
                self.device.screen_off()
            else:
                # iOS平台：锁定设备
                self.device.lock()
            self.test.debugLog("成功执行息屏")
        except Exception as e:
            self.test.errorLog("无法执行息屏")
            raise e

    def sleep(self, second):
        """
            强制等待指定时间
            
            暂停执行指定的秒数，用于在测试步骤之间添加延迟。
            
            Args:
                second (float): 等待时间（秒），支持小数
            
            Raises:
                Exception: 当等待操作失败时抛出异常
            
            Note:
                - 使用time.sleep()实现
                - 会阻塞当前线程
                - 支持小数秒（如0.5秒）
            
            使用场景:
                - 等待页面加载完成
                - 等待动画效果结束
                - 模拟用户思考时间
                - 避免操作过快导致的问题
            
            使用示例:
                >>> system.sleep(2)      # 等待2秒
                >>> system.sleep(0.5)    # 等待0.5秒
        """
        try:
            # 暂停执行指定时间
            sleep(second)
            self.test.debugLog("成功执行sleep %ds" % second)
        except Exception as e:
            self.test.errorLog("无法执行sleep %ds" % second)
            raise e

    def implicitly_wait(self, second):
        """
            设置隐式等待时间
            
            设置全局的隐式等待时间，当查找元素时如果元素不存在，
            会在指定时间内持续查找，直到找到元素或超时。
            
            Args:
                second (float): 隐式等待时间（秒）
            
            Raises:
                Exception: 当设置隐式等待失败时抛出异常
            
            Note:
                - 隐式等待是全局设置，影响所有元素查找操作
                - 与显式等待不同，隐式等待是自动的
                - 设置后会一直生效，直到重新设置或会话结束
                - 过长的等待时间可能影响测试执行效率
            
            使用场景:
                - 处理网络延迟
                - 等待页面元素加载
                - 提高测试稳定性
                - 减少因元素未及时出现导致的测试失败
            
            使用示例:
                >>> system.implicitly_wait(10)  # 设置10秒隐式等待
        """
        try:
            # 设置设备的隐式等待时间
            self.device.implicitly_wait(second)
            self.test.debugLog("成功执行implicitly wait %ds" % second)
        except Exception as e:
            self.test.errorLog("无法执行implicitly wait %ds" % second)
            raise e

    def custom(self, **kwargs):
        """
            执行自定义Python代码
            
            动态执行用户提供的Python代码，支持访问测试上下文、设备对象等。
            提供了丰富的内置函数用于数据存取和输出操作。
            
            Args:
                **kwargs: 关键字参数
                    - code (str): 要执行的Python代码字符串
                    - element: 元素对象（可选）
                    - data: 数据对象（可选）
                    - trans (str): 操作描述（用于日志）
            
            Raises:
                UiObjectNotFoundError: 当UI元素未找到时
                WDAElementNotFoundError: 当WDA元素未找到时
                Exception: 当代码执行失败时抛出异常
            
            内置函数:
                - print(): 重定向的打印函数，输出到测试缓冲区
                - sys_get(name): 获取公共参数或关联变量
                - sys_put(name, val, ps=False): 设置变量（ps=True设置公共参数）
            
            可用变量:
                - device: 设备驱动对象
                - test: 测试对象
                - element: 传入的元素对象
                - data: 传入的数据对象
            
            Warning:
                - 执行任意代码存在安全风险，请确保代码来源可信
                - 代码错误可能导致测试中断
            
            使用场景:
                - 实现复杂的业务逻辑
                - 数据处理和计算
                - 调用第三方库功能
                - 实现框架未覆盖的特殊操作
            
            使用示例:
                >>> system.custom(code="print('Hello World')", trans="打印消息")
                >>> system.custom(code="sys_put('result', 'success')", trans="保存结果")
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
