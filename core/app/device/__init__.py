from typing import Optional
from uiautomator2 import Device
from wda import Client, AlertAction, BaseClient


class AndroidDriver(Device):
    """
    Android设备驱动器类
    
    继承自uiautomator2.Device，提供Android设备的自动化操作功能。
    扩展了原有的元素查找功能，特别优化了XPath定位方式的处理。
    
    主要功能：
        - 元素定位：支持多种定位方式（ID、XPath、属性等）
        - 设备操作：点击、滑动、输入等基础操作
        - 应用管理：启动、关闭、安装、卸载应用
        - 系统控制：返回、菜单、最近任务等系统操作
    
    特殊处理：
        - XPath定位：直接调用xpath()方法，提高定位效率
        - 其他定位：使用父类的标准定位方法
    
    继承关系：
        AndroidDriver -> uiautomator2.Device
    
    使用示例：
        >>> driver = AndroidDriver("127.0.0.1:7555")
        >>> element = driver(xpath="//android.widget.Button[@text='登录']")
        >>> element.click()
    """
    
    def __call__(self, **kwargs):
        """
        重写父类的__call__方法，优化XPath定位处理
        
        Args:
            **kwargs: 元素定位参数，支持多种定位方式
                - xpath: XPath表达式定位
                - resourceId: 资源ID定位
                - text: 文本内容定位
                - description: 描述信息定位
                - className: 类名定位
        
        Returns:
            UiObject: 定位到的UI元素对象
        
        Note:
            - 当只有xpath参数时，直接调用xpath()方法提高效率
            - 其他情况使用父类的标准定位方法
        """
        if len(kwargs) == 1 and "xpath" in kwargs:
            # XPath定位：直接调用xpath方法，提高定位效率
            return self.xpath(kwargs["xpath"])
        else:
            # 其他定位方式：使用父类的标准方法
            return Device.__call__(self, **kwargs)

    def find_element(self, **kwargs):
        """
        查找单个元素的方法
        
        提供与__call__方法相同的功能，用于统一的元素查找接口。
        
        Args:
            **kwargs: 元素定位参数
        
        Returns:
            UiObject: 定位到的UI元素对象
        
        Note:
            - 功能与__call__方法完全相同
            - 提供更明确的方法名称，便于理解和使用
        """
        if len(kwargs) == 1 and "xpath" in kwargs:
            # XPath定位：直接调用xpath方法
            return self.xpath(kwargs["xpath"])
        else:
            # 其他定位方式：使用父类的标准方法
            return Device.__call__(self, **kwargs)


class AppleDevice(Client):
    """
    iOS设备驱动器类
    
    继承自wda.Client，提供iOS设备的自动化操作功能。
    通过WebDriverAgent协议与iOS设备进行通信，支持XCUITest框架的所有功能。
    
    主要功能：
        - 应用会话管理：启动、切换、关闭应用
        - 元素定位：支持多种iOS定位方式
        - 设备操作：点击、滑动、输入等操作
        - 系统控制：Home键、锁屏、截图等
    
    支持的定位方式：
        - ID定位：通过accessibility identifier定位
        - XPath定位：通过XPath表达式定位
        - 谓词定位：通过NSPredicate表达式定位
        - 类链定位：通过ClassChain表达式定位
        - 属性定位：通过元素属性定位
    
    继承关系：
        AppleDevice -> wda.Client -> wda.BaseClient
    
    使用示例：
        >>> device = AppleDevice("http://localhost:8100")
        >>> session = device.session("com.example.app")
        >>> element = session(name="登录")
        >>> element.tap()
    """
    
    def session(self,
                bundle_id=None,
                arguments: Optional[list] = None,
                environment: Optional[dict] = None,
                alert_action: Optional[AlertAction] = None):
        """
        创建应用会话
        
        启动指定的iOS应用并创建自动化会话，用于后续的UI操作。
        
        Args:
            bundle_id (str, optional): 应用的Bundle ID，如"com.apple.mobilesafari"
            arguments (list, optional): 应用启动参数列表
            environment (dict, optional): 应用启动环境变量字典
            alert_action (AlertAction, optional): 弹框处理策略
        
        Returns:
            Session: 应用会话对象，用于执行UI操作
        
        Note:
            - 动态添加find_element方法到Client类
            - 使用BaseClient的session方法创建会话
            - 会话创建后可以进行元素定位和操作
        
        使用示例：
            >>> session = device.session("com.example.app")
            >>> session(name="按钮").tap()
        """
        # 动态添加find_element方法到Client类
        setattr(Client, 'find_element', AppleDevice.find_element)
        # 创建应用会话
        client = BaseClient.session(self, bundle_id, arguments, environment, alert_action)
        return client

    def find_element(self, **kwargs):
        """
        查找单个元素的方法
        
        使用BaseClient的__call__方法进行元素定位。
        
        Args:
            **kwargs: 元素定位参数，支持iOS的各种定位方式
                - name: 元素名称（accessibility identifier）
                - xpath: XPath表达式
                - predicate: NSPredicate表达式
                - classChain: ClassChain表达式
                - label: 元素标签
                - value: 元素值
        
        Returns:
            Element: 定位到的UI元素对象
        
        Note:
            - 直接调用BaseClient的__call__方法
            - 支持iOS XCUITest框架的所有定位方式
        """
        return BaseClient.__call__(self, **kwargs)


def connect_device(system: str, url: str):
    """
    根据系统类型连接设备
    
    根据指定的操作系统类型创建对应的设备驱动器实例，
    用于后续的自动化操作。
    
    Args:
        system (str): 操作系统类型，支持"android"和"ios"
        url (str): 设备连接地址
            - Android: 设备IP:端口，如"127.0.0.1:7555"
            - iOS: WebDriverAgent服务地址，如"http://localhost:8100"
    
    Returns:
        AndroidDriver or AppleDevice: 对应的设备驱动器实例
    
    Note:
        - Android使用uiautomator2协议连接
        - iOS使用WebDriverAgent协议连接
        - 系统类型不区分大小写
    
    使用示例：
        >>> android_device = connect_device("android", "127.0.0.1:7555")
        >>> ios_device = connect_device("ios", "http://localhost:8100")
    """
    if system.lower() == "android":
        # 创建Android设备驱动器
        return AndroidDriver(url)
    else:
        # 创建iOS设备驱动器（默认处理）
        return AppleDevice(url)


class Operation(object):
    """
    设备操作基类
    
    提供设备操作的基础功能，包括元素定位、日志记录等。
    所有具体的操作类（如System、View、Assertion等）都继承自此类。
    
    主要功能：
        - 元素定位：统一的元素查找接口
        - 日志记录：操作过程的日志记录
        - 异常处理：统一的异常处理机制
    
    Attributes:
        device: 设备驱动器实例（AndroidDriver或AppleDevice）
        test: 测试实例，用于日志记录和上下文管理
        print: 打印函数引用
    
    使用示例：
        >>> operation = Operation(test, device)
        >>> element = operation.find_element({"xpath": "//button[@text='登录']"})
    """
    
    def __init__(self, test, device):
        """
        初始化操作基类
        
        Args:
            test: 测试实例，提供日志记录和上下文管理功能
            device: 设备驱动器实例，用于执行具体的设备操作
        """
        self.device = device      # 设备驱动器实例
        self.test = test         # 测试实例
        self.print = print       # 打印函数引用

    def find_element(self, ele):
        """
        查找单个元素
        
        使用设备驱动器查找指定的UI元素，并记录操作日志。
        
        Args:
            ele (dict): 元素定位参数字典，包含定位方式和表达式
                例如：{"xpath": "//button[@text='登录']"}
                     {"resourceId": "com.example:id/login_btn"}
        
        Returns:
            Element: 定位到的UI元素对象
        
        Raises:
            Exception: 当元素定位失败时抛出异常
        
        Note:
            - 成功定位时记录调试日志
            - 定位失败时记录错误日志并重新抛出异常
            - 支持所有设备驱动器支持的定位方式
        
        使用示例：
            >>> element = operation.find_element({"text": "登录"})
            >>> element.click()
        """
        try:
            # 使用设备驱动器查找元素
            element = self.device.find_element(**ele)
            # 记录成功定位的调试日志
            self.test.debugLog("定位元素: %s" % str(ele))
            return element
        except Exception as e:
            # 记录定位失败的错误日志
            self.test.errorLog("定位元素出错: %s" % str(ele))
            # 重新抛出异常，由上层处理
            raise e


class ElementNotFoundError(Exception):
    """
    元素获取失败异常
    
    当无法找到指定的UI元素时抛出此异常。
    通常发生在元素定位表达式错误、元素不存在或元素尚未加载完成的情况下。
    
    使用场景：
        - 元素定位超时
        - 定位表达式错误
        - 页面未完全加载
        - 元素被其他元素遮挡
    
    处理建议：
        - 检查定位表达式是否正确
        - 增加等待时间
        - 确认页面是否已加载完成
        - 使用更精确的定位方式
    """
    pass


class ElementNotDisappearError(Exception):
    """
    元素消失失败异常
    
    当期望元素消失但元素仍然存在时抛出此异常。
    通常发生在等待元素消失的操作中，如等待加载动画结束、弹框关闭等。
    
    使用场景：
        - 等待加载动画消失超时
        - 等待弹框关闭超时
        - 等待页面跳转超时
        - 等待元素隐藏超时
    
    处理建议：
        - 增加等待超时时间
        - 检查元素是否真的会消失
        - 确认触发消失的操作是否成功
        - 使用更精确的元素定位
    """
    pass

