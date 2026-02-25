import json


class AppOperationCollector:
    """
    移动应用操作数据收集器
    
    负责收集和解析移动应用自动化测试中的操作配置数据，包括操作类型、
    目标系统、元素定位、操作数据等信息。支持iOS和Android平台的
    各种UI操作和元素定位方式。
    
    主要功能：
        - 收集操作基本信息（ID、类型、名称等）
        - 解析元素定位配置（支持多种定位方式）
        - 处理操作数据和代码配置
        - 统一数据格式便于后续处理
    
    支持的操作类型：
        - 点击操作（click、tap）
        - 输入操作（input、sendKeys）
        - 滑动操作（swipe、scroll）
        - 等待操作（wait、sleep）
        - 断言操作（assert、verify）
        - 自定义代码操作
    
    支持的定位方式：
        - ID定位：通过元素ID定位
        - XPath定位：通过XPath表达式定位
        - 属性定位：通过元素属性定位
        - 谓词定位：通过NSPredicate定位（iOS）
        - 类链定位：通过ClassChain定位（iOS）
        - 坐标定位：通过屏幕坐标定位
    
    支持的平台：
        - iOS：支持XCUITest框架的所有定位方式
        - Android：支持UiAutomator2框架的所有定位方式
        - 跨平台：统一的操作接口和数据格式
    
    Attributes:
        id (str): 操作唯一标识符
        opt_type (str): 操作类型（click、input、swipe等）
        opt_system (str): 目标操作系统（iOS、Android）
        opt_name (str): 操作名称描述
        opt_trans (str): 操作转换配置
        opt_element (dict): 元素定位配置字典
        opt_data (dict): 操作数据配置
        opt_code (str): 自定义操作代码
    
    使用示例：:
        # 创建操作收集器
        collector = AppOperationCollector()
        
        # 收集操作数据
        ui_data = {
            "operationId": "login_click",
            "operationType": "click",
            "operationSystem": "iOS",
            "operationElement": {
                "login_btn": {
                    "by": "id",
                    "expression": "login_button"
                }
            }
        }
        collector.collect(ui_data)
        
        # 获取收集的数据
        element_config = collector.opt_element
    """

    def __init__(self):
        """
        初始化移动应用操作数据收集器
        
        初始化所有操作配置属性为None，等待后续的数据收集和解析。
        """
        self.id = None                    # 操作唯一标识符
        self.opt_type = None             # 操作类型
        self.opt_system = None           # 目标操作系统
        self.opt_name = None             # 操作名称描述
        self.opt_trans = None            # 操作转换配置
        self.opt_element = None          # 元素定位配置字典
        self.opt_data = None             # 操作数据配置
        self.opt_code = None             # 自定义操作代码

    @staticmethod
    def __parse(ui_data: dict, name):
        """
        解析UI数据中的指定字段
        
        从UI操作数据字典中安全地提取指定字段的值，如果字段不存在则返回None。
        
        Args:
            ui_data (dict): UI操作数据字典
            name (str): 要提取的字段名称
        
        Returns:
            Any: 字段值，如果字段不存在则返回None
        
        注意事项：
            - 使用安全的字典访问方式，避免KeyError异常
            - 对于不存在的字段返回None而不是抛出异常
        """
        if name not in ui_data:
            return None
        return ui_data.get(name)

    def collect_id(self, ui_data):
        """
        收集操作ID
        
        从UI数据中提取操作的唯一标识符，用于区分不同的操作步骤。
        
        Args:
            ui_data (dict): UI操作数据字典
        """
        self.id = AppOperationCollector.__parse(ui_data, "operationId")

    def collect_opt_type(self, ui_data):
        """
        收集操作类型
        
        从UI数据中提取操作类型，如click、input、swipe等。
        
        Args:
            ui_data (dict): UI操作数据字典
        
        支持的操作类型：
            - click: 点击操作
            - input: 输入文本
            - swipe: 滑动操作
            - wait: 等待操作
            - assert: 断言验证
            - custom: 自定义代码
        """
        self.opt_type = AppOperationCollector.__parse(ui_data, "operationType")

    def collect_opt_system(self, ui_data):
        """
        收集目标操作系统
        
        从UI数据中提取目标操作系统类型，用于确定使用的自动化框架。
        
        Args:
            ui_data (dict): UI操作数据字典
        
        支持的系统类型：
            - iOS: 使用XCUITest框架
            - Android: 使用UiAutomator2框架
        """
        self.opt_system = AppOperationCollector.__parse(ui_data, "operationSystem")

    def collect_opt_name(self, ui_data):
        """
        收集操作名称
        
        从UI数据中提取操作的描述性名称，用于测试报告和日志记录。
        
        Args:
            ui_data (dict): UI操作数据字典
        """
        self.opt_name = AppOperationCollector.__parse(ui_data, "operationName")

    def collect_opt_trans(self, ui_data):
        """
        收集操作转换配置
        
        从UI数据中提取操作转换相关的配置信息。
        
        Args:
            ui_data (dict): UI操作数据字典
        """
        self.opt_trans = AppOperationCollector.__parse(ui_data, "operationTrans")

    def collect_opt_code(self, ui_data):
        """
        收集自定义操作代码
        
        从UI数据中提取自定义的操作代码，用于执行复杂的自定义操作。
        
        Args:
            ui_data (dict): UI操作数据字典
        
        使用场景：
            - 复杂的业务逻辑操作
            - 平台特定的操作
            - 需要编程实现的操作
        """
        self.opt_code = AppOperationCollector.__parse(ui_data, "operationCode")

    def collect_opt_element(self, ui_data):
        """
        收集元素定位配置
        
        从UI数据中提取元素定位配置，支持多种定位方式，并将其转换为
        统一的格式便于后续的元素查找和操作。
        
        Args:
            ui_data (dict): UI操作数据字典
        
        支持的定位方式：
            - prop: 属性定位，通过元素属性进行定位
            - pred: 谓词定位，使用NSPredicate表达式（iOS）
            - class: 类链定位，使用ClassChain表达式（iOS）
            - id: ID定位，通过元素ID进行定位
            - xpath: XPath定位，通过XPath表达式进行定位
            - name: 名称定位，通过元素名称进行定位
            - accessibility_id: 可访问性ID定位
        
        元素配置格式：
            {
                "element_name": {
                    "by": "id",
                    "expression": "login_button"
                }
            }
        
        属性定位特殊处理：
            当定位方式为"prop"时，expression字段包含JSON格式的属性列表：
            [
                {"propName": "text", "propValue": "登录"},
                {"propName": "enabled", "propValue": "true"}
            ]
        
        转换后的格式：
            {
                "element_name": {
                    "text": "登录",
                    "enabled": "true"
                }
            }
        
        注意事项：
            - 空的元素配置会被设置为None
            - 属性定位会解析JSON并展开为键值对
            - 谓词和类链定位会保持原始表达式
            - 其他定位方式使用统一的键值对格式
        """
        opt_element = AppOperationCollector.__parse(ui_data, "operationElement")
        if opt_element is None or len(opt_element) == 0:
            self.opt_element = None
        else:
            elements = {}
            for name, element in opt_element.items():
                props = {}
                if element["by"].lower() == "prop":
                    # 属性定位：解析JSON格式的属性列表
                    for prop in json.loads(element["expression"]):
                        props[prop["propName"]] = prop["propValue"]
                elif element["by"].lower() == "pred":
                    # 谓词定位：使用NSPredicate表达式（iOS专用）
                    props["predicate"] = element["expression"]
                elif element["by"].lower() == "class":
                    # 类链定位：使用ClassChain表达式（iOS专用）
                    props["classChain"] = element["expression"]
                else:
                    # 其他定位方式：使用统一的键值对格式
                    props[element["by"].lower()] = element["expression"]
                elements[name] = props
            self.opt_element = elements

    def collect_opt_data(self, ui_data):
        """
        收集操作数据配置
        
        从UI数据中提取操作相关的数据配置，如输入文本、滑动坐标、
        等待时间等操作参数。
        
        Args:
            ui_data (dict): UI操作数据字典
        
        操作数据类型：
            - 输入操作：文本内容、清除标志等
            - 滑动操作：起始坐标、结束坐标、持续时间等
            - 等待操作：等待时间、等待条件等
            - 断言操作：期望值、比较方式等
        
        数据格式示例：
            {
                "text": "用户名",           # 输入文本
                "clear": true,             # 是否清除原有内容
                "timeout": 10              # 超时时间（秒）
            }
        
        注意事项：
            - 空的数据配置会被设置为None
            - 数据格式根据操作类型而变化
            - 支持复杂的嵌套数据结构
        """
        opt_data = AppOperationCollector.__parse(ui_data, "operationData")
        if opt_data is None or len(opt_data) == 0:
            self.opt_data = None
        else:
            self.opt_data = opt_data

    def collect(self, ui_data):
        """
        收集所有操作配置数据
        
        按照固定顺序收集UI操作的所有配置数据，包括基本信息、
        元素定位、操作数据和自定义代码等。
        
        Args:
            ui_data (dict): 完整的UI操作数据字典
        
        收集顺序：
            1. 操作ID - 唯一标识符
            2. 操作类型 - 确定操作行为
            3. 操作系统 - 确定自动化框架
            4. 操作名称 - 描述性信息
            5. 操作转换 - 转换配置
            6. 元素定位 - 目标元素配置
            7. 操作数据 - 操作参数
            8. 操作代码 - 自定义代码
        
        使用示例：:
            ui_data = {
                "operationId": "login_001",
                "operationType": "click",
                "operationSystem": "iOS",
                "operationName": "点击登录按钮",
                "operationElement": {
                    "login_btn": {
                        "by": "id",
                        "expression": "login_button"
                    }
                }
            }
            collector.collect(ui_data)
        
        注意事项：
            - 收集顺序固定，确保数据依赖关系正确
            - 所有字段都是可选的，不存在的字段会被设置为None
            - 收集完成后可以通过属性访问各个配置项
        """
        self.collect_id(ui_data)                # 收集操作ID
        self.collect_opt_type(ui_data)          # 收集操作类型
        self.collect_opt_system(ui_data)        # 收集目标操作系统
        self.collect_opt_name(ui_data)          # 收集操作名称
        self.collect_opt_trans(ui_data)         # 收集操作转换配置
        self.collect_opt_element(ui_data)       # 收集元素定位配置
        self.collect_opt_data(ui_data)          # 收集操作数据配置
        self.collect_opt_code(ui_data)          # 收集自定义操作代码

