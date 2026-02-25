"""Web自动化测试用例执行模块

    该模块提供Web自动化测试用例的核心执行功能，包括：
    - 测试用例的初始化和配置
    - WebDriver的启动和管理
    - 测试步骤的循环执行
    - 条件控制和循环控制
    - 模板渲染和数据处理
    - 异常处理和截图保存

    作者: LiuMa团队
    日期: 2024-01-15
"""

import re  # 正则表达式模块，用于模板变量匹配
from selenium import webdriver  # Selenium WebDriver，用于浏览器自动化
from core.template import Template  # 模板引擎，用于数据渲染
from core.web.collector import WebOperationCollector  # Web操作收集器
from core.web.teststep import WebTestStep  # Web测试步骤执行器
from tools.utils.utils import get_case_message, handle_operation_data, handle_params_data  # 工具函数


class WebTestCase:
    """Web自动化测试用例执行器
    
        负责Web自动化测试用例的完整执行流程，包括：
        - 测试用例数据的解析和初始化
        - WebDriver的生命周期管理
        - 测试步骤的顺序执行和控制流
        - 模板变量的渲染和数据处理
        - 异常处理和测试结果收集
        
        主要功能模块：
        1. 用例初始化：解析测试数据，设置执行环境
        2. 驱动管理：启动、配置和关闭WebDriver
        3. 步骤执行：循环执行测试步骤，支持条件控制
        4. 模板渲染：处理动态数据和参数替换
        5. 异常处理：捕获异常并保存截图
    """
    
    def __init__(self, test):
        """初始化Web测试用例执行器
        
            解析测试数据，设置执行环境，初始化各种组件
            
            Args:
                test: 测试实例对象，包含测试配置和上下文信息
                
            Attributes:
                test: 测试实例引用
                context: 测试上下文环境
                case_message: 解析后的用例数据
                id: 用例ID
                name: 用例名称
                functions: 用例中使用的函数列表
                params: 处理后的参数数据
                template: 模板渲染引擎
                driver: WebDriver实例
                comp: 正则表达式编译对象，用于匹配模板变量
        """
        self.test = test  # 保存测试实例引用
        self.context = test.context  # 获取测试上下文环境
        self.case_message = get_case_message(test.test_data)  # 解析测试用例数据
        self.id = self.case_message['caseId']  # 提取用例ID
        self.name = self.case_message['caseName']  # 提取用例名称
        setattr(test, 'test_case_name', self.case_message['caseName'])  # 设置测试实例的用例名称属性
        setattr(test, 'test_case_desc', self.case_message['comment'])  # 设置测试实例的用例描述属性
        self.functions = self.case_message['functions']  # 获取用例中使用的函数列表
        self.params = handle_params_data(self.case_message['params'])  # 处理参数数据
        test.common_params = self.params  # 将处理后的参数设置为测试实例的公共参数
        self.template = Template(self.test, self.context, self.functions, self.params)  # 初始化模板渲染引擎
        self.driver = self.before_execute()  # 执行前置操作，启动WebDriver
        self.comp = re.compile(r"\{\{.*?\}\}")  # 编译正则表达式，用于匹配模板变量

    def execute(self):
        """执行Web测试用例
        
            执行完整的测试用例流程，包括操作列表的循环执行
            
            主要流程：
            1. 检查操作列表是否存在
            2. 调用loop_execute执行所有测试步骤
            3. 无论成功失败都会执行后置清理操作
            
            Raises:
                RuntimeError: 当无法获取WEB测试相关数据时抛出
                Exception: 测试步骤执行过程中的各种异常
        """
        if self.case_message['optList'] is None:  # 检查操作列表是否存在
            self.after_execute()  # 执行清理操作
            raise RuntimeError("无法获取WEB测试相关数据, 请重试!!!")  # 抛出运行时异常
        try:
            self.loop_execute(self.case_message['optList'], [])  # 执行操作列表，初始跳过列表为空
        finally:
            self.after_execute()  # 无论成功失败都执行后置清理

    def loop_execute(self, opt_list, skip_opts, step_n=0):
        """循环执行测试步骤
        
            按顺序执行操作列表中的每个测试步骤，支持条件控制和循环控制
            
            Args:
                opt_list (list): 操作列表，包含所有测试步骤的配置信息
                skip_opts (list): 跳过的步骤索引列表，用于条件控制
                step_n (int): 当前步骤索引，默认从0开始
                
            主要功能：
            1. 遍历操作列表中的每个步骤
            2. 为每个步骤创建收集器和执行器
            3. 处理条件控制逻辑（跳过特定步骤）
            4. 处理循环控制逻辑（looper类型操作）
            5. 执行常规操作步骤
            6. 处理异常并保存截图
            
            异常处理：
            - 捕获所有异常并重新抛出
            - 对于非断言异常，自动保存截图
        """
        while step_n < len(opt_list):  # 遍历操作列表中的每个步骤
            opt_content = opt_list[step_n]  # 获取当前步骤的配置内容
            # 为当前步骤创建操作收集器
            collector = WebOperationCollector()
            # 创建测试步骤执行器，传入测试实例、驱动、上下文和收集器
            step = WebTestStep(self.test, self.driver, self.context, collector)
            # 在测试框架中定义当前操作的事务信息
            self.test.defineTrans(opt_content["operationId"], opt_content['operationTrans'],
                                  self.get_opt_content(opt_content['operationElement']), opt_content['operationDesc'])
            # 检查当前步骤是否在跳过列表中（条件控制逻辑）
            if step_n in skip_opts:
                self.test.updateTransStatus(3)  # 更新事务状态为跳过
                self.test.debugLog('[{}]操作在条件控制之外不被执行'.format(opt_content['operationTrans']))  # 记录跳过日志
                step_n += 1  # 移动到下一步
                continue  # 跳过当前步骤的执行
            # 使用收集器收集当前步骤的操作信息
            step.collector.collect(opt_content)
            try:
                # 判断操作类型是否为循环控制器
                if step.collector.opt_type == "looper":
                    # 执行循环控制逻辑，返回循环执行的步骤数
                    looper_step_num = step.looper_controller(self, opt_list, step_n)
                    step_n += looper_step_num + 1  # 跳过循环内的步骤
                else:
                    # 执行常规操作步骤
                    self.render_content(step)  # 渲染步骤内容（处理模板变量）
                    step.execute()  # 执行具体的操作
                    step.assert_controller()  # 执行断言检查
                    skip_opts.extend(step.condition_controller(step_n))  # 处理条件控制，更新跳过列表
                    step_n += 1  # 移动到下一步
            except Exception as e:
                # 异常处理：对于非断言异常，保存截图
                if not isinstance(e, AssertionError):
                    self.test.saveScreenShot(opt_content['operationTrans'], self.driver.get_screenshot_as_png())
                raise e  # 重新抛出异常

    @staticmethod
    def get_opt_content(elements):
        """获取操作元素的内容描述
        
            将操作元素字典转换为可读的字符串格式，用于事务描述
            
            Args:
                elements (dict): 操作元素字典，包含元素名称和目标信息
                
            Returns:
                str: 格式化后的元素内容描述字符串
                
            示例:
                elements = {
                    "button": {"target": "#submit-btn"},
                    "input": {"target": "input[name='username']"}}
                返回: "\n button: #submit-btn\n input: input[name='username']"
        """
        content = ""  # 初始化内容字符串
        if elements is not None:  # 检查元素字典是否存在
            for key, element in elements.items():  # 遍历所有元素
                # 格式化元素信息：元素名称和目标选择器
                content = "%s\n %s: %s" % (content, key, element["target"])
        return content  # 返回格式化后的内容

    def before_execute(self):
        """执行前置操作，启动和配置WebDriver
        
            根据用例配置决定是否启动新的WebDriver实例，并进行相应配置
            
            Returns:
                WebDriver: 配置好的WebDriver实例
                
            主要功能：
            1. 检查是否需要启动新的驱动
            2. 配置Chrome浏览器选项
            3. 处理各种驱动设置（参数、实验选项、扩展等）
            4. 支持无头模式和远程模式
            5. 复用现有驱动或抛出异常
            
            Raises:
                RuntimeError: 当无法找到已启动的浏览器进程时抛出
        """
        old_driver = self.test.driver.driver  # 获取现有的WebDriver实例
        if self.case_message["startDriver"]:  # 检查是否需要启动新的驱动
            # 创建Chrome浏览器选项对象
            opt = webdriver.ChromeOptions()
            # 渲染驱动设置配置（处理模板变量）
            driver_setting = self.render_driver(self.case_message["driverSetting"])
            # 处理启动参数配置
            if "arguments" in driver_setting.keys():
                for item in driver_setting["arguments"]:
                    if item["value"] != "":  # 跳过空值参数
                        opt.add_argument(item["value"])  # 添加Chrome启动参数
            # 处理实验性选项配置
            if "experimentals" in driver_setting.keys():
                for item in driver_setting["experimentals"]:
                    if item["name"] != "" and item["value"] != "":  # 确保名称和值都不为空
                        # 添加实验性选项，根据类型处理值
                        opt.add_experimental_option(item["name"], handle_operation_data(item["type"], item["value"]))
            # 处理编码扩展配置
            if "extensions" in driver_setting.keys():
                for item in driver_setting["extensions"]:
                    if item["value"] != "":  # 跳过空值扩展
                        opt.add_encoded_extension(item["value"])  # 添加Base64编码的扩展
            # 处理扩展文件配置
            if "files" in driver_setting.keys():
                for item in driver_setting["files"]:
                    if item["value"] != "":  # 跳过空值文件
                        opt.add_extension(item["value"])  # 添加扩展文件路径
            # 处理Chrome二进制文件路径配置
            if "binary" in driver_setting.keys() and driver_setting["binary"] != "":
                opt.binary_location = driver_setting["binary"]  # 设置Chrome可执行文件路径
            # 根据浏览器运行模式进行配置
            if self.test.driver.browser_opt == "headless":  # 无头模式配置
                opt.add_argument("--headless")  # 启用无头模式
                opt.add_argument("--no-sandbox")  # 禁用沙箱模式
            elif self.test.driver.browser_opt == "remote":  # 远程模式配置
                caps = {
                    'browserName': 'chrome'  # 设置浏览器类型为Chrome
                }
            else:  # 普通模式配置
                opt.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用日志输出
            # 清理旧的WebDriver实例
            if old_driver is not None:
                old_driver.quit()  # 退出旧的浏览器实例
            self.test.driver.driver = None  # 重置驱动引用
            # 根据模式创建WebDriver实例
            if self.test.driver.browser_opt == "remote":
                # 创建远程WebDriver实例
                return webdriver.Remote(command_executor=self.test.driver.browser_path,
                                        desired_capabilities=caps, options=opt)
            else:
                # 创建本地Chrome WebDriver实例
                return webdriver.Chrome(executable_path=self.test.driver.browser_path, options=opt)
        else:  # 不启动新驱动的情况
            if old_driver is not None:
                return old_driver  # 复用现有驱动
            else:
                # 抛出异常：无法找到现有驱动
                raise RuntimeError("无法找到已启动的浏览器进程 请检查用例开关驱动配置")

    def after_execute(self):
        """执行后置清理操作
        
            根据用例配置决定是否关闭WebDriver，或者保留供后续使用
            
            主要功能：
            1. 检查是否需要关闭驱动
            2. 关闭驱动或保留驱动引用
            3. 更新测试实例的驱动状态
        """
        if self.case_message["closeDriver"]:  # 检查是否需要关闭驱动
            self.driver.quit()  # 退出WebDriver实例
            self.test.driver.driver = None  # 清空驱动引用
        else:
            self.test.driver.driver = self.driver  # 保留驱动引用供后续使用

    def render_driver(self, driver_setting):
        """渲染驱动设置配置
        
            使用模板引擎处理驱动设置中的模板变量
            
            Args:
                driver_setting: 驱动设置配置字典
                
            Returns:
                dict: 渲染后的驱动设置配置
        """
        self.template.init(driver_setting)  # 初始化模板数据
        return self.template.render()  # 渲染并返回结果

    def render_looper(self, looper):
        """渲染循环控制器配置
        
            处理循环控制器的模板变量和数据类型转换
            
            Args:
                looper: 循环控制器配置字典
                
            Returns:
                dict: 渲染和处理后的循环控制器配置
                
            主要处理：
            1. 模板变量渲染
            2. 数据类型转换（除了target和expect字段）
            3. 循环次数的整数转换和默认值处理
        """
        self.template.init(looper)  # 初始化模板数据
        _looper = self.template.render()  # 渲染模板变量
        # 遍历所有参数进行数据类型处理
        for name, param in _looper.items():
            if name != "target" or name != "expect":  # 断言实际值不作数据处理
                _looper[name] = handle_operation_data(param["type"], param["value"])
        # 处理循环次数参数
        if "times" in _looper:
            try:
                times = int(_looper["times"])  # 尝试转换为整数
            except:
                times = 1  # 转换失败时默认为1
            _looper["times"] = times  # 设置处理后的次数
        return _looper  # 返回处理后的配置

    def render_content(self, step):
        """渲染测试步骤内容
        
            处理测试步骤中的模板变量，包括操作元素和操作数据
            
            Args:
                step: 测试步骤对象，包含收集器和操作信息
                
            主要功能：
            1. 渲染操作元素中的模板变量
            2. 渲染操作数据中的模板变量
            3. 进行数据类型转换和处理
        """
        # 处理操作元素的模板渲染
        if step.collector.opt_element is not None:
            for name, expressions in step.collector.opt_element.items():
                expression = expressions[1]  # 获取元素表达式（第二个元素）
                # 检查表达式中是否包含模板变量
                if self.comp.search(str(expression)) is not None:
                    self.template.init(expression)  # 初始化模板数据
                    render_value = self.template.render()  # 渲染模板变量
                    expressions = (expressions[0], str(render_value))  # 更新表达式元组
                step.collector.opt_element[name] = expressions  # 保存处理后的元素表达式
        # 处理操作数据的模板渲染和类型转换
        if step.collector.opt_data is not None:
            data = {}  # 创建新的数据字典
            for name, param in step.collector.opt_data.items():
                param_value = param["value"]  # 获取参数值
                # 检查参数值是否为字符串且包含模板变量
                if isinstance(param_value, str) and self.comp.search(param_value) is not None:
                    self.template.init(param_value)  # 初始化模板数据
                    param_value = self.template.render()  # 渲染模板变量
                # 根据参数类型进行数据处理和转换
                data[name] = handle_operation_data(param["type"], param_value)
            step.collector.opt_data = data  # 更新操作数据

