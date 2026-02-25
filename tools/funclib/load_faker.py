# -*- coding: utf-8 -*-
"""
    自定义Faker数据生成器模块

    本模块扩展了Faker库的功能，支持动态加载自定义数据提供者和用户自定义函数。
    主要用于测试数据生成，支持多种数据类型和自定义业务逻辑。

"""

import os  # 文件系统操作
from faker import Faker  # 基础数据生成库
from importlib import import_module, reload  # 动态模块导入和重载
import sys  # 系统相关功能
from faker.providers import BaseProvider  # Faker提供者基类
from tools.funclib.params_enum import PARAMS_ENUM  # 参数类型枚举


class CustomFaker(Faker):
    """
        自定义Faker数据生成器类
        
        继承自Faker类，扩展了动态加载自定义提供者和用户自定义函数的功能。
        支持从指定包中加载数据提供者，并支持执行用户自定义的Python代码函数。
        
        Attributes:
            package (str): 自定义提供者包名，默认为'provider'
            test: 测试实例对象，用于函数执行时的上下文
            lm_func (list): 用户自定义函数列表
            temp (dict): 临时数据存储，包含上下文和参数
            func_param (dict): 函数参数类型映射
        
        Example:
            >>> faker = CustomFaker(package='provider', lm_func=[])
            >>> faker.name()  # 调用内置函数
            'John Doe'
            >>> faker('custom_func', arg1, arg2)  # 调用自定义函数
    """
    
    def __init__(self, package: str = 'provider', test=None, lm_func: list = None, temp: dict = None, *args, **kwargs):
        """
            初始化自定义Faker实例
            
            Args:
                package (str): 自定义提供者包名，默认为'provider'
                test: 测试实例对象，用于提供执行上下文
                lm_func (list): 用户自定义函数配置列表，默认为空列表
                temp (dict): 临时数据存储字典，包含context和params
                *args: 传递给父类Faker的位置参数
                **kwargs: 传递给父类Faker的关键字参数
            
            Note:
                初始化过程中会自动加载自定义模块和用户自定义函数
        """
        super().__init__(*args, **kwargs)  # 调用父类初始化方法
        
        # 处理默认参数
        if lm_func is None:
            lm_func = []
        
        # 设置实例属性
        self.package = package  # 自定义提供者包名
        self.test = test  # 测试实例对象（testcase）
        self.print = print  # 保存原始print函数引用
        self.lm_func = lm_func  # 用户自定义函数列表
        self.temp = temp  # 临时数据的提取和存储（context和公共params）
        self.func_param = PARAMS_ENUM  # 函数参数类型枚举
        
        # 加载自定义模块和函数
        self._load_module()  # 加载自定义数据提供者模块，将基于baseprovider的自定义类（数据提供者）的方法属性加载到faker子类中
        self._load_lm_func()  # 加载用户自定义函数

    def __call__(self, name: str, *args, **kwargs):
        """
            使实例可调用，支持动态调用方法
            
            通过方法名动态调用实例的方法，支持传递任意参数。
            这使得可以通过字符串方式调用Faker的各种数据生成方法。
            
            Args:
                name (str): 要调用的方法名
                *args: 传递给方法的位置参数
                **kwargs: 传递给方法的关键字参数
            
            Returns:
                调用方法的返回值
            
            Example:
                >>> faker = CustomFaker()
                >>> faker('name')  # 等同于 faker.name()
                'John Doe'
                >>> faker('random_int', min=1, max=100)  # 等同于 faker.random_int(min=1, max=100)
                42
        """
        return getattr(self, name)(*args, **kwargs)  # 动态获取并调用指定方法

    def _read_module(self) -> list:
        """
            读取自定义提供者模块列表
            
            扫描指定包目录下的所有Python文件，构建模块名列表。
            用于后续动态导入和加载自定义数据提供者。
            
            Returns:
                list: 模块名列表，格式为完整的模块路径
            
            Example:
                >>> faker._read_module()
                ['tools.funclib.provider.custom_provider', 'tools.funclib.provider.another_provider']
        """
        # 构建模块目录路径
        module_path = os.path.join(os.path.dirname(__file__), self.package)
        module_list = []  # 存储模块名列表
        
        # 遍历目录中的所有文件
        for file_name in os.listdir(module_path):
            # 检查是否为Python文件（以.py结尾）
            if file_name[-2:] == "py":
                # 构建完整的模块名：包名.子包名.文件名（不含.py扩展名）
                module_name = __package__ + "." + self.package + "." + file_name[0:-3]
                module_list.append(module_name)  # 添加到模块列表
        
        return module_list

    def _load_module(self):
        """
            动态加载自定义数据提供者模块
            
            遍历指定包中的所有模块，导入或重载模块，并将其中继承自BaseProvider的类
            注册为Faker的数据提供者。支持热重载，确保模块更新后能够生效。
            
            Note:
                - 如果模块未加载，则导入模块
                - 如果模块已加载，则重载模块以获取最新代码
                - 只有继承自BaseProvider的类才会被注册为提供者
            
            Example:
                加载provider包下的所有自定义提供者：
                >>> faker._load_module()
                # 自动注册所有继承自BaseProvider的提供者类
        """
        # 遍历所有./provider/.py模块
        for name in self._read_module():
            # 检查模块是否已经加载
            if name not in sys.modules:
                # 模块未加载，进行导入
                module = import_module(name)
            else:
                # 模块已加载，进行重载以获取最新代码
                module = sys.modules.get(name)
                reload(module)
            
            # 遍历模块中的所有属性
            for value in module.__dict__.values():
                # 检查是否为类且继承自BaseProvider
                if type(value) is type and BaseProvider in value.__bases__:
                    # 将符合条件的类注册为Faker提供者
                    self.add_provider(value)

    def _load_lm_func(self):
        """
            ### 加载用户自定义函数
            
            遍历用户自定义函数配置列表，为每个函数创建可执行的Python函数对象，
            并将其绑定到当前实例。同时处理函数参数类型映射。
            
            ### 自定义函数配置格式：
            {
                "name": "函数名",
                "code": "Python代码字符串",
                "params": {
                    "names": ["arg01", "arg02"],
                    "types": ["string", "dict"]
                }
            }
            
            ### 支持的参数类型：
            - Int: 整数类型
            - Float: 浮点数类型
            - Boolean: 布尔类型
            - Bytes: 字节类型
            - JSONObject: 字典类型
            - JSONArray: 列表类型
            - Other: 无类型限制
            - 其他: 字符串类型（默认）
            
            ### Note:
                函数执行时会提供特殊的内置函数：
                - print: 重定向输出到测试缓冲区
                - sys_return: 设置函数返回值
                - sys_get: 获取公共参数或关联变量
                - sys_put: 设置公共参数或关联变量
        """
        # 遍历所有自定义函数配置
        for custom in self.lm_func:
            # 创建自定义函数对象
            func = self._lm_custom_func(custom["code"], custom["params"]["names"], self.test, self.temp)
            
            # 处理参数类型映射
            params = []  # 存储参数类型列表
            for value in custom["params"]["types"]:
                # 根据类型字符串映射到Python类型
                if value == "Int":
                    params.append(int)  # 整数类型
                elif value == "Float":
                    params.append(float)  # 浮点数类型
                elif value == "Boolean":
                    params.append(bool)  # 布尔类型
                elif value == "Bytes":
                    params.append(bytes)  # 字节类型
                elif value == "JSONObject":
                    params.append(dict)  # 字典类型
                elif value == "JSONArray":
                    params.append(list)  # 列表类型
                elif value == "Other":
                    params.append(None)  # 无类型限制
                else:
                    params.append(str)  # 默认为字符串类型
            
            # 保存函数参数类型信息
            self.func_param[custom["name"]] = params

            # 将函数绑定到当前实例
            setattr(self, custom["name"], func)

    def _lm_custom_func(self, code: str, params: list, test, temp: dict):
        """
            创建用户自定义函数的执行器
            
            根据用户提供的Python代码字符串和参数列表，创建一个可执行的函数对象。
            该函数在执行时会提供特殊的内置函数和变量访问能力。
            
            Args:
                code (str): 用户自定义的Python代码字符串
                params (list): 函数参数名列表
                test: 测试实例对象，用于提供执行上下文
                temp (dict): 临时数据存储，包含context和params
            
            Returns:
                function: 可执行的函数对象
            
            Note:
                创建的函数会提供以下内置函数：
                - print: 重定向输出到测试缓冲区
                - sys_return: 设置函数返回值
                - sys_get: 获取公共参数或关联变量
                - sys_put: 设置公共参数或关联变量
            
            Example:
                >>> func = faker._lm_custom_func('sys_return("Hello")', [], test, temp)
                >>> result = func()
                >>> print(result)  # 输出: Hello
        """
        def func(*args):
            """
                用户自定义函数的实际执行函数
                
                Args:
                    *args: 传递给用户函数的参数
                
                Returns:
                    用户函数通过sys_return设置的返回值
            """
            # 重定义print函数，将输出重定向到测试缓冲区
            def print(*args, sep=' ', end='\n', file=None, flush=False):
                """
                重定向的print函数，输出到测试缓冲区而非标准输出
                """
                if file is None or file in (sys.stdout, sys.stderr):
                    file = names["_test"].stdout_buffer  # 重定向到测试缓冲区
                self.print(*args, sep=sep, end=end, file=file, flush=flush)

            def sys_return(res):
                """
                设置函数返回值
                
                Args:
                    res: 要返回的值
                """
                names["_exec_result"] = res

            def sys_get(name: str):
                """
                    获取公共参数或关联变量
                    
                    Args:
                        name (str): 变量名
                    
                    Returns:
                        变量值
                    
                    Raises:
                        KeyError: 当变量不存在时
                """
                if name in names["_test_context"]:
                    return names["_test_context"][name]  # 从测试上下文获取
                elif name in names["_test_params"]:
                    return names["_test_params"][name]  # 从测试参数获取
                else:
                    raise KeyError("不存在的公共参数或关联变量: {}".format(name))

            def sys_put(name: str, val, ps: bool = False):
                """
                    设置公共参数或关联变量
                    
                    Args:
                        name (str): 变量名
                        val: 变量值
                        ps (bool): 是否设置为公共参数，False表示设置为上下文变量
                """
                if ps:
                    names["_test_params"][name] = val  # 设置为公共参数
                else:
                    names["_test_context"][name] = val  # 设置为上下文变量

            # 初始化执行环境
            names = locals()  # 获取局部变量字典
            names["_test_context"] = temp["context"]  # 设置测试上下文
            names["_test_params"] = temp["params"]  # 设置测试参数
            names["_test"] = test  # 设置测试实例
            
            # 将传入的参数绑定到对应的参数名
            for index, value in enumerate(params):
                names[value] = args[index]  # 参数名 -> 参数值  ['args01', 'args02','args03']
            
            # 执行用户代码
            exec(code)
            
            # 返回用户设置的结果
            return names["_exec_result"]
        
        return func
