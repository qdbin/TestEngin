"""Web自动化测试步骤执行模块

    该模块负责执行Web自动化测试中的单个测试步骤，包括操作执行、
    循环控制、断言控制、条件控制等核心功能。
    
    主要功能：
    1. 测试步骤的执行和结果处理
    2. 循环控制器（While循环和For循环）
    3. 断言控制器（成功/失败处理）
    4. 条件控制器（分支跳转逻辑）
    5. 操作日志记录和显示
    6. 异常处理和错误截图
    
    作者: LiuMa团队
    日期: 2024
"""

import sys  # 系统相关功能，用于异常信息处理
from datetime import datetime  # 日期时间处理，用于循环超时控制
from core.assertion import LMAssert  # 断言模块，用于条件判断和断言验证
from core.web.find_opt import *  # Web操作查找模块，用于获取具体的操作函数


class WebTestStep:
    """Web测试步骤执行器
    
        负责执行单个Web测试步骤，包括操作执行、结果处理、
        循环控制、断言控制和条件控制等功能。
        
        主要职责：
        1. 根据操作类型查找并执行相应的操作函数
        2. 处理循环控制逻辑（While循环和For循环）
        3. 处理断言结果和失败截图
        4. 处理条件分支跳转逻辑
        5. 记录和显示操作日志信息
        
        Attributes:
            test: 测试实例，用于日志记录和状态管理
            driver: WebDriver实例，用于浏览器操作
            context: 测试上下文，用于变量存储和传递
            collector: 操作收集器，包含操作的详细信息
            result: 操作执行结果
    """
    
    def __init__(self, test, driver, context, collector):
        """初始化Web测试步骤执行器
        
            Args:
                test: 测试实例对象
                driver: WebDriver驱动实例
                context: 测试上下文字典
                collector: 操作信息收集器对象
        """
        self.test = test  # 测试实例，提供日志和状态管理功能
        self.driver = driver  # WebDriver实例，用于浏览器操作
        self.context = context  # 测试上下文，存储变量和数据
        self.collector = collector  # 操作收集器，包含操作的所有信息
        self.result = None  # 操作执行结果，初始为None

    def execute(self):
        """执行Web测试步骤
        
            根据操作类型查找对应的操作函数并执行，记录执行过程和结果
            
            主要流程：
            1. 记录操作开始日志
            2. 根据操作类型查找对应的操作函数
            3. 构建操作参数并执行操作
            4. 记录操作结果和日志
            5. 确保记录操作结束日志
            
            Raises:
                NotExistedWebOperation: 当操作类型未定义时抛出异常
        """
        try:
            # 记录操作开始日志
            self.test.debugLog('WEB操作[{}]开始'.format(self.collector.opt_name))
            opt_type = self.collector.opt_type  # 获取操作类型
            
            # 根据操作类型查找对应的操作函数
            if opt_type == "browser":
                func = find_browser_opt(self.collector.opt_name)  # 浏览器操作
            elif opt_type == "page":
                func = find_page_opt(self.collector.opt_name)  # 页面操作
            elif opt_type == "condition":
                func = find_condition_opt(self.collector.opt_name)  # 条件操作
            elif opt_type == "assertion":
                func = find_assertion_opt(self.collector.opt_name)  # 断言操作
            elif opt_type == "relation":
                func = find_relation_opt(self.collector.opt_name)  # 关联操作
            else:
                func = find_scenario_opt(self.collector.opt_name)  # 场景操作
            
            # 检查操作函数是否存在
            if func is None:
                raise NotExistedWebOperation("未定义操作")
            
            # 构建操作参数字典
            opt_content = {
                "trans": self.collector.opt_trans,  # 操作描述
                "code": self.collector.opt_code,  # 操作代码
                "element": self.collector.opt_element,  # 元素定位信息
                "data": self.collector.opt_data  # 操作数据
            }
            
            # 执行操作函数并获取结果
            self.result = func(self.test, self.driver, **opt_content)
            # 显示操作日志信息
            self.log_show()
        finally:
            # 确保记录操作结束日志
            self.test.debugLog('WEB操作[{}]结束'.format(self.collector.opt_name))

    def looper_controller(self, case, opt_list, step_n):
        """循环控制器
        
            处理While循环和For循环两种循环类型的控制逻辑
            
            Args:
                case: 测试用例实例，用于执行循环内的操作
                opt_list: 完整的操作列表
                step_n: 当前步骤在操作列表中的索引
                
            Returns:
                int: 循环体包含的步骤数量
                
            循环类型：
            1. While循环：基于条件和超时控制的循环
            2. For循环：基于次数控制的循环
        """
        if self.collector.opt_trans == "While循环":
            # While循环处理逻辑
            loop_start_time = datetime.now()  # 记录循环开始时间
            timeout = int(self.collector.opt_data["timeout"]["value"])  # 获取超时时间（毫秒）
            index_name = self.collector.opt_data["indexName"]["value"]  # 获取循环索引变量名
            steps = int(self.collector.opt_data["steps"]["value"])  # 获取循环体步骤数
            index = 0  # 初始化循环索引
            
            # 循环条件：超时时间为0（无限循环）或未超时
            while timeout == 0 or (datetime.now() - loop_start_time).seconds * 1000 < timeout:
                # timeout为0时可能会死循环 慎重选择
                self.context[index_name] = index  # 给循环索引赋值第几次循环 母循环和子循环的索引名不应一样
                _looper = case.render_looper(self.collector.opt_data)  # 渲染循环控制控制器 每次循环都需要渲染
                index += 1  # 递增循环索引
                
                # 执行循环条件断言判断
                result, _ = LMAssert(_looper['assertion'], _looper['target'], _looper['expect']).compare()
                if not result:  # 条件不满足时跳出循环
                    break
                    
                # 获取循环体操作列表（排除循环操作本身）
                _opt_list = opt_list[step_n+1: (step_n + _looper["steps"]+1)]   # 循环操作本身不参与循环 不然死循环
                case.loop_execute(_opt_list, [])  # 执行循环体操作
            return steps  # 返回循环体步骤数
        else:
            # For循环处理逻辑
            _looper = case.render_looper(self.collector.opt_data) # 渲染循环控制控制器 for只需渲染一次
            for index in range(_looper["times"]):  # 本次循环次数
                self.context[_looper["indexName"]] = index  # 给循环索引赋值第几次循环 母循环和子循环的索引名不应一样
                # 获取循环体操作列表
                _opt_list = opt_list[step_n+1: (step_n + _looper["steps"]+1)]
                case.loop_execute(_opt_list, [])  # 执行循环体操作
            return _looper["steps"]  # 返回循环体步骤数

    def assert_controller(self):
        """断言控制器
        
            处理断言操作的结果，包括成功日志记录、失败处理和异常抛出
            
            主要功能：
            1. 判断断言结果并记录相应日志
            2. 断言失败时保存错误截图
            3. 根据continue配置决定是否继续执行
            4. 抛出断言异常或记录失败状态
            
            断言处理逻辑：
            - 成功：记录调试日志
            - 失败且continue=True：记录失败状态但继续执行
            - 失败且continue=False：抛出异常中断执行
        """
        # 只处理断言类型的操作
        if self.collector.opt_type == "assertion":
            if self.result[0]:  # 断言成功
                # 记录断言成功的调试日志
                self.test.debugLog('[{}]断言成功: {}'.format(self.collector.opt_trans,
                                                             self.result[1]))
            else:  # 断言失败
                # 记录断言失败的错误日志
                self.test.errorLog('[{}]断言失败: {}'.format(self.collector.opt_trans,
                                                             self.result[1]))
                # 保存失败时的屏幕截图
                self.test.saveScreenShot(self.collector.opt_trans, self.driver.get_screenshot_as_png())
                
                # 检查是否配置了继续执行标志
                if "continue" in self.collector.opt_data and self.collector.opt_data["continue"] is True:
                    try:
                        # 抛出断言异常但不中断执行
                        raise AssertionError(self.result[1])
                    except AssertionError:
                        # 捕获异常信息并记录失败状态
                        error_info = sys.exc_info()
                        self.test.recordFailStatus(error_info)
                else:
                    # 直接抛出断言异常，中断测试执行
                    raise AssertionError(self.result[1])

    def condition_controller(self, current):
        """条件控制器
        
            处理条件判断操作的结果，根据判断结果决定跳过哪些步骤
            
            Args:
                current: 当前步骤在操作列表中的索引位置
                
            Returns:
                list: 需要跳过的步骤索引列表
                
            分支逻辑：
            - 条件成功：跳过失败分支的步骤，执行成功分支
            - 条件失败：跳过成功分支的步骤，执行失败分支
            
            参数说明：
            - true: 成功分支包含的步骤数
            - false: 失败分支包含的步骤数
        """
        # 只处理条件类型的操作
        if self.collector.opt_type == "condition":
            # 获取成功分支步骤数，默认为0
            offset_true = self.collector.opt_data["true"]
            if not isinstance(offset_true, int):
                offset_true = 0
            
            # 获取失败分支步骤数，默认为0
            offset_false = self.collector.opt_data["false"]
            if not isinstance(offset_false, int):
                offset_false = 0
            
            if self.result[0]:  # 条件判断成功
                # 记录条件成功日志
                self.test.debugLog('[{}]判断成功, 执行成功分支: {}'.format(self.collector.opt_name,
                                                                        self.result[1]))
                # 返回需要跳过的失败分支步骤索引列表
                return [current + i for i in range(offset_true + 1, offset_true + offset_false + 1)]
            else:  # 条件判断失败
                # 记录条件失败日志
                self.test.errorLog('[{}]判断失败, 执行失败分支: {}'.format(self.collector.opt_name,
                                                                        self.result[1]))
                # 返回需要跳过的成功分支步骤索引列表
                return [current + i for i in range(1, offset_true + 1)]
        return []  # 非条件操作返回空列表

    def log_show(self):
        """日志显示方法
        
            显示操作的详细信息，包括元素定位信息和操作数据
            
            主要功能：
            1. 显示元素定位信息（如果存在）
            2. 显示操作数据信息（如果存在）
            3. 格式化并记录操作信息日志
            
            日志格式：
            - 元素定位: 定位方式: 定位值
            - 操作数据: {参数名: 参数值, ...}
        """
        msg = ""  # 初始化日志消息字符串
        
        # 处理元素定位信息
        if self.collector.opt_element is not None:
            for k, v in self.collector.opt_element.items():
                # 添加元素定位信息到日志消息
                msg += '元素定位: {}: {}<br>'.format(k, v)
        
        # 处理操作数据信息
        if self.collector.opt_data is not None:
            data_log = '{'  # 开始构建数据日志字符串
            for k, v in self.collector.opt_data.items():
                class_name = type(v).__name__  # 获取数据类型名称（暂未使用）
                # 添加参数键值对到数据日志
                data_log += "{}: {}, ".format(k, v)
            
            # 移除最后的逗号和空格
            if len(data_log) > 1:
                data_log = data_log[:-2]
            data_log += '}'  # 结束数据日志字符串
            
            # 添加操作数据信息到日志消息
            msg += '操作数据: {}'.format(data_log)
        
        # 如果有日志信息则记录到测试日志中
        if msg != "":
            msg = '操作信息: <br>' + msg  # 添加操作信息标题
            self.test.debugLog(msg)  # 记录调试日志


class NotExistedWebOperation(Exception):
    """未定义的WEB操作"""
