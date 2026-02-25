from core.app.device.viewOpt import View
from core.app.device.systemOpt import System
from core.app.device.scenarioOpt import Scenario
from core.app.device.assertionOpt import Assertion
from core.app.device.relationOpt import Relation
from core.app.device.conditionOpt import Condition


def find_system_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的系统操作函数。
    
    系统操作包括应用管理、设备控制、屏幕操作、输入操作、等待操作等基础功能。
    通过装饰器模式匹配操作名称，返回对应的操作函数。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 应用管理："启动应用", "关闭应用"
            - 设备控制："系统首页", "系统返回", "系统按键"
            - 屏幕操作："屏幕截图", "左滑", "右滑", "上滑", "下滑", "亮屏", "息屏"
            - 等待操作："强制等待", "隐式等待"
            - 其他操作："自定义"
    
    Returns:
        function or None: 匹配的操作函数，如果未找到匹配的操作则返回None
    
    Note:
        - 使用装饰器模式进行操作名称匹配，提高代码的可读性和可维护性
        - 所有操作函数都接收test、device和**kwargs参数
        - 操作函数内部会调用System类的对应方法执行具体操作
        - 异常处理确保在匹配失败时返回None而不是抛出异常
    
    Example:
        >>> func = find_system_opt("启动应用")
        >>> if func:
        >>>     func(test, device, data={"appId": "com.example.app"})
    """
    function = None  # 存储匹配到的操作函数

    def keywords(name):
        """
        装饰器工厂函数，用于匹配操作名称。
        
        Args:
            name (str): 操作名称
        
        Returns:
            function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则将函数赋值给function变量
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("启动应用")
    def start_app(test, device, **kwargs):
        System(test, device).start_app(kwargs["data"]["appId"])

    @keywords("关闭应用")
    def close_app(test, device, **kwargs):
        System(test, device).close_app(kwargs["data"]["appId"])

    @keywords("左滑")
    def swipe_left(test, device, **kwargs):
        System(test, device).swipe_left(kwargs["system"])

    @keywords("右滑")
    def swipe_right(test, device, **kwargs):
        System(test, device).swipe_right(kwargs["system"])

    @keywords("上滑")
    def swipe_up(test, device, **kwargs):
        System(test, device).swipe_up(kwargs["system"])

    @keywords("下滑")
    def swipe_down(test, device, **kwargs):
        System(test, device).swipe_down(kwargs["system"])

    @keywords("系统首页")
    def home(test, device, **kwargs):
        System(test, device).home(kwargs["system"])

    @keywords("系统返回")
    def back(test, device, **kwargs):
        System(test, device).back()

    @keywords("系统按键")
    def press(test, device, **kwargs):
        System(test, device).press(kwargs["data"]["keycode"])

    @keywords("屏幕截图")
    def screenshot(test, device, **kwargs):
        System(test, device).screenshot(kwargs["data"]["name"])

    @keywords("亮屏")
    def screen_on(test, device, **kwargs):
        System(test, device).screen_on(kwargs["system"])

    @keywords("息屏")
    def screen_off(test, device, **kwargs):
        System(test, device).screen_off(kwargs["system"])

    @keywords("强制等待")
    def sleep(test, device, **kwargs):
        System(test, device).sleep(kwargs["data"]["second"])

    @keywords("隐式等待")
    def implicitly_wait(test, device, **kwargs):
        System(test, device).implicitly_wait(kwargs["data"]["second"])

    @keywords("自定义")
    def custom(test, device, **kwargs):
        System(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常


def find_view_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的视图操作函数。
    
    视图操作包括元素点击、输入、滑动、拖拽、等待、弹框处理等UI交互功能。
    通过装饰器模式匹配操作名称，返回对应的操作函数。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 点击操作："单击", "双击", "长按", "坐标单击", "坐标双击", "坐标长按"
            - 输入操作："输入", "清空"
            - 滑动操作："坐标滑动", "滑动到元素出现", "元素内滑动"
            - 手势操作："缩小", "放大"
            - 拖拽操作："拖动到元素", "拖动到坐标", "坐标拖动"
            - 等待操作："等待元素出现", "等待元素消失"
            - 弹框操作："等待弹框出现", "弹框确认", "弹框取消", "弹框点击"
            - 其他操作："自定义"
    
    Returns:
        function or None: 匹配的操作函数，如果未找到匹配的操作则返回None
    
    Note:
        - 使用装饰器模式进行操作名称匹配
        - 所有操作函数都接收test、device和**kwargs参数
        - 操作函数内部会调用View类的对应方法执行具体操作
        - 异常处理确保在匹配失败时返回None
    
    Example:
        >>> func = find_view_opt("单击")
        >>> if func:
        >>>     func(test, device, element={"element": element_obj})
    """
    function = None

    def keywords(name):
        def back(func):
            if name == operate_name:
                nonlocal function
                function = func
        return back

    @keywords("单击")
    def click(test, device, **kwargs):
        View(test, device).click(kwargs["element"]["element"])

    @keywords("双击")
    def double_click(test, device, **kwargs):
        View(test, device).double_click(kwargs["system"], kwargs["element"]["element"])

    @keywords("长按")
    def long_click(test, device, **kwargs):
        View(test, device).long_click(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["second"])

    @keywords("坐标单击")
    def click_coord(test, device, **kwargs):
        View(test, device).click_coord(**kwargs["data"])

    @keywords("坐标双击")
    def double_click_coord(test, device, **kwargs):
        View(test, device).double_click_coord(kwargs["system"], **kwargs["data"])

    @keywords("坐标长按")
    def long_click_coord(test, device, **kwargs):
        View(test, device).long_click_coord(kwargs["system"], **kwargs["data"])

    @keywords("坐标滑动")
    def swipe_int(test, device, **kwargs):
        View(test, device).swipe(kwargs["system"], **kwargs["data"])

    @keywords("输入")
    def input_text(test, device, **kwargs):
        View(test, device).input_text(kwargs["element"]["element"], kwargs["data"]["text"])

    @keywords("清空")
    def input_text(test, device, **kwargs):
        View(test, device).clear_text(kwargs["system"], kwargs["element"]["element"])

    @keywords("滑动到元素出现")
    def scroll_to_ele(test, device, **kwargs):
        View(test, device).scroll_to_ele(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["direction"])

    @keywords("缩小")
    def pinch_in(test, device, **kwargs):
        View(test, device).pinch_in(kwargs["system"], kwargs["element"]["element"])

    @keywords("放大")
    def pinch_out(test, device, **kwargs):
        View(test, device).pinch_out(kwargs["system"], kwargs["element"]["element"])

    @keywords("等待元素出现")
    def wait(test, device, **kwargs):
        View(test, device).wait(kwargs["element"]["element"], kwargs["data"]["second"])

    @keywords("等待元素消失")
    def wait_gone(test, device, **kwargs):
        View(test, device).wait_gone(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["second"])

    @keywords("拖动到元素")
    def drag_to_ele(test, device, **kwargs):
        View(test, device).drag_to_ele(kwargs["element"]["startElement"],kwargs["element"]["endElement"])

    @keywords("拖动到坐标")
    def drag_to_coord(test, device, **kwargs):
        View(test, device).drag_to_coord(kwargs["element"]["element"], **kwargs["data"])

    @keywords("坐标拖动")
    def drag_coord(test, device, **kwargs):
        View(test, device).drag_coord(**kwargs["data"])

    @keywords("元素内滑动")
    def swipe_ele(test, device, **kwargs):
        View(test, device).swipe_ele(kwargs["element"]["element"], kwargs["data"]["direction"])

    @keywords("等待弹框出现")
    def alert_wait(test, device, **kwargs):
        View(test, device).alert_wait(kwargs["data"]["second"])

    @keywords("弹框确认")
    def alert_accept(test, device, **kwargs):
        View(test, device).alert_accept()

    @keywords("弹框取消")
    def alert_dismiss(test, device, **kwargs):
        View(test, device).alert_dismiss()

    @keywords("弹框点击")
    def alert_click(test, device, **kwargs):
        View(test, device).alert_click(kwargs["data"]["name"])

    @keywords("自定义")
    def custom(test, device, **kwargs):
        View(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常


def find_assertion_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的断言操作函数。
    
    断言操作用于验证元素状态、属性、位置等是否符合预期，是自动化测试的核心功能。
    通过装饰器模式匹配操作名称，返回对应的断言函数。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 元素断言："断言元素存在", "断言元素文本", "断言元素属性"
            - 位置断言："断言元素位置", "断言元素X坐标", "断言元素Y坐标"
            - 弹框断言："断言弹框存在", "断言弹框文本"
            - 其他操作："自定义"
    
    Returns:
        function or None: 匹配的断言函数，如果未找到匹配的操作则返回None
    
    Note:
        - 断言函数会返回布尔值表示断言结果
        - 支持多种断言类型：等于、不等于、包含、不包含等
        - 操作函数内部会调用Assertion类的对应方法执行具体断言
        - 异常处理确保在匹配失败时返回None
    
    Example:
        >>> func = find_assertion_opt("断言元素存在")
        >>> if func:
        >>>     result = func(test, device, element={"element": element_obj}, 
        >>>                   data={"assertion": "等于", "expect": True})
    """
    function = None  # 存储匹配到的操作函数

    def keywords(name):
        """
        装饰器工厂函数，用于匹配操作名称。
        
        Args:
            name (str): 操作名称
        
        Returns:
            function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则将函数赋值给function变量
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("断言元素存在")
    def assert_ele_exists(test, device, **kwargs):
        return Assertion(test, device).assert_ele_exists(kwargs["element"]["element"],
                                                         kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素文本")
    def assert_ele_text(test, device, **kwargs):
        return Assertion(test, device).assert_ele_text(kwargs["system"], kwargs["element"]["element"],
                                                       kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素属性")
    def assert_ele_attribute(test, device, **kwargs):
        return Assertion(test, device).assert_ele_attribute(kwargs["element"]["element"], kwargs["data"]["attribute"],
                                                            kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素位置")
    def assert_ele_center(test, device, **kwargs):
        return Assertion(test, device).assert_ele_center(kwargs["system"], kwargs["element"]["element"],
                                                         kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素X坐标")
    def assert_ele_x(test, device, **kwargs):
        return Assertion(test, device).assert_ele_x(kwargs["system"], kwargs["element"]["element"],
                                                    kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言元素Y坐标")
    def assert_ele_y(test, device, **kwargs):
        return Assertion(test, device).assert_ele_y(kwargs["system"], kwargs["element"]["element"],
                                                    kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言弹框存在")
    def assert_alert_exists(test, device, **kwargs):
        return Assertion(test, device).assert_alert_exists(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("断言弹框文本")
    def assert_alert_text(test, device, **kwargs):
        return Assertion(test, device).assert_alert_text(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("自定义")
    def custom(test, device, **kwargs):
        return Assertion(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常


def find_relation_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的关联操作函数。
    
    关联操作用于提取和保存测试过程中的数据，如屏幕尺寸、元素属性、文本内容等，
    这些数据可以在后续的测试步骤中使用。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 屏幕信息："提取屏幕尺寸", "提取屏幕宽度", "提取屏幕高度"
            - 元素信息："提取元素文本", "提取元素位置", "提取元素X坐标", "提取元素Y坐标"
            - 弹框信息："提取弹框文本"
            - 其他操作："自定义"
    
    Returns:
        function or None: 匹配的关联函数，如果未找到匹配的操作则返回None
    
    Note:
        - 关联函数会将提取的数据保存到指定的变量名中
        - 保存的数据可以在后续测试步骤中通过变量名引用
        - 操作函数内部会调用Relation类的对应方法执行具体提取操作
        - 异常处理确保在匹配失败时返回None
    
    Example:
        >>> func = find_relation_opt("提取元素文本")
        >>> if func:
        >>>     func(test, device, element={"element": element_obj}, 
        >>>          data={"save_name": "element_text"})
    """
    function = None  # 存储匹配到的操作函数

    def keywords(name):
        """
        装饰器工厂函数，用于匹配操作名称。
        
        Args:
            name (str): 操作名称
        
        Returns:
            function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则将函数赋值给function变量
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("提取屏幕尺寸")
    def get_window_size(test, device, **kwargs):
        Relation(test, device).get_window_size(kwargs["system"], kwargs["data"]["save_name"])

    @keywords("提取屏幕宽度")
    def get_window_width(test, device, **kwargs):
        Relation(test, device).get_window_width(kwargs["system"], kwargs["data"]["save_name"])

    @keywords("提取屏幕高度")
    def get_window_height(test, device, **kwargs):
        Relation(test, device).get_window_height(kwargs["system"], kwargs["data"]["save_name"])

    @keywords("提取元素文本")
    def get_ele_text(test, device, **kwargs):
        Relation(test, device).get_ele_text(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素位置")
    def get_ele_center(test, device, **kwargs):
        Relation(test, device).get_ele_center(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素X坐标")
    def get_ele_x(test, device, **kwargs):
        Relation(test, device).get_ele_x(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取元素Y坐标")
    def get_ele_y(test, device, **kwargs):
        Relation(test, device).get_ele_y(kwargs["system"], kwargs["element"]["element"], kwargs["data"]["save_name"])

    @keywords("提取弹框文本")
    def get_alert_text(test, device, **kwargs):
        Relation(test, device).get_alert_text(kwargs["data"]["save_name"])

    @keywords("自定义")
    def custom(test, device, **kwargs):
        Relation(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常


def find_condition_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的条件判断操作函数。
    
    条件判断操作用于在测试流程中进行条件分支控制，根据元素状态、属性等
    判断结果来决定后续的执行路径。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 元素判断："判断元素存在", "判断元素文本", "判断元素属性"
            - 位置判断："判断元素位置", "判断元素X坐标", "判断元素Y坐标"
            - 弹框判断："判断弹框存在", "判断弹框文本"
            - 其他操作："自定义"
    
    Returns:
        function or None: 匹配的条件判断函数，如果未找到匹配的操作则返回None
    
    Note:
        - 条件判断函数会返回布尔值表示判断结果
        - 支持多种判断类型：等于、不等于、包含、不包含等
        - 操作函数内部会调用Condition类的对应方法执行具体判断
        - 异常处理确保在匹配失败时返回None
    
    Example:
        >>> func = find_condition_opt("判断元素存在")
        >>> if func:
        >>>     result = func(test, device, element={"element": element_obj}, 
        >>>                   data={"assertion": "等于", "expect": True})
    """
    function = None  # 存储匹配到的操作函数

    def keywords(name):
        """
        装饰器工厂函数，用于匹配操作名称。
        
        Args:
            name (str): 操作名称
        
        Returns:
            function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则将函数赋值给function变量
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("判断元素存在")
    def condition_ele_exists(test, device, **kwargs):
        return Condition(test, device).condition_ele_exists(kwargs["element"]["element"],
                                                            kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素文本")
    def condition_ele_text(test, device, **kwargs):
        return Condition(test, device).condition_ele_text(kwargs["system"], kwargs["element"]["element"],
                                                          kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素属性")
    def condition_ele_attribute(test, device, **kwargs):
        return Condition(test, device).condition_ele_attribute(kwargs["element"]["element"], kwargs["data"]["attribute"],
                                                            kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素位置")
    def condition_ele_center(test, device, **kwargs):
        return Condition(test, device).condition_ele_center(kwargs["system"], kwargs["element"]["element"],
                                                            kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素X坐标")
    def condition_ele_x(test, device, **kwargs):
        return Condition(test, device).condition_ele_x(kwargs["system"], kwargs["element"]["element"],
                                                       kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断元素Y坐标")
    def condition_ele_y(test, device, **kwargs):
        return Condition(test, device).condition_ele_y(kwargs["system"], kwargs["element"]["element"],
                                                       kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断弹框存在")
    def condition_alert_exists(test, device, **kwargs):
        return Condition(test, device).condition_alert_exists(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("判断弹框文本")
    def condition_alert_text(test, device, **kwargs):
        return Condition(test, device).condition_alert_text(kwargs["data"]["assertion"], kwargs["data"]["expect"])

    @keywords("自定义")
    def custom(test, device, **kwargs):
        return Condition(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常


def find_scenario_opt(operate_name: str):
    """
    根据操作名称查找并返回对应的场景操作函数。
    
    场景操作用于执行复杂的业务场景或自定义的测试逻辑，
    可以组合多个基础操作来完成特定的测试任务。
    
    Args:
        operate_name (str): 操作名称，支持的操作包括：
            - 自定义操作："自定义"
    
    Returns:
        function or None: 匹配的场景操作函数，如果未找到匹配的操作则返回None
    
    Note:
        - 场景操作函数可以返回任意类型的结果
        - 主要用于执行自定义的复杂测试逻辑
        - 操作函数内部会调用Scenario类的对应方法执行具体场景
        - 异常处理确保在匹配失败时返回None
    
    Example:
        >>> func = find_scenario_opt("自定义")
        >>> if func:
        >>>     result = func(test, device, **custom_kwargs)
    """
    function = None  # 存储匹配到的操作函数

    def keywords(name):
        """
        装饰器工厂函数，用于匹配操作名称。
        
        Args:
            name (str): 操作名称
        
        Returns:
            function: 装饰器函数
        """
        def back(func):
            # 如果操作名称匹配，则将函数赋值给function变量
            if name == operate_name:
                nonlocal function
                function = func

        return back

    @keywords("自定义")
    def custom(test, device, **kwargs):
        return Scenario(test, device).custom(**kwargs)

    try:
        return function  # 返回匹配到的操作函数
    except:
        return None  # 匹配失败时返回None，避免抛出异常
