import sys
from datetime import datetime
from core.app.find_opt import *
from core.assertion import LMAssert


class AppTestStep:
    """
    移动应用测试步骤执行器
    
    负责执行单个移动应用测试步骤，包括操作查找、参数处理、结果验证、
    循环控制、条件判断、断言验证等功能。
    
    主要功能：
        - 操作步骤执行：根据操作类型查找并执行相应操作
        - 循环控制：支持For循环和While循环控制
        - 条件判断：支持条件分支控制流程
        - 断言验证：执行断言检查并处理结果
        - 日志记录：详细记录操作过程和结果
        - 异常处理：捕获并处理执行异常
    
    支持的操作类型：
        - system: 系统级操作（如启动应用、返回桌面）
        - view: 视图操作（如点击、输入、滑动）
        - condition: 条件控制（如if判断）
        - assertion: 断言验证（如文本断言、元素断言）
        - relation: 关联操作（如参数提取、数据关联）
        - scenario: 场景操作（如自定义业务场景）
    
    控制器支持：
        - For循环：指定次数的循环执行
        - While循环：基于条件的循环执行，支持超时控制
        - 条件控制：基于断言结果的分支跳转
        - 循环嵌套：支持多层循环嵌套执行
    
    属性：
        test: 测试实例对象，用于日志记录和状态管理
        device: 设备连接对象，用于设备操作
        context: 测试上下文，存储变量和状态信息
        collector: 操作数据收集器，包含操作配置信息
        result: 操作执行结果，包含成功状态和返回数据
    
    使用示例：:
        # 创建测试步骤执行器
        step = AppTestStep(test, device, context, collector)
        
        # 执行测试步骤
        step.execute()
        
        # 处理循环控制
        skip_steps = step.looper_controller(case, opt_list, step_n)
        
        # 处理断言验证
        step.assert_controller()
        
        # 处理条件控制
        skip_list = step.condition_controller(current_step)
    """
    
    def __init__(self, test, device, context, collector):
        """
        初始化移动应用测试步骤执行器
        
        Args:
            test: 测试实例对象，提供日志记录和状态管理功能
            device: 设备连接对象，用于执行设备操作
            context (dict): 测试上下文字典，存储变量和状态
            collector: 操作数据收集器，包含操作的所有配置信息
        """
        self.test = test                                                  # 测试实例引用
        self.device = device                                              # 设备连接对象
        self.context = context                                            # 测试上下文
        self.collector = collector                                        # 操作数据收集器
        self.result = None                                                # 操作执行结果

    def execute(self):
        """
        执行移动应用测试步骤
        
        根据操作类型查找对应的操作函数，构建操作参数，执行操作并记录结果。
        
        执行流程：
            1. 记录操作开始日志
            2. 根据操作类型查找对应的操作函数
            3. 构建操作参数字典
            4. 执行操作函数并获取结果
            5. 记录操作详细信息
            6. 记录操作结束日志
        
        操作类型映射：
            - system: 系统操作（启动应用、返回桌面、锁屏等）
            - view: 视图操作（点击、输入、滑动、等待等）
            - condition: 条件操作（if判断、条件分支）
            - assertion: 断言操作（文本断言、元素断言、属性断言）
            - relation: 关联操作（参数提取、数据关联、变量赋值）
            - scenario: 场景操作（自定义业务场景、复合操作）
        
        操作参数：
            - system: 操作系统类型（Android/iOS）
            - trans: 操作事务名称（用于日志和报告）
            - code: 自定义代码（用于脚本执行）
            - element: 元素定位信息（ID、XPath、属性等）
            - data: 操作数据（输入内容、断言期望值等）
        
        异常处理：
            - 操作函数未找到时抛出NotExistedAppOperation异常
            - 操作执行异常会向上传播
            - 无论成功失败都会记录结束日志
        
        注意事项：
            - 操作结果存储在self.result中
            - 支持自定义操作扩展
            - 操作执行过程会详细记录日志
        """
        try:
            self.test.debugLog('APP操作[{}]开始'.format(self.collector.opt_name))  # 记录操作开始
            opt_type = self.collector.opt_type                           # 获取操作类型
            if opt_type == "system":                                     # 系统操作
                func = find_system_opt(self.collector.opt_name)
            elif opt_type == "view":                                     # 视图操作
                func = find_view_opt(self.collector.opt_name)
            elif opt_type == "condition":                                # 条件操作
                func = find_condition_opt(self.collector.opt_name)
            elif opt_type == "assertion":                                # 断言操作
                func = find_assertion_opt(self.collector.opt_name)
            elif opt_type == "relation":                                 # 关联操作
                func = find_relation_opt(self.collector.opt_name)
            else:                                                         # 场景操作（默认）
                func = find_scenario_opt(self.collector.opt_name)
            if func is None:                                              # 检查操作函数是否存在
                raise NotExistedAppOperation("未定义操作")
            opt_content = {                                               # 构建操作参数字典
                "system": self.collector.opt_system,                     # 操作系统类型
                "trans": self.collector.opt_trans,                       # 事务名称
                "code": self.collector.opt_code,                         # 自定义代码
                "element": self.collector.opt_element,                   # 元素定位信息
                "data": self.collector.opt_data                          # 操作数据
            }
            self.result = func(self.test, self.device, **opt_content)    # 执行操作函数
            self.log_show()                                               # 记录操作详细信息
        finally:
            self.test.debugLog('APP操作[{}]结束'.format(self.collector.opt_name))  # 记录操作结束

    def looper_controller(self, case, opt_list, step_n):
        """
        循环控制器
        
        处理For循环和While循环控制逻辑，支持嵌套循环和超时控制。
        
        Args:
            case: 测试用例对象，用于执行循环内的操作步骤
            opt_list (list): 完整的操作步骤列表
            step_n (int): 当前循环操作在列表中的索引位置
        
        Returns:
            int: 循环体包含的步骤数量，用于跳过循环内的步骤
        
        循环类型：
            1. While循环：基于条件的循环执行
               - 支持超时控制，防止死循环
               - 每次循环都重新渲染条件表达式
               - 条件不满足时自动退出循环
            
            2. For循环：指定次数的循环执行
               - 固定循环次数，执行效率高
               - 只需渲染一次循环配置
               - 适用于已知循环次数的场景
        
        循环配置参数：
            - times: 循环次数（For循环）
            - timeout: 超时时间，毫秒（While循环，0表示无限制）
            - indexName: 循环索引变量名
            - steps: 循环体包含的步骤数量
            - assertion: 循环条件断言类型（While循环）
            - target: 断言目标值（While循环）
            - expect: 断言期望值（While循环）
        
        执行逻辑：
            1. 根据事务类型判断循环类型
            2. 渲染循环配置参数
            3. 设置循环索引变量
            4. 执行循环体内的操作步骤
            5. 返回需要跳过的步骤数量
        
        注意事项：
            - While循环timeout为0时可能死循环，需谨慎使用
            - 循环索引变量会添加到测试上下文中
            - 嵌套循环的索引变量名不应相同
            - 循环操作本身不参与循环执行
        """
        if self.collector.opt_trans == "While循环":                      # While循环处理
            loop_start_time = datetime.now()                             # 记录循环开始时间
            timeout = int(self.collector.opt_data["timeout"]["value"])   # 获取超时时间
            index_name = self.collector.opt_data["indexName"]["value"]   # 获取索引变量名
            steps = int(self.collector.opt_data["steps"]["value"])       # 获取循环步骤数
            index = 0                                                     # 初始化循环索引
            while timeout == 0 or (datetime.now() - loop_start_time).seconds * 1000 < timeout:  # 循环条件检查
                # timeout为0时可能会死循环 慎重选择
                self.context[index_name] = index                         # 给循环索引赋值第几次循环 母循环和子循环的索引名不应一样
                _looper = case.render_looper(self.collector.opt_data)    # 渲染循环控制控制器 每次循环都需要渲染
                index += 1                                                # 递增循环索引
                result, _ = LMAssert(_looper['assertion'], _looper['target'], _looper['expect']).compare()  # 执行循环条件断言
                if not result:                                            # 条件不满足时退出循环
                    break
                _opt_list = opt_list[step_n+1: (step_n + _looper["steps"]+1)]  # 循环操作本身不参与循环 不然死循环
                case.loop_execute(_opt_list, [])                         # 执行循环体内的操作
            return steps                                                  # 返回循环步骤数
        else:                                                             # For循环处理
            _looper = case.render_looper(self.collector.opt_data)        # 渲染循环控制控制器 for只需渲染一次
            for index in range(_looper["times"]):                        # 本次循环次数
                self.context[_looper["indexName"]] = index               # 给循环索引赋值第几次循环 母循环和子循环的索引名不应一样
                _opt_list = opt_list[step_n+1: (step_n + _looper["steps"]+1)]  # 获取循环体操作列表
                case.loop_execute(_opt_list, [])                         # 执行循环体内的操作
            return _looper["steps"]                                      # 返回循环步骤数

    def assert_controller(self):
        """
        断言控制器
        
        处理断言操作的结果验证和后续控制逻辑。
        
        断言处理逻辑：
            1. 断言成功：
               - 记录成功日志
               - 继续执行后续步骤
            
            2. 断言失败：
               - 记录失败日志
               - 截取失败截图
               - 根据配置决定是否停止执行
        
        断言配置参数：
            - continue: 断言失败时是否继续执行
              - True: 记录失败状态但继续执行
              - False/不存在: 抛出AssertionError异常，停止测试
        
        异常处理：
            - 当continue为True时，捕获异常并记录失败状态
            - 当continue为False或不存在时，直接抛出AssertionError
            - 异常会被上层捕获并进行相应处理
        
        使用场景：
            - 关键功能验证：不设置continue，确保关键断言通过
            - 非关键检查：设置continue为True，记录问题但不中断流程
            - 数据验证：验证界面数据的正确性
            - 状态检查：验证应用或系统的状态
        
        注意事项：
            - 断言结果存储在self.result[0]中（布尔值）
            - 断言详细信息存储在self.result[1]中（字符串）
            - 截图文件会自动保存到测试报告中
            - 断言失败的详细信息会记录在测试日志中
        """
        if self.collector.opt_type == "assertion":                      # 检查是否为断言操作
            if self.result[0]:                                            # 断言成功处理
                self.test.debugLog('[{}]断言成功: {}'.format(self.collector.opt_trans,
                                                             self.result[1]))  # 记录成功日志
            else:                                                         # 断言失败处理
                self.test.errorLog('[{}]断言失败: {}'.format(self.collector.opt_trans,
                                                             self.result[1]))  # 记录失败日志
                self.test.saveScreenShot(self.collector.opt_trans, self.device.screenshot(format='raw'))  # 截取失败截图
                if "continue" in self.collector.opt_data and self.collector.opt_data["continue"] is True:  # 检查是否继续执行
                    try:
                        raise AssertionError(self.result[1])             # 抛出断言异常
                    except AssertionError:
                        error_info = sys.exc_info()                      # 获取异常信息
                        self.test.recordFailStatus(error_info)           # 记录失败状态但继续执行
                else:
                    raise AssertionError(self.result[1])                 # 直接抛出断言异常，停止测试

    def condition_controller(self, current):
        """
        条件控制器
        
        根据条件判断结果控制测试流程的跳转逻辑，支持分支控制和步骤跳过。
        
        Args:
            current (int): 当前步骤的索引位置
        
        Returns:
            list: 需要跳过的步骤索引列表
                - 空列表：不跳过任何步骤，继续顺序执行
                - 包含索引的列表：跳过列表中指定的步骤
        
        条件判断逻辑：
            1. 条件为真（True）：
               - 执行成功分支逻辑
               - 跳过false分支对应的步骤
               - 记录成功分支执行日志
            
            2. 条件为假（False）：
               - 执行失败分支逻辑
               - 跳过true分支对应的步骤
               - 记录失败分支执行日志
        
        条件配置参数：
            - true: 条件为真时的分支步骤数
            - false: 条件为假时的分支步骤数
        
        跳过步骤计算：
            - 条件为真：跳过从(current + offset_true + 1)到(current + offset_true + offset_false)的步骤
            - 条件为假：跳过从(current + 1)到(current + offset_true)的步骤
        
        使用场景：
            - 分支逻辑：根据界面状态选择不同的操作路径
            - 异常处理：检测到异常时跳转到处理流程
            - 数据验证：根据数据状态选择不同的处理方式
            - 流程控制：实现复杂的业务逻辑分支
        
        注意事项：
            - 只有condition类型的操作才会执行条件控制
            - 条件结果存储在self.result[0]中（布尔值）
            - 条件详细信息存储在self.result[1]中（字符串）
            - offset参数必须为整数，非整数时默认为0
            - 跳过的步骤不会被执行，需要合理设计分支结构
        """
        if self.collector.opt_type == "condition":                      # 检查是否为条件操作
            offset_true = self.collector.opt_data["true"]               # 获取真值分支步骤数
            if not isinstance(offset_true, int):                        # 确保为整数类型
                offset_true = 0
            offset_false = self.collector.opt_data["false"]             # 获取假值分支步骤数
            if not isinstance(offset_false, int):                       # 确保为整数类型
                offset_false = 0
            if self.result[0]:                                           # 条件为真的处理
                self.test.debugLog('[{}]判断成功, 执行成功分支: {}'.format(self.collector.opt_name,
                                                                        self.result[1]))  # 记录成功分支日志
                return [current + i for i in range(offset_true + 1, offset_true + offset_false + 1)]  # 跳过假值分支步骤
            else:                                                        # 条件为假的处理
                self.test.errorLog('[{}]判断失败, 执行失败分支: {}'.format(self.collector.opt_name,
                                                                        self.result[1]))  # 记录失败分支日志
                return [current + i for i in range(1, offset_true + 1)] # 跳过真值分支步骤
        return []                                                        # 非条件操作返回空列表

    def log_show(self):
        """
        日志展示
        
        记录当前操作步骤的详细信息到测试日志中，用于调试和问题排查。
        
        日志内容包括：
            1. 元素定位信息：目标UI元素的定位方式和定位值
               - ID定位：通过元素ID进行定位
               - XPath定位：通过XPath表达式进行定位
               - 属性定位：通过元素属性进行定位
               - 文本定位：通过元素文本内容进行定位
            
            2. 操作数据信息：操作所需的参数和配置数据
               - 输入数据：文本输入、数值输入等
               - 配置参数：超时时间、重试次数等
               - 断言数据：期望值、比较方式等
               - 控制参数：循环次数、条件判断等
        
        日志格式：
            - 使用HTML格式的换行符<br>便于在Web报告中显示
            - 元素定位信息以键值对形式展示
            - 操作数据以字典格式展示，包含数据类型信息
        
        使用场景：
            - 测试调试：通过日志了解操作执行的详细过程
            - 问题排查：定位操作失败的原因和位置
            - 测试报告：为测试报告提供详细的执行记录
            - 性能分析：分析操作执行的时间和效率
        
        日志级别：
            - 使用debugLog记录，属于调试级别日志
            - 在生产环境中可以通过日志级别控制是否输出
        
        注意事项：
            - 只有当元素定位或操作数据不为空时才记录相应信息
            - 日志信息来源于collector收集的操作配置
            - 操作数据可能包含敏感信息，需注意日志安全
            - 日志格式统一，便于后续解析和分析
        """
        msg = ""                                                        # 初始化日志消息
        if self.collector.opt_element is not None:                     # 检查元素定位信息是否存在
            for k, v in self.collector.opt_element.items():            # 遍历元素定位信息
                msg += '元素定位: {}: {}<br>'.format(k, v)              # 添加元素定位信息到日志
        if self.collector.opt_data is not None:                        # 检查操作数据是否存在
            data_log = '{'                                              # 初始化数据日志格式
            for k, v in self.collector.opt_data.items():               # 遍历操作数据
                class_name = type(v).__name__                          # 获取数据类型名称
                data_log += "{}: {}, ".format(k, v)                   # 添加数据项到日志
            if len(data_log) > 1:                                       # 检查是否有数据项
                data_log = data_log[:-2]                               # 移除最后的逗号和空格
            data_log += '}'                                             # 结束数据日志格式
            msg += '操作数据: {}'.format(data_log)                      # 添加操作数据到日志
        if msg != "":                                                   # 检查是否有日志内容
            msg = '操作信息: <br>' + msg                                # 添加日志标题
            self.test.debugLog(msg)                                     # 记录调试日志


class NotExistedAppOperation(Exception):
    """
    未定义的APP操作异常
    
    当尝试执行一个不存在或未定义的APP操作时抛出的自定义异常。
    
    异常场景：
        1. 操作类型不在支持的类型列表中
           - 支持的类型：system, view, condition, assertion, relation, scenario
           - 不支持的类型会触发此异常
        
        2. 操作事务名称在对应类型中不存在
           - 每种操作类型都有特定的事务列表
           - 事务名称拼写错误或不存在时触发
        
        3. 操作函数未在设备操作类中定义
           - 操作函数需要在对应的设备操作类中实现
           - 缺少函数定义时会触发此异常
    
    异常处理：
        - 异常会被上层捕获并记录到测试日志中
        - 测试执行会中断，并标记为失败状态
        - 异常信息会包含具体的操作类型和事务名称
    
    使用示例：
        try:
            # 执行操作步骤
            step.execute()
        except NotExistedAppOperation as e:
            # 处理不存在的操作异常
            logger.error(f"操作不存在: {e}")
            # 记录失败状态并继续或停止测试
    
    预防措施：
        - 在配置测试用例时验证操作类型和事务名称
        - 定期检查操作函数的实现完整性
        - 使用IDE的代码提示功能避免拼写错误
    
    注意事项：
        - 继承自Python内置的Exception类
        - 异常信息应该包含足够的上下文信息
        - 可以通过日志系统记录异常的详细堆栈信息
        - 建议在异常消息中包含操作类型和事务名称便于排查
    """
