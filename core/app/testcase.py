from core.template import Template
from core.app.collector import AppOperationCollector
from core.app.teststep import AppTestStep
from core.app.device import connect_device
from tools.utils.utils import get_case_message, handle_operation_data, handle_params_data
import re


class AppTestCase:
    """
    移动应用测试用例执行器
    
    负责执行完整的移动应用自动化测试用例，包括设备连接、应用启动、
    操作步骤执行、循环控制、条件判断、模板渲染、断言验证等功能。
    
    主要功能：
        - 设备连接和应用管理：自动连接测试设备，启动和停止目标应用
        - 操作步骤执行：按顺序执行测试步骤，支持各种UI操作
        - 循环控制：支持FOR和WHILE循环，实现重复操作
        - 条件控制：基于条件判断跳过或执行特定步骤
        - 模板渲染：支持动态参数替换和数据驱动测试
        - 异常处理：自动截图保存，便于问题定位
        - 事务管理：记录操作状态和执行结果
    
    支持的平台：
        - Android：通过uiautomator2进行自动化
        - iOS：通过WebDriverAgent进行自动化
    
    支持的操作类型：
        - 基础操作：点击、输入、滑动、等待
        - 断言操作：元素存在性、文本内容、属性值验证
        - 循环操作：FOR循环、WHILE循环
        - 条件操作：基于断言结果的条件执行
        - 自定义操作：执行自定义Python代码
    
    属性：
        test: 测试实例，包含测试上下文和配置
        context: 测试上下文，存储共享数据和变量
        case_message (dict): 测试用例配置信息
        id (str): 测试用例唯一标识符
        name (str): 测试用例名称
        functions (dict): 自定义函数集合
        params (dict): 测试参数集合
        device: 设备连接对象（Android或iOS）
        template: 模板渲染引擎
        comp: 正则表达式编译对象，用于检测模板变量
    
    使用示例：
        # 创建测试用例执行器
        test_case = AppTestCase(test_instance)
        
        # 执行测试用例
        try:
            test_case.execute()
        except Exception as e:
            print(f"测试执行失败: {e}")
    
    注意事项：
        - 执行前需确保设备在线且应用已安装
        - 执行过程中会自动管理应用生命周期
        - 异常发生时会自动截图保存
        - 支持参数化测试和数据驱动
    """
    
    def __init__(self, test):
        """
        初始化移动应用测试用例执行器
        
        解析测试用例配置，初始化设备连接，设置模板引擎和参数处理器。
        
        Args:
            test: 测试实例对象，包含测试数据和上下文信息
        
        初始化流程：
            1. 解析测试用例配置信息
            2. 提取用例基本信息（ID、名称、描述）
            3. 处理自定义函数和参数
            4. 连接测试设备并启动应用
            5. 初始化模板渲染引擎
            6. 编译正则表达式用于模板变量检测
        
        设置的属性：
            - test: 测试实例引用
            - context: 测试上下文，用于数据共享
            - case_message: 解析后的用例配置
            - id/name: 用例标识和名称
            - functions: 自定义函数集合
            - params: 处理后的测试参数
            - device: 连接的设备对象
            - template: 模板渲染引擎
            - comp: 模板变量检测的正则表达式
        
        异常情况：
            - 设备连接失败时抛出异常
            - 应用启动失败时抛出异常
            - 配置解析错误时抛出异常
        """
        self.test = test                                                    # 保存测试实例引用
        self.context = test.context                                         # 获取测试上下文
        self.case_message = get_case_message(test.test_data)               # 解析测试用例配置
        self.id = self.case_message['caseId']                             # 提取用例ID
        self.name = self.case_message['caseName']                         # 提取用例名称
        setattr(test, 'test_case_name', self.case_message['caseName'])    # 设置测试实例的用例名称
        setattr(test, 'test_case_desc', self.case_message['comment'])     # 设置测试实例的用例描述
        self.functions = self.case_message['functions']                   # 获取自定义函数集合
        self.params = handle_params_data(self.case_message['params'])     # 处理测试参数
        test.common_params = self.params                                  # 设置公共参数到测试实例
        self.device = self.before_execute()                               # 连接设备并启动应用
        self.template = Template(self.test, self.context, self.functions, self.params)  # 初始化模板引擎
        self.comp = re.compile(r"\{\{.*?\}\}")                            # 编译模板变量检测正则表达式

    def execute(self):
        """
        执行移动应用测试用例
        
        按照配置的操作列表顺序执行所有测试步骤，包括循环控制、
        条件判断、异常处理等。执行完成后自动清理资源。
        
        执行流程：
            1. 验证操作列表是否存在
            2. 调用循环执行方法处理所有操作
            3. 无论成功失败都执行清理操作
        
        异常处理：
            - 操作列表为空时抛出RuntimeError
            - 执行过程中的异常会向上传播
            - finally块确保资源清理
        
        注意事项：
            - 执行前设备已连接且应用已启动
            - 异常发生时会自动截图
            - 执行完成后会停止应用
        """
        if self.case_message['optList'] is None:
            self.after_execute()                                           # 清理资源
            raise RuntimeError("无法获取APP测试相关数据, 请重试!!!")          # 抛出运行时错误
        try:
            self.loop_execute(self.case_message['optList'], [])           # 执行操作列表
        finally:
            self.after_execute()                                           # 确保资源清理

    def loop_execute(self, opt_list, skip_opts, step_n=0):
        """
        循环执行操作列表中的所有步骤
        
        按顺序遍历操作列表，处理每个操作步骤，支持循环控制、
        条件跳过、异常处理等功能。
        
        Args:
            opt_list (list): 操作步骤列表
            skip_opts (list): 需要跳过的步骤索引列表
            step_n (int): 当前步骤索引，默认从0开始
        
        执行逻辑：
            1. 遍历操作列表中的每个步骤
            2. 为每个步骤创建收集器和执行器
            3. 定义事务用于状态跟踪
            4. 检查是否需要跳过当前步骤
            5. 收集步骤配置信息
            6. 根据操作类型执行相应逻辑
            7. 处理循环控制和条件控制
        
        操作类型处理：
            - looper: 循环操作，调用循环控制器
            - 其他: 普通操作，执行渲染、执行、断言、条件控制
        
        异常处理：
            - 非断言异常时自动截图
            - 异常向上传播，由调用方处理
        
        注意事项：
            - skip_opts列表会动态更新
            - 循环操作会跳过多个步骤
            - 事务状态会实时更新
        """
        while step_n < len(opt_list):
            opt_content = opt_list[step_n]                                 # 获取当前操作配置
            # 定义收集器
            collector = AppOperationCollector()                           # 创建操作数据收集器
            step = AppTestStep(self.test, self.device, self.context, collector)  # 创建测试步骤执行器
            # 定义事务
            self.test.defineTrans(opt_content["operationId"], opt_content['operationTrans'],
                                  self.get_opt_content(opt_content['operationElement']), opt_content['operationDesc'])
            if step_n in skip_opts:                                       # 检查是否需要跳过当前步骤
                self.test.updateTransStatus(3)                           # 更新事务状态为跳过
                self.test.debugLog('[{}]操作在条件控制之外不被执行'.format(opt_content['operationTrans']))
                step_n += 1
                continue
            # 收集步骤信息
            step.collector.collect(opt_content)                          # 收集操作配置数据
            try:
                if step.collector.opt_type == "looper":                 # 处理循环操作
                    looper_step_num = step.looper_controller(self, opt_list, step_n)
                    step_n += looper_step_num + 1                        # 跳过循环内的步骤
                else:                                                     # 处理普通操作
                    # 渲染主体
                    self.render_content(step)                            # 渲染模板变量
                    step.execute()                                        # 执行操作步骤
                    step.assert_controller()                             # 执行断言验证
                    skip_opts.extend(step.condition_controller(step_n))  # 处理条件控制
                    step_n += 1                                          # 移动到下一步
            except Exception as e:
                if not isinstance(e, AssertionError):                    # 非断言异常时截图
                    self.test.saveScreenShot(opt_content['operationTrans'], self.device.screenshot(format='raw'))
                raise e                                                   # 重新抛出异常

    @staticmethod
    def get_opt_content(elements):
        """
        获取操作元素的内容描述
        
        将元素定位配置转换为可读的字符串格式，用于事务日志记录。
        
        Args:
            elements (dict): 元素定位配置字典，格式为 {name: {"target": value}}
        
        Returns:
            str: 格式化的元素内容描述字符串
        
        格式示例：
            输入: {"login_btn": {"target": "登录按钮"}, "username": {"target": "用户名输入框"}}
            输出: "\n login_btn: 登录按钮\n username: 用户名输入框"
        
        注意事项：
            - 空元素配置返回空字符串
            - 每个元素占一行，便于日志查看
            - 使用target字段作为描述内容
        """
        content = ""                                                      # 初始化内容字符串
        if elements is not None:                                         # 检查元素配置是否存在
            for key, element in elements.items():                        # 遍历所有元素
                content = "%s\n %s: %s" % (content, key, element["target"])  # 格式化元素信息
        return content                                                    # 返回格式化的内容

    def before_execute(self):
        """
        执行前的准备工作
        
        连接测试设备并启动目标应用，为测试执行做好准备。
        
        Returns:
            device: 连接的设备对象（Android或iOS）
        
        执行流程：
            1. 检查设备URL是否有效
            2. 根据系统类型连接设备
            3. Android: 健康检查 + 启动应用
            4. iOS: 创建会话 + 设置WDA URL
        
        Android设备处理：
            - 执行健康检查确保设备可用
            - 启动指定的应用和Activity
            - 返回uiautomator2设备对象
        
        iOS设备处理：
            - 创建WebDriverAgent会话
            - 设置WDA服务器URL
            - 返回WDA设备对象
        
        异常情况：
            - 设备URL为空时抛出异常
            - 设备连接失败时抛出异常
            - 应用启动失败时抛出异常
        
        注意事项：
            - 需要确保设备在线且可访问
            - Android需要安装uiautomator2服务
            - iOS需要安装WebDriverAgent
        """
        if self.case_message['deviceUrl'] is None:                       # 检查设备URL
            raise Exception("执行设备不在线 本用例执行失败")                  # 抛出设备离线异常
        device = connect_device(self.case_message['deviceSystem'], f"http://{self.case_message['deviceUrl']}")  # 连接设备
        if self.case_message['deviceSystem'] == 'android':              # Android设备处理
            device.healthcheck()                                         # 执行健康检查
            device.app_start(self.case_message['appId'], self.case_message['activity'])  # 启动应用
            return device                                                 # 返回Android设备对象
        else:                                                            # iOS设备处理
            device = device.session(self.case_message['appId'])         # 创建应用会话
            device._wda_url = f"http://{self.case_message['deviceUrl']}" # 设置WDA URL
            return device                                                 # 返回iOS设备对象

    def after_execute(self):
        """
        执行后的清理工作
        
        停止目标应用，释放设备资源，确保测试环境的清洁。
        
        清理操作：
            - 停止正在运行的目标应用
            - 释放设备连接资源
        
        注意事项：
            - 无论测试成功失败都会执行
            - 确保应用完全停止，避免影响后续测试
            - 异常情况下也要保证资源清理
        """
        self.device.app_stop(self.case_message['appId'])                 # 停止目标应用

    def render_looper(self, looper):
        """
        渲染循环器配置中的模板变量
        
        处理循环器配置中的模板变量，将其渲染为实际值，并进行数据类型转换。
        
        Args:
            looper (dict): 循环器配置字典，包含循环控制参数
        
        Returns:
            dict: 渲染后的循环器配置，包含处理后的参数值
        
        处理流程：
            1. 初始化模板引擎并传入循环器配置
            2. 渲染所有模板变量为实际值
            3. 对非断言字段进行数据类型转换
            4. 特殊处理循环次数字段，确保为整数
        
        支持的循环参数：
            - times: 循环次数，自动转换为整数
            - condition: 循环条件表达式
            - data_source: 数据源配置
            - variables: 循环变量定义
        
        数据处理规则：
            - target和expect字段跳过数据处理（用于断言）
            - 其他字段根据type进行相应的数据类型转换
            - times字段强制转换为整数，转换失败时默认为1
        
        模板变量格式：
            - {{variable_name}}: 简单变量引用
            - {{context.data}}: 上下文数据引用
            - {{functions.get_data()}}: 函数调用
        
        注意事项：
            - 模板渲染失败会抛出异常
            - times字段转换异常时使用默认值1
            - 支持复杂的嵌套数据结构
        """
        self.template.init(looper)                                       # 初始化模板引擎
        _looper = self.template.render()                                 # 渲染模板变量
        for name, param in _looper.items():                              # 遍历渲染后的参数
            if name != "target" or name != "expect":                     # 断言实际值不作数据处理
                _looper[name] = handle_operation_data(param["type"], param["value"])  # 进行数据类型转换
        if "times" in _looper:                                          # 特殊处理循环次数
            try:
                times = int(_looper["times"])                            # 尝试转换为整数
            except:
                times = 1                                                 # 转换失败时使用默认值
            _looper["times"] = times                                     # 更新循环次数
        return _looper                                                    # 返回处理后的循环器配置

    def render_content(self, step):
        """
        渲染测试步骤中的模板变量
        
        处理测试步骤中元素定位和操作数据的模板变量，实现动态数据驱动测试。
        
        Args:
            step: 测试步骤对象，包含收集器和操作配置信息
        
        处理内容：
            1. 元素定位表达式的模板变量渲染
            2. 操作数据的模板变量渲染和类型转换
        
        元素定位处理：
            - 检测定位表达式中的模板变量
            - 使用模板引擎渲染为实际定位值
            - 支持动态元素定位和参数化定位
        
        操作数据处理：
            - 检测数据值中的模板变量
            - 渲染模板变量为实际数据
            - 根据数据类型进行相应转换
            - 更新步骤收集器的数据配置
        
        支持的模板变量：
            - {{test_data.username}}: 测试数据变量
            - {{context.current_user}}: 上下文变量
            - {{functions.generate_id()}}: 函数调用
            - {{params.base_url}}: 参数变量
        
        数据类型转换：
            - string: 字符串类型
            - int: 整数类型
            - float: 浮点数类型
            - bool: 布尔类型
            - json: JSON对象类型
        
        使用场景：
            - 动态元素定位（如根据用户ID定位元素）
            - 参数化输入数据（如用户名、密码）
            - 关联测试数据（如使用上一步的输出）
            - 环境相关配置（如不同环境的URL）
        
        注意事项：
            - 只处理字符串类型的模板变量
            - 模板渲染失败会抛出异常
            - 数据类型转换失败会抛出异常
        """
        if step.collector.opt_element is not None:                       # 处理元素定位表达式
            for name, expression in step.collector.opt_element.items():  # 遍历所有元素定位
                if self.comp.search(str(expression)) is not None:        # 检测是否包含模板变量
                    self.template.init(expression)                       # 初始化模板引擎
                    expression = self.template.render()                  # 渲染模板变量
                step.collector.opt_element[name] = expression            # 更新元素定位表达式
        if step.collector.opt_data is not None:                         # 处理操作数据
            data = {}                                                     # 初始化数据字典
            for name, param in step.collector.opt_data.items():          # 遍历所有操作数据
                param_value = param["value"]                             # 获取参数值
                if isinstance(param_value, str) and self.comp.search(param_value) is not None:  # 检测字符串中的模板变量
                    self.template.init(param_value)                      # 初始化模板引擎
                    param_value = self.template.render()                 # 渲染模板变量
                data[name] = handle_operation_data(param["type"], param_value)  # 进行数据类型转换
            step.collector.opt_data = data                               # 更新步骤的操作数据

