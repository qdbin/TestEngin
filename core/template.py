from functools import reduce  # 用于序列累积操作，主要用于字符串连接和参数列表处理
from hashlib import md5  # MD5哈希算法，用于生成字节数据的唯一标识符
from jsonpath import jsonpath  # JSONPath查询库，用于在复杂数据结构中查找和提取数据
from jsonpath_ng.parser import JsonPathParser  # JSONPath解析器，用于解析和执行JSONPath表达式
from tools.funclib import get_func_lib  # 获取函数库实例，提供模板中可调用的内置函数
import json  # JSON处理模块，用于数据序列化和反序列化
import re  # 正则表达式模块，用于模板语法解析和字符串匹配
import time  # 时间处理模块，用于生成时间戳和唯一标识符

from tools.utils.utils import extract_by_jsonpath, quotation_marks  # 工具函数：JSONPath提取和字符串引号处理


class Template:
    """
        模板引擎类
        
        用于处理测试数据中的模板变量、函数调用和参数替换。支持变量插值、
        函数调用、JSONPath提取和字节数据处理等功能，是自动化测试框架
        中数据处理的核心组件。
        
        主要功能：
            - 变量插值：将模板中的变量占位符替换为实际值
            - 函数调用：执行内置函数并返回结果
            - JSONPath提取：从复杂数据结构中提取指定数据
            - 字节数据处理：支持二进制数据的保存和还原
            - 特殊引用处理：处理请求数据引用和响应数据引用
        
        支持的模板语法：
            - 变量引用：${variable_name}
            - 函数调用：${@function_name(args)}
            - JSONPath：${variable.path[0].field}
            - 请求数据引用：${request.body.field}
            - 响应数据引用：${response.json.field}
            - 字节数据引用：${bytes_data_key}
        
        Attributes:
            function_prefix (str): 函数调用前缀，默认为'@'
            func_lib (FuncLib): 函数库实例，提供可调用的内置函数
            help_data (dict): 辅助数据字典，存储请求和响应数据
            bytes_data (dict): 字节数据存储字典
            bytes_key_list (list): 字节数据键列表
        
        Example:
            >>> template = Template()
            >>> template.init({'name': 'test', 'count': 10})
            >>> result = template.render('Hello ${name}, count: ${count}')
            >>> # 返回: 'Hello test, count: 10'
            
            >>> # 函数调用示例
            >>> result = template.render('Random: ${@random_int(1,100)}')
            >>> # 返回: 'Random: 42' (随机数)
            
            >>> # JSONPath提取示例
            >>> template.init({'user': {'profile': {'name': 'Alice'}}})
            >>> result = template.render('Name: ${user.profile.name}')
            >>> # 返回: 'Name: Alice'
    """

    def __init__(self, test, context, functions, params, variable_start_string='{{', variable_end_string='}}', function_prefix='@', param_prefix='$'):
        """
            初始化模板引擎
            
            创建模板引擎实例并初始化所有必要的属性。设置模板解析参数、
            创建函数库实例、初始化数据存储容器等。
            
            Args:
                test: 测试实例对象，用于输出日志和错误信息
                context (dict): 关联参数字典，存储测试过程中的动态变量
                functions (dict): 函数库字典，包含可调用的内置函数
                params (dict): 公共参数字典，存储全局配置参数
                variable_start_string (str): 变量开始标识符，默认'{{'
                variable_end_string (str): 变量结束标识符，默认'}}'
                function_prefix (str): 函数调用前缀，默认'@'
                param_prefix (str): 参数前缀，默认'$'
            
            初始化的属性：
                - test: 测试实例对象
                - data: 待渲染的数据（JSON字符串格式）
                - context: 关联参数字典
                - params: 公共参数字典
                - variable_start_string/variable_end_string: 变量标识符
                - function_prefix: 函数调用前缀
                - param_prefix: 参数前缀
                - stack: 字符栈，用于模板解析
                - request_*: 请求相关数据存储
                - func_lib: 函数库实例
                - bytes_map: 字节数据映射表
                - parser: JSONPath解析器
            
            Note:
                初始化后需要调用init()方法设置模板数据，
                然后才能使用render()方法进行模板渲染。
            
            Example:
                >>> template = Template(test, {}, functions, {"base_url": "http://api.test.com"})
        """
        self.test = test  # 测试实例对象，用于日志输出和错误处理
        self.param_prefix = param_prefix  # 参数前缀标识符
        self.data = None  # 待渲染的数据（JSON字符串格式）
        self.context = context  # 关联参数字典，存储测试过程中的动态变量
        self.params = params  # 公共参数字典，存储全局配置参数
        self.variable_start_string = variable_start_string  # 变量开始标识符
        self.variable_end_string = variable_end_string  # 变量结束标识符
        self.function_prefix = function_prefix  # 函数调用前缀标识符
        self.param_prefix = param_prefix  # 参数前缀标识符（重复赋值）
        self.stack = list()  # 字符栈，用于逐字符解析模板
        # 动态存储HTTP请求信息，用于模板渲染中的请求数据引用
        self.request_url = None  # 完整的请求URL
        self.request_path = None  # 请求路径
        self.request_headers = None  # 请求头字典
        self.request_query = None  # 查询参数字典
        self.request_body = None  # 请求体字典
        self.func_lib = get_func_lib(test, functions, self.context, self.params)  # 获取函数库实例，faker实例
        self.bytes_map = dict()  # 字节数据映射表，用于存储和还原字节数据
        self.parser = JsonPathParser()  # JSONPath解析器实例

    def init(self, data):
        """
            初始化待渲染的数据
            
            将输入数据转换为JSON字符串格式，并清空内部状态。这是模板渲染
            的第一步，必须在调用render()方法之前执行。
            
            Args:
                data: 待渲染的数据，可以是字典、列表或其他可序列化对象。
                    通常包含模板变量占位符，如{{variable}}或@function()格式。
            
            功能说明：
                - 将数据序列化为JSON字符串，便于逐字符解析
                - 清空字符栈，准备新的解析过程
                - 清空字节映射表，避免数据污染
            
            Note:
                数据会被转换为JSON字符串格式，因此原始数据必须是可序列化的。
                如果数据包含不可序列化的对象，会抛出异常。
            
            Example:
                >>> template.init({"name": "{{username}}", "age": "@random_int(18,65)"})
                >>> # 数据被转换为JSON字符串并存储在self.data中
        """
        self.data = json.dumps(data, ensure_ascii=False)  # 转换为JSON字符串，保持中文字符
        self.stack.clear()  # 清空字符栈，准备新的解析过程
        self.bytes_map.clear()  # 清空字节映射表，避免数据污染

    def set_help_data(self, url, path: str, headers: dict, query: dict, body: dict):
        """
            设置请求辅助数据
            
            存储HTTP请求的相关信息，用于在模板渲染过程中引用请求数据。
            这些数据可以通过特殊的引用语法在模板中使用，实现动态数据引用。
            
            Args:
                url (str): 完整的请求URL，包含协议、域名、端口和路径
                path (str): 请求路径部分，不包含域名和查询参数
                headers (dict): 请求头字典，包含所有HTTP头信息
                query (dict): 查询参数字典，URL中?后面的参数
                body (dict): 请求体字典，POST/PUT等请求的数据载荷
            
            功能说明：
                - 存储的数据可在模板中通过特殊语法引用
                - 支持在断言、关联参数提取等场景中使用
                - 为模板渲染提供请求上下文信息
            
            使用场景：
                - 在响应断言中引用请求数据进行对比
                - 在关联参数提取中引用请求信息
                - 在后续请求中引用前一个请求的数据
            
            Example:
                >>> template.set_help_data(
                ...     "http://api.test.com/users",
                ...     "/users",
                ...     {"Content-Type": "application/json"},
                ...     {"page": 1},
                ...     {"name": "test"}
                ... )
                >>> # 之后可在模板中使用 #{_request_body.name} 引用请求体中的name字段
        """
        self.request_url = url  # 存储完整的请求URL
        self.request_path = path  # 存储请求路径
        self.request_headers = headers  # 存储请求头信息
        self.request_query = query  # 存储查询参数
        self.request_body = body  # 存储请求体数据

    def render(self):
        """
            执行模板渲染
            
            解析并替换模板中的变量、函数调用等占位符，返回渲染后的结果。
            这是模板引擎的核心方法，支持多种模板语法和复杂的数据处理。
            
            支持的模板语法：
                - 变量插值: {{variable_name}} 或 {{variable.path}}
                - 函数调用: @function_name(args) 或 @function_name
                - JSONPath提取: 支持复杂的路径表达式
                - 字节数据处理: 自动处理二进制数据的编码转换
                - 特殊引用: 支持引用请求数据和响应数据
            
            渲染流程：
                1. 逐char遍历Json字符串，解析JSON字符串
                2. 识别模板占位符（{{}} 或 @函数）
                3. 提取变量名或函数调用
                4. 执行变量替换或函数调用
                5. 处理字节数据的编码转换
                6. 返回最终渲染结果
            
            Returns:
                渲染后的数据，类型与原始数据保持一致。如果原始数据是字典，
                返回字典；如果是列表，返回列表；如果是字符串，返回字符串。
            
            Raises:
                SplitFunctionError: 函数调用语法错误时抛出
                KeyError: 变量不存在时抛出
                Exception: 函数执行失败或其他处理异常
            
            Note:
                - 渲染过程中会自动处理字节数据的Base64编码
                - 支持嵌套的JSONPath表达式
                - 函数调用支持多种参数类型（字符串、数字、布尔值、列表、字典）
            
            Example:
                >>> template.init({"name": "{{username}}", "age": "@random_int(18,65)"})
                >>> result = template.render()
                >>> # 返回: {"name": "张三", "age": 25}
                >>> 
                >>> # 复杂示例
                >>> template.init({
                ...     "user": "{{user_info.name}}",
                ...     "token": "@generate_token({{user_info.id}})",
                ...     "data": "#{_request_body.data}"
                ... })
        """
        start_stack = list()  # 存储变量开始位置的栈，用于处理嵌套变量
        start_length = len(self.variable_start_string)  # 变量开始标识符长度（{{的长度）
        end_length = len(self.variable_end_string)  # 变量结束标识符长度（}}的长度）
        top = 0  # 栈顶指针，记录当前栈的大小
        flag = False  # 标记是否需要跳过下一个字符（处理JSON引号转义）
        for cur in range(len(self.data)):  # 逐字符遍历JSON数据字符串
            self.stack.append(self.data[cur])  # 将当前字符压入解析栈
            top += 1
            if flag:  # 如果需要跳过当前字符（JSON引号转义处理）
                self.stack.pop()  # 移除刚压入的字符
                top -= 1
                flag = False
                continue
            # 检查栈尾是否匹配变量开始标识符（{{）
            if reduce(lambda x, y: x + y, self.stack[-start_length:]) == self.variable_start_string:
                start_stack.append(top - start_length)  # 记录变量开始位置
            # 检查栈尾是否匹配变量结束标识符（}}）
            if reduce(lambda x, y: x + y, self.stack[-end_length:]) == self.variable_end_string:
                if len(start_stack) == 0:  # 没有对应的开始标识符，跳过
                    continue
                recent = start_stack.pop()  # 获取最近的变量开始位置
                tmp = ''  # 临时存储完整的变量表达式
                for _ in range(top - recent):  # 从栈中提取变量内容'{{xxx}}'
                    tmp += self.stack.pop()
                    top -= 1
                # 处理JSON字符串中的引号转义问题
                if self.stack[-1] == '"' and self.data[cur + 1] == '"':
                    self.stack.pop()  # 移除前引号
                    top -= 1
                    flag = True  # 标记跳过后引号
                else:
                    flag = False
                tmp = tmp[::-1]  # 反转字符串得到正确顺序
                key = tmp[start_length:-end_length].strip()  # 提取变量名（去掉{{}}）
                key, json_path = self.split_key(key)  # 分离变量名和JSONPath表达式  处理前后示例 ：data.items[0].name → ("data", "$.items[0].name")
                try:
                    # 处理函数调用（以@开头）
                    if key.startswith(self.function_prefix):
                        name_args = self.split_func(key, self.function_prefix)  # 解析函数名和参数  // 处理示例：@random_int(18,65) → ("random_int", 18, "65")
                        value = self.func_lib(name_args[0], *name_args[1:])  # 通过函数名和args为入参，执行faker.__call__执行内置自定义的函数
                    # 优先从关联参数中获取值（测试步骤间的数据传递）
                    elif key in self.context:   #{{xxxkey}}
                        if json_path is None:
                            value = self.context.get(key)  # 直接获取值
                        else:
                            value = extract_by_jsonpath(self.context.get(key), json_path)  # 使用JSONPath提取
                    # 从公共参数中获取值（全局配置参数）
                    elif key in self.params:
                        if json_path is None:
                            value = self.params.get(key)  # 直接获取值
                        else:
                            value = extract_by_jsonpath(self.params.get(key), json_path)  # 使用JSONPath提取
                    # 兼容老版本的参数前缀格式（$开头）  如：{{$key.data[0]}}
                    elif key.startswith(self.param_prefix) and key[1:] in self.params:
                        if json_path is None:
                            value = self.params.get(key[1:])  # 去掉前缀后获取值
                        else:
                            value = extract_by_jsonpath(self.params.get(key[1:]), json_path)  # 使用JSONPath提取
                    else:
                        value = tmp  # 未找到对应变量，保持原始表达式
                except:
                    value = tmp  # 异常时保持原始表达式
                    print('不存在的公共参数、关联变量或内置函数: {}'.format(key), file=self.test.stdout_buffer)

                # 根据值的类型进行不同的处理，确保JSON格式正确
                if not flag and isinstance(value, str):
                    # 处理字符串类型的值
                    if '"' in value and value != tmp:
                        value = json.dumps(value)[1:-1]  # 转义JSON字符串中的引号，去掉外层引号     '"value"'转储之后，变成了"\"value\""
                    final_value = value
                elif isinstance(value, bytes):
                    # 处理字节类型的值，保存到映射表并生成占位符
                    final_value = self._bytes_save(value, flag)     # 此次字节值先用'#{bytes_xxx_123}'表示，最后再转换
                elif isinstance(value, list):
                    # 处理列表类型的值，递归处理列表中的字节数据
                    final_value = list()
                    for list_item in value:
                        if isinstance(list_item, bytes):
                            final_value.append(self._bytes_save(list_item, False))  # 处理列表中的字节项
                        else:
                            final_value.append(list_item)
                    final_value = json.dumps(final_value)  # 转换为JSON字符串格式
                else:
                    # 处理其他类型的值（数字、布尔值、字典等）
                    if value == tmp and isinstance(value, str):
                        final_value = '"'+value+'"'  # 为未替换的原始表达式添加引号
                    else:
                        final_value = json.dumps(value)  # 转换为标准JSON格式
                # 将处理后的值逐字符压入解析栈
                for s in final_value:
                    self.stack.append(s)
                    top += 1
        # 将栈中的字符连接并解析为JSON对象
        res = json.loads(reduce(lambda x, y: x + y, self.stack))

        # 处理字节数据的还原（将占位符替换为实际的字节数据）
        if len(self.bytes_map) > 0:
            pattern = r'#\{(bytes_\w+_\d+?)\}'  # 字节数据占位符的正则模式
            if isinstance(res, str):
                # 如果结果是字符串，直接检查并还原字节数据
                bytes_value = self._bytes_slove(res, pattern)       # 此处 self._bytes_slove(res, pattern) 返回的是文件
                if bytes_value is not None:
                    res = bytes_value  # 替换为原始字节数据
            elif isinstance(res, dict) or isinstance(res, list):
                # 如果结果是字典或列表，递归处理所有嵌套的字符串值
                for i, j in zip(jsonpath(res, '$..'), jsonpath(res, '$..', result_type='PATH')):    # zip（）：将多个可迭代对象打包成一个元组的迭代器如：[(),(),()]
                    if isinstance(i, str):
                        bytes_value = self._bytes_slove(i, pattern)  # 检查是否为字节占位符
                        if bytes_value is not None:
                            # 使用JSONPath表达式更新嵌套结构中的字节数据
                            expression = self.parser.parse(j)
                            expression.update(res, bytes_value)
        return res  # 返回最终渲染结果

    def _bytes_save(self, value, flag):
        """
            保存字节数据并生成占位符
            
            将字节数据存储到映射表中，并生成唯一的占位符用于后续还原。
            这是处理二进制数据的关键方法，避免在JSON序列化过程中丢失字节数据。
            
            Args:
                value (bytes): 要保存的字节数据，如图片、文件等二进制内容
                flag (bool): 是否需要JSON转义，用于处理字符串上下文中的占位符
            
            Returns:
                str: 字节数据的占位符字符串，格式为 #{bytes_hash_timestamp}
            
            功能说明：
                - 使用MD5哈希和时间戳生成唯一键名
                - 将字节数据存储到内部映射表中
                - 生成占位符字符串用于JSON序列化
                - 根据flag参数决定是否进行JSON转义
            
            Note:
                占位符格式: #{bytes_<md5_hash>_<timestamp_ns>}
                映射表用于在渲染完成后还原原始字节数据
            
            Example:
                >>> placeholder = template._bytes_save(b'\x89PNG...', False)
                >>> # 返回: "#{bytes_abc123_1234567890123456789}"
        """
        # 生成唯一的字节数据键名（使用MD5哈希值和纳秒级时间戳确保全局唯一性）
        bytes_map_key = 'bytes_{}_{}'.format(md5(value).hexdigest(), int(time.time() * 1000000000))
        # 将字节数据存储到映射表中，键为生成的唯一标识，值为原始字节数据
        self.bytes_map[bytes_map_key] = value
        # 生成占位符字符串，格式为 #{key}，用于在JSON序列化中标记字节数据位置
        change_value = '#{%s}' % bytes_map_key
        if flag:
            # 需要JSON转义的情况（在字符串上下文中，需要将占位符作为JSON字符串处理）
            final_value = json.dumps(change_value)
        else:
            # 不需要转义的情况（直接作为JSON值使用）
            final_value = change_value
        return final_value

    def _bytes_slove(self, s, pattern):
        """
            解析字符串中的字节数据占位符
            
            根据正则模式查找字符串中的字节数据占位符，并从映射表中还原原始字节数据。
            这是字节数据处理的逆向操作，将之前保存的占位符替换为实际的字节内容。
            
            Args:
                s (str): 包含占位符的字符串，格式如 "#{bytes_hash_timestamp}"
                pattern (str): 用于匹配占位符的正则表达式，用于匹配字节数据标识符
            
            Returns:
                bytes or None: 还原的字节数据，如果字符串不是字节占位符则返回None
            
            功能说明：
                - 使用正则表达式匹配字节数据占位符
                - 从映射表中查找对应的原始字节数据
                - 只处理完全匹配占位符格式的字符串
                - 非占位符字符串返回None，保持原值不变
            
            Note:
                - 只有当整个字符串完全匹配占位符格式时才进行还原
                - 部分匹配或包含其他内容的字符串不会被处理
                - 映射表中必须存在对应的键值对
            
            Example:
                >>> bytes_data = template._bytes_slove("#{bytes_abc123_1234567890123456789}", pattern)
                >>> # 返回: b'\x89PNG...' 或 None
        """
        search_result = re.search(pattern, s)  # 使用正则表达式搜索字节占位符模式
        if search_result is not None:
            # 提取占位符中的键名（去掉#{和}部分，获取bytes_hash_timestamp格式的键）
            expr = search_result.group(1)
            # 从映射表中获取对应的原始字节数据并返回
            return self.bytes_map[expr]

    def replace_param(self, param):
        """
            替换参数中的特殊引用
            
            处理函数参数中的特殊引用，包括请求数据引用、字节数据引用等。
            支持#{_request_xxx}格式的请求数据引用和JSONPath语法。这是模板引擎
            处理特殊引用的核心方法，用于在函数调用时动态获取请求上下文数据。
            
            Args:
                param (str): 待处理的参数字符串，可能包含特殊引用语法：
                    - #{_request_url}: 引用完整的请求URL
                    - #{_request_path}: 引用请求路径部分
                    - #{_request_header}: 引用完整的请求头字典
                    - #{_request_header.key}: 引用特定的请求头字段
                    - #{_request_body}: 引用完整的请求体
                    - #{_request_body.field}: 引用请求体中的特定字段
                    - #{_request_query}: 引用查询参数字典
                    - #{_request_query.key}: 引用特定的查询参数
                    - #{bytes_xxx}: 引用字节数据映射表中的数据
            
            Returns:
                处理后的参数值，类型根据引用内容而定：
                    - 字符串: URL、路径等文本数据
                    - 字典: 请求头、请求体等结构化数据
                    - bytes: 字节数据映射表中的二进制数据
                    - 原始值: 如果不匹配任何特殊引用格式
            
            功能说明：
                - 使用正则表达式匹配#{...}格式的特殊引用
                - 支持请求数据的各种属性访问
                - 支持JSONPath语法进行深层数据提取
                - 支持字节数据的引用和还原
                - 提供请求上下文信息给函数调用
            
            支持的引用类型：
                1. 请求URL相关:
                - _request_url: 完整URL
                - _request_path: 路径部分
                2. 请求头相关:
                - _request_header: 完整头部字典
                - _request_header.key: 特定头部字段
                3. 请求体相关:
                - _request_body: 完整请求体
                - _request_body.field: 特定字段（支持JSONPath）
                4. 查询参数相关:
                - _request_query: 完整查询参数字典
                - _request_query.key: 特定查询参数
                5. 字节数据相关:
                - bytes_xxx: 字节数据映射表引用
            
            Example:
                >>> # 引用请求URL
                >>> template.replace_param("#{_request_url}")
                >>> # 返回: "http://api.test.com/users"
                
                >>> # 引用特定请求头
                >>> template.replace_param("#{_request_header.Content-Type}")
                >>> # 返回: "application/json"
                
                >>> # 引用请求体中的字段
                >>> template.replace_param("#{_request_body.user.name}")
                >>> # 返回: "张三"
                
                >>> # 引用查询参数
                >>> template.replace_param("#{_request_query.page}")
                >>> # 返回: "1"
                
                >>> # 引用字节数据
                >>> template.replace_param("#{bytes_abc123_1234567890}")
                >>> # 返回: b'\x89PNG...' (原始字节数据)
        """
        param = param.strip()  # 去除参数字符串的首尾空白字符
        # 查找特殊引用模式，匹配#{...}格式的特殊引用语法
        search_result = re.search(r'#\{(.*?)\}', param)
        if search_result is not None:
            expr = search_result.group(1).strip()  # 提取大括号内的引用内容并去除空白
            # 处理请求URL引用（完整的请求URL）
            if expr.lower() == '_request_url':
                return self.request_url
            # 处理请求路径引用（URL中的路径部分，不包含域名和查询参数）
            elif expr.lower() == '_request_path':
                return self.request_path
            # 处理请求头引用（返回完整的请求头字典）
            elif expr.lower() == '_request_header':
                return self.request_headers
            # 处理请求体引用（返回完整的请求体）
            elif expr.lower() == '_request_body':
                return self.request_body
            # 处理查询参数引用（返回完整的查询参数字典）
            elif expr.lower() == '_request_query':
                return self.request_query
            # 处理字节数据引用（从字节映射表中获取原始字节数据）
            elif expr.startswith('bytes_'):
                return self.bytes_map[expr]
            else:
                # 支持从请求头和查询参数中取单个数据，以及复杂的JSONPath提取
                if expr.lower().startswith("_request_header."):
                    data = self.request_headers  # 设置数据源为请求头字典
                    expr = '$.' + expr[16:]  # 转换为JSONPath格式，去掉"_request_header."前缀
                elif expr.lower().startswith("_request_query."):
                    data = self.request_query  # 设置数据源为查询参数字典
                    expr = '$.' + expr[15:]  # 转换为JSONPath格式，去掉"_request_query."前缀
                else:
                    # 默认从请求体中提取数据
                    data = self.request_body  # 设置数据源为请求体
                    if expr.lower().startswith("_request_body."):
                        expr = '$.' + expr[14:]  # 转换为JSONPath格式，去掉"_request_body."前缀
                    elif not expr.startswith('$'):
                        expr = '$.' + expr  # 添加JSONPath根标识符$
                try:
                    # 使用JSONPath提取数据，支持复杂的嵌套结构访问
                    return extract_by_jsonpath(data, expr)
                except:
                    # 提取失败时返回原参数，避免程序崩溃
                    return param
        else:
            # 没有找到特殊引用格式，返回原参数不做任何处理
            return param

    def split_key(self, key: str):
        """
            分离变量名和JSONPath表达式
            
            将形如"variable.path[0].field"的键分离为变量名和JSONPath表达式。
            这是模板引擎处理复杂数据结构访问的核心方法，支持嵌套对象和数组的访问。
            
            Args:
                key (str): 待分离的键字符串，支持以下格式：
                    - 简单变量: "username"
                    - 对象属性: "user.name"
                    - 嵌套属性: "user.profile.email"
                    - 数组索引: "users[0]"
                    - 复合访问: "users[0].profile.name"
                    - 函数调用: "@function_name(args)"
            
            Returns:
                tuple: (变量名, JSONPath表达式) 的元组
                    - 变量名: 字符串，表示根变量名
                    - JSONPath表达式: 字符串或None，用于提取嵌套数据
            
            功能说明：
                - 识别并分离根变量名和访问路径
                - 将点号分隔的路径转换为JSONPath格式
                - 处理数组索引语法 [index]
                - 支持函数调用的识别（以函数前缀开头）
                - 自动添加JSONPath根标识符 '$'
            
            支持的语法：
                - 点号访问: user.name → ("user", "$.name")
                - 数组索引: items[0] → ("items", "$[0]")
                - 混合语法: data.items[0].name → ("data", "$.items[0].name")
                - 函数调用: @func() → ("@func()", None)
            
            Example:
                >>> template.split_key("user.profile[0].name")
                >>> # 返回: ("user", "$.profile[0].name")
                
                >>> template.split_key("items[2]")
                >>> # 返回: ("items", "$[2]")
                
                >>> template.split_key("@random_int(1,100)")
                >>> # 返回: ("@random_int(1,100)", None)
        """
        # 如果是函数调用（以函数前缀开头），直接返回，不进行分离
        if key.startswith(self.function_prefix):
            return key, None
        
        # 按点号分割键，分离变量名和属性路径
        key_list = key.split(".")
        key = key_list[0]  # 第一部分是根变量名
        json_path = None
        
        # 如果有多个部分，说明存在嵌套属性访问，构建JSONPath表达式
        if len(key_list) > 1:
            json_path = reduce(lambda x, y: x + '.' + y, key_list[1:])  # 连接剩余部分作为属性路径
        
        # 处理数组索引语法 variable[index]（如users[0]或data[1].name）
        if key.endswith(']') and '[' in key:
            keys = key.split("[")  # 按左括号分割
            key = keys[0]  # 变量名部分（括号前的部分）
            # 构建数组索引的JSONPath表达式
            if json_path is None:
                json_path = '[' + keys[-1]  # 只有数组索引，如[0]
            else:
                json_path = '[' + keys[-1] + "." + json_path  # 数组索引+属性路径，如[0].name
        
        # 为JSONPath添加根标识符$，形成标准的JSONPath表达式
        if json_path is not None:
            json_path = "$." + json_path
        
        return key, json_path  # 返回分离后的变量名和JSONPath表达式

    def split_func(self, statement: str, flag: 'str' = '@'):
        """
            解析函数调用语句
            
            使用正则表达式解析函数调用语句，提取函数名和参数列表。
            支持类型转换和复杂参数处理，包括字典、列表等复合类型。
            这是模板引擎处理函数调用的核心方法，负责将字符串格式的函数调用
            转换为可执行的函数名和参数列表。
            
            Args:
                statement (str): 函数调用语句，格式如"@function_name(arg1,arg2)"
                            支持的参数类型：
                            - 字符串："string_value" 或 'string_value'
                            - 数字：123, 123.45
                            - 布尔值：true, false
                            - 列表：[item1, item2, ...]
                            - 字典：{"key": "value", ...}
                            - 特殊引用：#{_request_body.field}
                flag (str): 函数前缀标识符，默认为'@'，用于识别函数调用语句
            
            Returns:
                list: [函数名, 参数1, 参数2, ...] 的列表
                    - 第一个元素是函数名（字符串）
                    - 后续元素是转换后的参数，类型根据原始参数而定
            
            Raises:
                SplitFunctionError: 当函数格式错误或参数类型转换失败时抛出，
                                包含详细的错误信息用于调试
            
            功能说明：
                1. 正则表达式匹配：使用正则模式识别函数名和参数部分
                2. 参数分割处理：按逗号分割参数字符串，处理特殊引用
                3. 类型转换：根据函数定义的参数类型进行自动转换
                4. 复合类型处理：通过concat方法处理字典和列表参数
                5. 错误处理：提供详细的错误信息和异常处理
            
            支持的参数类型转换：
                - str: 字符串类型，自动去除引号
                - int: 整数类型，字符串转整数
                - float: 浮点数类型，字符串转浮点数
                - bool: 布尔类型，"false"转False，其他转True
                - dict: 字典类型，通过concat方法连接分割的部分
                - list: 列表类型，通过concat方法连接分割的部分
                - bytes: 字节类型，保持原始字符串
                - None: 任意类型，不进行转换
            
            Example:
                >>> template.split_func("@random_int(1,100)", "@")
                >>> # 返回: ["random_int", 1, 100]
                
                >>> template.split_func("@format('Hello {}', #{_request_body.name})", "@")
                >>> # 返回: ["format", "Hello {}", "张三"]  # 假设请求体中name为"张三"
                
                >>> template.split_func("@create_user({'name': 'test', 'age': 25})", "@")
                >>> # 返回: ["create_user", {"name": "test", "age": 25}]
        """
        # 构建函数匹配的正则表达式，匹配函数名和可选的参数部分
        # 模式说明：
        # - flag: 函数前缀（如@）
        # - ([_a-zA-Z][_a-zA-Z0-9]*): 捕获组1，匹配函数名（以字母或下划线开头，后跟字母数字下划线）
        # - (\(.*?\))?: 捕获组2，可选的参数部分（括号及其内容，非贪婪匹配）
        pattern = flag + r'([_a-zA-Z][_a-zA-Z0-9]*)(\(.*?\))?'
        m = re.match(pattern, statement)  # 使用正则表达式匹配整个语句
        result = list()  # 初始化结果列表，第一个元素是函数名，后续是参数
        
        if m is not None:
            name, _ = m.groups()  # 提取函数名（忽略参数部分的匹配结果）
            args = statement.replace(flag+name, "")  # 从完整语句中移除前缀和函数名，得到参数部分
            result.append(name)  # 将函数名作为结果列表的第一个元素
            
            # 处理函数参数部分
            if args is not None and args != '()':
                # 分割参数字符串并处理特殊引用
                # 1. args[1:-1]: 去除首尾的括号
                # 2. split(','): 按逗号分割参数
                # 3. map(self.replace_param, ...): 处理每个参数中的特殊引用（如#{_request_body.field}）
                # 4. [str(_) for _ in ...]: 将所有参数转换为字符串格式
                argList = [str(_) for _ in map(self.replace_param, args[1:-1].split(','))]
                argList_length = len(argList)  # 记录参数个数，用于后续处理
                
                # 检查是否有有效参数（排除空参数的情况）
                if not (argList_length == 1 and len(argList[0]) == 0):
                    # 如果函数没有在函数库中定义参数类型，直接添加所有参数（保持字符串格式）
                    if name not in self.func_lib.func_param:
                        for i in range(argList_length):
                            result.append(argList[i])  # 不进行类型转换，保持原始字符串格式
                    else:
                        # 根据函数库中定义的参数类型进行精确的类型转换
                        type_list = self.func_lib.func_param[name]  # 获取函数的参数类型定义列表
                        j = 0  # 当前处理的参数索引
                        for i in range(len(type_list)):
                            if j >= argList_length:  # 如果参数已处理完毕，退出循环
                                break
                            # 根据预定义的参数类型进行相应的转换
                            if type_list[i] is str:
                                # 字符串类型：去除参数两端的引号
                                result.append(quotation_marks(argList[j]))
                                j += 1
                            elif type_list[i] is int:
                                # 整数类型：将字符串转换为整数
                                result.append(int(argList[j]))
                                j += 1
                            elif type_list[i] is float:
                                # 浮点数类型：将字符串转换为浮点数
                                result.append(float(argList[j]))
                                j += 1
                            elif type_list[i] is bool:
                                # 布尔类型："false"(不区分大小写)转为False，其他转为True
                                result.append(False if argList[j].lower() == 'false' else True)
                                j += 1
                            elif type_list[i] is dict:
                                # 字典类型：使用concat方法连接被逗号分割的字典参数
                                j, r = self.concat(j, argList, '}')
                                result.append(r)
                            elif type_list[i] is list:
                                # 列表类型：使用concat方法连接被逗号分割的列表参数
                                j, r = self.concat(j, argList, ']')
                                result.append(r)
                            elif type_list[i] is bytes:
                                # 字节类型：保持原始字符串格式，不进行转换
                                result.append(argList[j])
                                j += 1
                            elif type_list[i] is None:
                                # 任意类型：不进行类型转换，保持原始格式
                                result.append(argList[j])
                                j += 1
                            else:
                                # 不支持的参数类型，抛出异常
                                raise SplitFunctionError('函数{}第{}个参数类型错误: {}'.format(name, i + 1, type_list[i]))
            return result  # 返回包含函数名和转换后参数的列表
        else:
            # 正则表达式匹配失败，说明函数调用语法不正确
            raise SplitFunctionError('函数语法错误: {}'.format(statement))

    @staticmethod
    def concat(start: int, arg_list: list, terminal_char: str):
        """
            连接参数列表中的复合类型参数
            
            用于处理函数参数中的字典、列表等复合类型。当参数被逗号分割后，
            需要重新组合成完整的复合类型对象。这是模板引擎处理复合参数的
            核心方法，解决了逗号分隔符与复合类型内部逗号冲突的问题。
            
            Args:
                start (int): 开始位置索引，指示从参数列表的哪个位置开始连接
                arg_list (list): 参数列表，包含被逗号分割的参数字符串片段
                terminal_char (str): 终止字符，用于识别复合类型的结束位置：
                                - '}' 表示字典类型的结束
                                - ']' 表示列表类型的结束
            
            Returns:
                tuple: (下一个位置索引, 解析后的复合对象)
                    - 下一个位置索引 (int): 处理完成后的参数索引，指向下一个待处理参数
                    - 解析后的复合对象 (dict/list/str): 连接并解析后的对象
            
            功能说明:
                1. 逐个检查参数片段，查找包含终止字符的位置
                2. 将从开始位置到终止位置的所有片段用逗号连接
                3. 尝试多种解析策略：直接eval、JSON解析等
                4. 处理解析失败的情况，提供容错机制
                5. 支持嵌套的复合类型结构
            
            解析策略:
                1. 首先尝试使用quotation_marks处理引号后直接eval解析
                2. 如果失败，尝试将连接字符串作为JSON字符串解析
                3. 如果仍然失败，继续查找下一个可能的终止字符
                4. 最后返回连接后的字符串作为备选方案
            
            使用场景:
                - 函数参数包含字典：@func({"key1": "value1", "key2": "value2"})
                - 函数参数包含列表：@func(["item1", "item2", "item3"])
                - 嵌套复合类型：@func({"list": [1, 2, 3], "dict": {"nested": true}})
            
            Example:
                >>> Template.concat(0, ['{"key"', '"value"}'], '}')
                >>> # 返回: (2, {"key": "value"})
                >>> 
                >>> Template.concat(1, ['start', '["item1"', '"item2"]', 'end'], ']')
                >>> # 返回: (3, ["item1", "item2"])
        """
        end = start  # 初始化结束位置为开始位置
        length = len(arg_list)  # 获取参数列表的总长度
        
        # 从开始位置逐个检查参数，查找包含终止字符的参数位置
        for i in range(start, length):
            if terminal_char in arg_list[i]:  # 找到包含终止字符的参数
                end = i  # 记录终止位置
                # 连接从开始位置到终止位置的所有参数片段
                # 使用reduce函数将参数列表片段用逗号连接成完整字符串
                s = reduce(lambda x, y: x + ',' + y, arg_list[start:end + 1])
                try:
                    # 第一种解析策略：使用quotation_marks处理引号后直接eval解析
                    # quotation_marks函数用于处理字符串中的引号格式
                    return end + 1, eval(quotation_marks(s))
                except:
                    try:
                        # 第二种解析策略：将连接字符串包装为JSON字符串后解析
                        # 这种方式适用于某些特殊的字符串格式
                        s = '"'+s+'"'  # 在字符串两端添加引号
                        return end + 1, eval(json.loads(s))  # 先JSON解析再eval
                    except:
                        # 两种解析策略都失败，继续查找下一个可能的终止字符
                        # 这种情况可能出现在嵌套结构或特殊格式中
                        continue
        else:
            # 遍历完所有参数都没有找到有效的终止字符
            # 将所有剩余参数连接成字符串作为备选方案
            s = reduce(lambda x, y: x + ',' + y, arg_list[start:end + 1])
            return end + 1, s  # 返回连接后的字符串，而不是解析后的对象


class SplitFunctionError(Exception):
    """
        函数解析错误异常类
        
        当模板引擎在解析函数调用语句时遇到语法错误、参数类型错误或其他解析问题时抛出此异常。
        这是模板引擎专用的异常类，用于标识函数解析过程中的各种错误情况。
        
        继承自Python内置的Exception类，提供了函数解析过程中的错误信息和上下文。
        通过抛出此异常，可以帮助开发者快速定位模板中函数调用的问题。
        
        错误类型分类:
            1. 语法错误：
            - 函数调用格式不正确（缺少括号、引号不匹配等）
            - 函数名不符合Python标识符规范
            - 参数列表格式错误
            
            2. 参数错误：
            - 参数类型转换失败（如将字符串转换为数字时格式错误）
            - 参数数量与函数定义不匹配
            - 复合类型参数（字典、列表）解析失败
            
            3. 引用错误：
            - 特殊引用格式错误（如#{_request_body.field}格式不正确）
            - 引用的数据源不存在或无法访问
            
            4. 函数库错误：
            - 调用的函数在函数库中不存在
            - 函数参数类型定义与实际调用不匹配
        
        异常处理建议:
            - 在模板渲染过程中捕获此异常，提供友好的错误提示
            - 记录详细的错误信息，包括出错的函数调用语句和上下文
            - 在开发阶段，可以通过此异常快速定位模板语法问题
        
        使用场景:
            - 函数调用语法不正确：@func_name(invalid syntax)
            - 函数参数类型转换失败：@add("abc", 123) # "abc"无法转换为数字
            - 函数名不符合规范：@123invalid() # 函数名不能以数字开头
            - 参数数量不匹配：@add(1) # add函数需要两个参数
            - 复合类型参数解析失败：@func({"key": value}) # value未定义
        
        Attributes:
            继承自Exception的所有属性，包括args、__cause__、__context__等
        
        Example:
            >>> # 语法错误示例
            >>> raise SplitFunctionError("函数语法错误: @invalid_function_call")
            >>> 
            >>> # 参数类型错误示例
            >>> raise SplitFunctionError("参数类型转换失败: 无法将'abc'转换为int类型")
            >>> 
            >>> # 复合参数解析错误示例
            >>> raise SplitFunctionError("复合参数解析失败: {\"key\": undefined_value}")
            >>> 
            >>> # 在模板渲染中的使用
            >>> try:
            ...     template.render()
            >>> except SplitFunctionError as e:
            ...     print(f"模板函数解析错误: {e}")
    """
