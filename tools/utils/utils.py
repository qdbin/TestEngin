# -*- coding: utf-8 -*-
"""
    通用工具函数模块

    提供数据提取、URL处理、代理配置、数据类型转换等常用工具函数。
    主要用于自动化测试平台中的数据处理和参数解析。

    Author: LiuMa Team
    Date: 2024
"""

import json  # JSON数据处理
import re  # 正则表达式处理
from urllib.parse import quote  # URL编码
import jsonpath  # JSONPath表达式解析
import copy  # 深拷贝操作


def extract_by_jsonpath(data: (dict, list, str), expression: str):
    """
        使用JSONPath表达式从JSON数据中提取值
        
        支持从字典或列表类型的数据中，使用JSONPath表达式提取指定的值。
        如果匹配到多个值则返回列表，单个值则直接返回该值。
        
        Args:
            data (dict|list|str): 要提取数据的源对象，必须是字典或列表类型
            expression (str): JSONPath表达式，如'$.user.name'或'$..id'
        
        Returns:
            any: 提取到的值，单个值直接返回，多个值返回列表
        
        Raises:
            ExtractValueError: 当数据类型不支持或表达式错误时抛出
        
        Example:
            >>> data = {'user': {'name': 'Alice', 'age': 25}}
            >>> extract_by_jsonpath(data, '$.user.name')
            'Alice'
            >>> extract_by_jsonpath([{'id': 1}, {'id': 2}], '$..id')
            [1, 2]
    """
    # 检查数据类型是否支持JSONPath提取
    if not isinstance(data, dict) and not isinstance(data, list):
        raise ExtractValueError('被提取的值不是json, 不支持jsonpath')
    
    # 使用JSONPath表达式提取数据
    value = jsonpath.jsonpath(data, expression)
    if value:
        # 如果只有一个值则直接返回，多个值返回列表
        return value[0] if len(value) == 1 else value
    else:
        raise ExtractValueError('jsonpath表达式错误: {}'.format(expression))


def extract_by_regex(data: (dict, str), pattern: str):
    """
        使用正则表达式从数据中提取值
        
        支持从字符串或字典数据中使用正则表达式提取匹配的内容。
        字典类型会先转换为JSON字符串再进行匹配。
        
        Args:
            data (dict|str): 要提取数据的源对象，支持字典或字符串类型
            pattern (str): 正则表达式模式
        
        Returns:
            any: 匹配到的值，单个匹配直接返回，多个匹配返回列表
        
        Raises:
            ExtractValueError: 当正则表达式匹配失败时抛出
        
        Example:
            >>> extract_by_regex('Hello World', r'Hello (\w+)')
            'World'
            >>> extract_by_regex({'msg': 'Error: 404'}, r'Error: (\d+)')
            '404'
    """
    # 处理不同数据类型，统一转换为字符串
    if isinstance(data, dict):
        # 字典类型转换为JSON字符串，保持中文字符
        content = json.dumps(data, ensure_ascii=False)
    else:
        content = data
    
    # 使用正则表达式查找匹配项
    result = re.findall(pattern, content)
    if len(result) > 0:
        # 如果只有一个匹配则直接返回，多个匹配返回列表
        return result[0] if len(result) == 1 else result
    else:
        raise ExtractValueError("正则表达式匹配失败: {}".format(pattern))


def quotation_marks(s):
    """
        移除字符串两端的引号（包括各种类型的引号）
        
        支持移除单引号、双引号、中文引号以及转义引号。
        如果字符串两端没有引号则原样返回。
        
        Args:
            s (str): 需要处理的字符串
        
        Returns:
            str: 移除引号后的字符串
        
        Example:
            >>> quotation_marks('"hello"')
            'hello'
            >>> quotation_marks("'world'")
            'world'
            >>> quotation_marks('test')
            'test'
    """
    # 检查字符串开头的引号类型
    if s[0] in ["'", '"', b'\xe2\x80\x98'.decode('utf-8'), b'\xe2\x80\x99'.decode('utf-8'),
                b'\xe2\x80\x9c'.decode('utf-8'), b'\xe2\x80\x9d'.decode('utf-8')]:
        # 单个引号字符
        before = 1
    elif s[0:2] in ["\\'", '\\"']:
        # 转义引号字符
        before = 2
    else:
        # 没有引号，直接返回原字符串
        return s
    
    # 检查字符串结尾的引号类型，先判断转义的，再判断单个引号
    if s[-2:] in ["\\'", '\\"']:
        # 转义引号字符
        after = -2
    elif s[-1] in ["'", '"', b'\xe2\x80\x98'.decode('utf-8'), b'\xe2\x80\x99'.decode('utf-8'),
                   b'\xe2\x80\x9c'.decode('utf-8'), b'\xe2\x80\x9d'.decode('utf-8')]:
        # 单个引号字符
        after = -1
    else:
        # 结尾没有引号，直接返回原字符串
        return s
    
    # 返回移除引号后的字符串
    return s[before:after]


def url_join(host: str, path: str):
    """
        拼接主机地址和路径为完整的URL
        
        智能处理主机地址和路径的斜杠，确保拼接后的URL格式正确。
        自动处理主机地址末尾和路径开头的斜杠重复问题。
        
        Args:
            host (str): 主机地址，如'http://example.com'或'http://example.com/'
            path (str): 路径部分，如'/api/users'或'api/users'
        
        Returns:
            str: 拼接后的完整URL
        
        Example:
            >>> url_join('http://example.com', '/api/users')
            'http://example.com/api/users'
            >>> url_join('http://example.com/', 'api/users')
            'http://example.com/api/users'
            >>> url_join('', '/path')
            'path'
    """
    # 处理主机地址，确保以斜杠结尾（空值时为空字符串）
    url = "" if host is None or host == "" else (host if host.endswith('/') else host + '/')
    # 处理路径部分，移除开头的斜杠避免重复
    api = "" if path is None or path == "" else (path[1:] if path.startswith('/') else path)
    return url + api


def proxies_join(proxies: dict):
    """
    构建代理配置字典
    
    根据提供的代理信息构建符合requests库要求的代理配置。
    支持带认证和不带认证的代理配置，自动处理URL编码和格式验证。
    
    Args:
        proxies (dict): 代理配置字典，包含以下键：
            - url (str): 代理服务器地址
            - username (str, optional): 代理用户名
            - password (str, optional): 代理密码
    
    Returns:
        dict: 格式化的代理配置字典，键为协议名，值为代理URL
    
    Raises:
        ProxiesError: 当代理配置不完整或格式错误时抛出
    
    Example:
        >>> proxies_join({'url': 'http://proxy.com:8080'})
        {'http': 'http://proxy.com:8080'}
        >>> proxies_join({
        ...     'url': 'http://proxy.com:8080',
        ...     'username': 'user',
        ...     'password': 'pass'
        ... })
        {'http': 'http://user:pass@proxy.com:8080'}
    """
    # 验证代理URL是否存在
    if 'url' not in proxies or proxies['url'] is None or len(proxies['url']) == 0:
        raise ProxiesError("未设置代理网址")
    
    # 确保URL包含协议前缀
    if not proxies['url'].startswith('http'):
        proxies['url'] = 'http://' + proxies['url']
    
    # 处理用户名，进行URL编码
    if 'username' not in proxies or proxies['username'] is None or len(proxies['username']) == 0:
        proxies['username'] = None
    else:
        proxies['username'] = quote(proxies['username'], safe='')
    
    # 处理密码，进行URL编码
    if 'password' not in proxies or proxies['password'] is None or len(proxies['password']) == 0:
        proxies['password'] = None
    else:
        proxies['password'] = quote(proxies['password'], safe='')
    
    # 提取协议类型
    scheme = proxies['url'].split(':')[0]
    
    # 根据认证信息构建最终的代理URL
    if proxies['username'] is not None and proxies['password'] is not None:
        # 带认证的代理配置
        pre, suf = proxies['url'].split('//', maxsplit=1)
        url = '{}//{}:{}@{}'.format(pre, proxies['username'], proxies['password'], suf)
        return {scheme: url}
    elif proxies['username'] is None and proxies['password'] is None:
        # 不带认证的代理配置
        return {scheme: proxies['url']}
    else:
        # 认证信息不完整
        raise ProxiesError("未设置代理账号或密码")


def extract(name: str, data: (dict, list, str), expression: str):
    """
    通用数据提取函数
    
    根据指定的提取方式（jsonpath或regex）从数据中提取值。
    这是一个统一的入口函数，内部调用具体的提取函数。
    
    Args:
        name (str): 提取方式名称，支持'jsonpath'和'regular'
        data (dict|list|str): 要提取数据的源对象
        expression (str): 提取表达式（JSONPath表达式或正则表达式）
    
    Returns:
        any: 提取到的值
    
    Raises:
        ExtractValueError: 当提取方式未定义或提取失败时抛出
    
    Example:
        >>> extract('jsonpath', {'user': {'name': 'Alice'}}, '$.user.name')
        'Alice'
        >>> extract('regular', 'Error: 404', r'Error: (\d+)')
        '404'
    """
    if name == 'jsonpath':
        # 使用JSONPath方式提取
        return extract_by_jsonpath(data, expression)
    elif name == 'regular':
        # 使用正则表达式方式提取
        return extract_by_regex(data, expression)
    else:
        # 未支持的提取方式
        raise ExtractValueError("未定义提取函数: {}".format(name))


def get_case_message(data):
    """
    获取测试用例消息数据
    
    智能处理不同类型的输入数据，统一转换为字典格式。
    支持字典、JSON字符串和文件路径三种输入方式。
    
    Args:
        data (dict|str): 测试用例数据，可以是：
            - dict: 字典对象，直接返回
            - str: JSON字符串或文件路径
    
    Returns:
        dict: 解析后的测试用例数据字典
    
    Raises:
        json.decoder.JSONDecodeError: 当JSON字符串格式错误时抛出
        FileNotFoundError: 当文件路径不存在时抛出
        IOError: 当文件读取失败时抛出
    
    Example:
        >>> get_case_message({'name': 'test'})
        {'name': 'test'}
        >>> get_case_message('{"name": "test"}')
        {'name': 'test'}
        >>> get_case_message('/path/to/test.json')
        {'name': 'test'}  # 文件内容
    """
    if isinstance(data, dict):
        # 已经是字典格式，直接返回
        return data
    else:
        try:
            # 尝试解析为JSON字符串
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            # JSON解析失败，当作文件路径处理
            with open(data, 'rb') as f:
                return json.load(f)


def handle_operation_data(data_type, data_value):
    """
    处理操作数据的类型转换
    
    根据指定的数据类型将字符串值转换为对应的Python数据类型。
    支持JSONObject、JSONArray、Boolean、Int、Float、Number等类型的转换。
    
    Args:
        data_type (str): 数据类型标识，如'JSONObject'、'Boolean'、'Int'等
        data_value (str): 需要转换的字符串值
    
    Returns:
        any: 转换后的值，转换失败时返回原值
    
    Example:
        >>> handle_operation_data('JSONObject', '{"name": "test"}')
        {'name': 'test'}
        >>> handle_operation_data('Boolean', 'true')
        True
        >>> handle_operation_data('Int', '123')
        123
        >>> handle_operation_data('Float', '99.99')
        99.99
        >>> handle_operation_data('Number', '123')
        123
        >>> handle_operation_data('Number', '99.99')
        99.99
    """
    try:
        if data_type == "JSONObject":
            # 转换JSON对象字符串为字典
            data_value = eval(data_value)
        elif data_type == "JSONArray":
            # 转换JSON数组字符串为列表
            data_value = eval(data_value)
        elif data_type == "Boolean":
            # 转换布尔值字符串为布尔类型
            if data_value.lower() == "true":
                data_value = True
            else:
                data_value = False
        elif data_type == "Int":
            # 转换整数字符串为整数类型
            data_value = int(data_value)
        elif data_type == "Float":
            # 转换浮点数字符串为浮点类型
            data_value = float(data_value)
        elif data_type == "Number":
            # 智能转换数字字符串，根据是否包含小数点决定类型
            data_value = float(data_value) if "." in data_value else int(data_value)
        else:
            # 其他类型保持原值
            data_value = data_value
    except:
        # 转换失败时保持原值
        pass
    return data_value


def handle_params_data(params):
    """
    处理参数数据的类型转换
    
    将包含类型信息的参数字典转换为实际的数据类型。
    每个参数项包含type和value字段，根据type字段进行相应的类型转换。
    
    Args:
        params (dict): 参数字典，格式为 {
            'param_name': {
                'type': 'JSONObject|JSONArray|Boolean|Int|Float|String',
                'value': 'string_value'
            }
        }
    
    Returns:
        dict: 转换后的参数字典，键为参数名，值为转换后的实际类型值
    
    Example:
        >>> handle_params_data({
        ...     'user': {'type': 'JSONObject', 'value': '{"name": "Alice"}'},
        ...     'active': {'type': 'Boolean', 'value': 'true'},
        ...     'count': {'type': 'Int', 'value': '10'},
        ...     'price': {'type': 'Float', 'value': '99.99'},
        ...     'title': {'type': 'String', 'value': 'Hello World'}
        ... })
        {
            'user': {'name': 'Alice'},
            'active': True,
            'count': 10,
            'price': 99.99,
            'title': 'Hello World'
        }
    """
    result = {}
    for key, item in params.items():
        data_type = item["type"]
        data_value = item["value"]
        try:
            if data_type == "JSONObject":
                # 转换JSON对象字符串为字典
                data_value = eval(data_value)
            elif data_type == "JSONArray":
                # 转换JSON数组字符串为列表
                data_value = eval(data_value)
            elif data_type == "Boolean":
                # 转换布尔值字符串为布尔类型
                if data_value.lower() == "true":
                    data_value = True
                else:
                    data_value = False
            elif data_type == "Int":
                # 转换整数字符串为整数类型
                data_value = int(data_value)
            elif data_type == "Float":
                # 转换浮点数字符串为浮点类型
                data_value = float(data_value)
            # 其他类型（如String）保持原值
        except:
            # 转换失败时保持原值
            pass
        result[key] = data_value
    return result


def handle_form_data(form):
    """
    处理表单数据和文件数据的类型转换
    
    将表单项列表转换为表单数据字典和文件数据字典。
    支持多种数据类型转换，包括文件上传、JSON对象、基本数据类型等。
    
    Args:
        form (list): 表单项列表，每个项包含name、type、value字段
    
    Returns:
        tuple: (表单数据字典, 文件数据字典)
    
    Example:
        >>> form = [
        ...     {'name': 'username', 'type': 'String', 'value': 'Alice'},
        ...     {'name': 'age', 'type': 'Int', 'value': '25'},
        ...     {'name': 'avatar', 'type': 'File', 'value': 'image.jpg'}
        ... ]
        >>> handle_form_data(form)
        ({'username': 'Alice', 'age': 25}, {'avatar': '{{@loadfile(image.jpg)}}'}) 
    """
    form_data = {}
    form_file = {}
    for item in form:
        try:
            if item["type"] == "File":
                # 文件类型，生成文件加载标记
                form_file[item["name"]] = "{{@loadfile(%s)}}" % item["value"]
            elif item["type"] == "JSONObject":
                # JSON对象类型，使用eval解析
                form_data[item["name"]] = eval(item["value"])
            elif item["type"] == "JSONArray":
                # JSON数组类型，使用eval解析
                form_data[item["name"]] = eval(item["value"])
            elif item["type"] == "Boolean":
                # 布尔类型，转换字符串为布尔值
                if item["value"].lower() == 'true':
                    form_data[item["name"]] = True
                else:
                    form_data[item["name"]] = False
            elif item["type"] == "Int":
                # 整数类型转换
                form_data[item["name"]] = int(item["value"])
            elif item["type"] == "Float":
                # 浮点数类型转换
                form_data[item["name"]] = float(item["value"])
            else:
                # 其他类型保持原值（如String类型）
                form_data[item["name"]] = item["value"]
        except:
            # 转换失败时保持原值
            form_data[item["name"]] = item["value"]
    return form_data, form_file


def handle_files(files):
    """
    处理文件上传数据
    
    将文件信息列表转换为符合requests库要求的文件上传格式。
    每个文件项包含文件名和文件ID，转换为文件加载标记。
    
    Args:
        files (list): 文件信息列表，每个项包含name和id字段
    
    Returns:
        list: 文件上传元组列表，格式为[("file", (文件名, 文件内容标记))]
    
    Example:
        >>> files = [
        ...     {'name': 'document.pdf', 'id': 'file123'},
        ...     {'name': 'image.jpg', 'id': 'file456'}
        ... ]
        >>> handle_files(files)
        [('file', ('document.pdf', '{{@loadfile(file123)}}')), 
         ('file', ('image.jpg', '{{@loadfile(file456)}}'))]
    """
    body_files = []
    for item in files:
        # 获取文件名
        file_name = item["name"]
        # 生成文件加载标记，使用文件ID
        file_value = "{{@loadfile(%s)}}" % item["id"]
        # 添加到文件列表，格式为(字段名, (文件名, 文件内容))
        body_files.append(("file", (file_name, file_value)))
    return body_files


def json_to_path(data):
    """
    将JSON数据转换为JSONPath格式的路径-值对字典
    
    使用广度优先搜索遍历JSON数据结构，将嵌套的字典和列表转换为
    扁平化的路径-值对。路径采用JSONPath格式，支持字典键和数组索引。
    
    Args:
        data (dict|list): 要转换的JSON数据，支持字典和列表类型
    
    Returns:
        dict: 扁平化后的路径-值对字典，键为JSONPath格式的路径
    
    Example:
        >>> data = {
        ...     'user': {'name': 'Alice', 'tags': ['admin', 'user']},
        ...     'count': 10
        ... }
        >>> json_to_path(data)
        {
            "$.'user'.'name'": 'Alice',
            "$.'user'.'tags'[0]": 'admin',
            "$.'user'.'tags'[1]": 'user',
            "$.'count'": 10
        }
    """
    # 使用队列进行广度优先遍历，初始路径为JSONPath根路径"$"
    queue = [("$", data)]
    fina = {}
    
    while len(queue) != 0:
        (path, tar) = queue.pop()
        
        # 处理空容器的情况
        if len(tar) == 0:
            fina["%s" % path] = tar
        
        if isinstance(tar, dict):
            # 处理字典类型，遍历所有键值对
            for key, value in tar.items():
                try:
                    # 检查键是否为纯数字，需要加引号处理
                    if key.isdigit():
                        key = "'%s'" % str(key)
                except:
                    # 其他情况也加引号，确保路径格式正确
                    key = "'%s'" % str(key)
                
                if isinstance(value, dict) or isinstance(value, list):
                    # 如果值是容器类型，添加到队列继续处理
                    queue.append(("%s.%s" % (path, key), value))
                else:
                    # 如果是叶子节点，直接添加到结果字典
                    fina["%s.%s" % (path, key)] = value
        else:
            # 处理列表类型，遍历所有元素
            for index, value in enumerate(tar):
                if isinstance(value, dict) or isinstance(value, list):
                    # 如果元素是容器类型，添加到队列继续处理
                    queue.append(("%s[%d]" % (path, index), value))
                else:
                    # 如果是叶子节点，直接添加到结果字典
                    fina["%s[%d]" % (path, index)] = value
    
    return fina


def relate_sort(data, data_from):
    """
    对包含关联引用的数据进行依赖排序
    
    将数据项按照依赖关系进行排序，确保被引用的数据项在引用它的数据项之前。
    支持处理变量引用（#{...}格式）和请求数据引用（_request_*格式）。
    
    Args:
        data (dict): 包含键值对的数据字典，值可能包含引用表达式
        data_from (str): 数据来源标识，用于确定引用类型（'query'、'headers'或其他）
    
    Returns:
        list: 排序后的(key, value)元组列表，按依赖关系排序
    
    Example:
        # 注意：此函数通常通过get_json_relation()调用，接收json_to_path()处理后的扁平化数据
        
        # 原始JSON数据示例
        >>> original_data = {
        ...     'user_name': '#{$.\'login\'.username}',  # 引用了 login.username
        ...     'user_id': '12345',                      # 普通数据，无引用
        ...     'request_data': '#{_request_header}',    # 特殊的请求引用
        ...     'login': {'username': 'admin', 'password': '123456'},  # 被引用的数据
        ...     'token': '#{$.\'login\'.password}_encrypted'  # 引用了 login.password
        ... }
        
        # json_to_path()处理后的扁平化数据（relate_sort的实际输入）
        >>> flattened_data = {
        ...     "$.'user_name'": '#{$.\'login\'.username}',
        ...     "$.'user_id'": '12345',
        ...     "$.'request_data'": '#{_request_header}',
        ...     "$.'login'.'username'": 'admin',
        ...     "$.'login'.'password'": '123456',
        ...     "$.'token'": '#{$.\'login\'.password}_encrypted'
        ... }
        
        >>> relate_sort(flattened_data, 'headers')
        调用结果：
            [
                ("$.'user_id'", '12345'),  # 无依赖项排在前面
                ("$.'login'.'username'", 'admin'),  # 被引用的数据项
                ("$.'login'.'password'", '123456'),
                ("$.'user_name'", '#{$.\'login\'.username}'),  # 引用项排在后面
                ("$.'token'", '#{$.\'login\'.password}_encrypted'),
                ("$.'request_data'", '#{_request_header}')  # 请求引用被移到最后
            ]
        
        # 实际使用场景：通过get_json_relation()函数调用
        >>> get_json_relation(original_data, 'headers')
        # 内部会先调用json_to_path()扁平化数据，再调用relate_sort()排序
        
        # 场景示例：API测试中的请求头依赖
        >>> api_headers = {
        ...     'Authorization': 'Bearer #{$.\'auth_response\'.access_token}',
        ...     'User-Agent': 'TestClient/1.0',
        ...     'Content-Type': 'application/json',
        ...     'auth_response': {'access_token': 'token123', 'expires_in': 3600}
        ... }
        
        # 经过json_to_path()和relate_sort()处理后的结果
        >>> get_json_relation(api_headers, 'headers')
        [
            ("$.'User-Agent'", 'TestClient/1.0'),  # 普通header先处理
            ("$.'Content-Type'", 'application/json'),
            ("$.'auth_response'.'access_token'", 'token123'),  # 被依赖的数据
            ("$.'auth_response'.'expires_in'", 3600),
            ("$.'Authorization'", 'Bearer #{$.\'auth_response\'.access_token}')  # 依赖项最后处理
        ]
    """
    # 分离有关联引用和无关联引用的数据项
    not_relate_list = []  # 无引用的数据项
    relate_list = []      # 有引用的数据项
    
    for key, value in data.items():
        if "#{" in str(value):
            # 包含引用表达式的数据项
            relate_list.append((key, value))
        else:
            # 普通数据项，无依赖关系
            not_relate_list.append((key, value))
    
    # 对有关联的数据项进行依赖排序
    copy_list = copy.deepcopy(relate_list)
    sorted_list = []
    
    # 使用拓扑排序算法处理依赖关系
    for index in range(len(relate_list)):
        for (key, value) in copy_list:
            # 检查当前项是否被其他项依赖
            for (com_key, com_value) in copy_list:
                # 提取JSONPath中的路径部分
                if com_key[0:2] == "$.":
                    json_path = com_key[2:]
                else:
                    json_path = com_key[1:]
                
                # 如果当前项的路径被其他项引用，则存在依赖关系
                if json_path in str(value) and com_key != key:
                    break
            else:
                # 当前项不被其他项依赖，可以优先处理
                sorted_list.append((key, value))
                copy_list.remove((key, value))
                break
    
    # 处理请求数据引用，将其移到最后
    for (key, value) in sorted_list:
        # 根据数据来源确定引用标识
        if data_from == "query":
            sign = "#{_request_query}"
        elif data_from == "headers":
            sign = "#{_request_header}"
        else:
            sign = "#{_request_body}"
        
        # 如果包含请求数据引用，移到列表末尾
        if sign in str(value).lower():
            sorted_list.remove((key, value))
            sorted_list.append((key, value))
            break
    
    # 返回合并后的排序结果：无关联项 + 有关联项（已排序）
    return not_relate_list + sorted_list


def get_json_relation(data: dict, data_from: str):
    """
        Example:
            # 注意：此函数通常通过get_json_relation()调用，接收json_to_path()处理后的扁平化数据
            
            # 原始JSON数据示例
            >>> original_data = {
            ...     'user_name': '#{$.\'login\'.username}',  # 引用了 login.username
            ...     'user_id': '12345',                      # 普通数据，无引用
            ...     'request_data': '#{_request_header}',    # 特殊的请求引用
            ...     'login': {'username': 'admin', 'password': '123456'},  # 被引用的数据
            ...     'token': '#{$.\'login\'.password}_encrypted'  # 引用了 login.password
            ... }
            
            # json_to_path()处理后的扁平化数据（relate_sort的实际输入）
            >>> flattened_data = {
            ...     "$.'user_name'": '#{$.\'login\'.username}',
            ...     "$.'user_id'": '12345',
            ...     "$.'request_data'": '#{_request_header}',
            ...     "$.'login'.'username'": 'admin',
            ...     "$.'login'.'password'": '123456',
            ...     "$.'token'": '#{$.\'login\'.password}_encrypted'
            ... }
            
            >>> relate_sort(flattened_data, 'headers')
            调用结果：
                [
                    ("$.'user_id'", '12345'),  # 无依赖项排在前面
                    ("$.'login'.'username'", 'admin'),  # 被引用的数据项
                    ("$.'login'.'password'", '123456'),
                    ("$.'user_name'", '#{$.\'login\'.username}'),  # 引用项排在后面
                    ("$.'token'", '#{$.\'login\'.password}_encrypted'),
                    ("$.'request_data'", '#{_request_header}')  # 请求引用被移到最后
                ]
            
            # 实际使用场景：通过get_json_relation()函数调用
            >>> get_json_relation(original_data, 'headers')
            # 内部会先调用json_to_path()扁平化数据，再调用relate_sort()排序
            
            # 场景示例：API测试中的请求头依赖
            >>> api_headers = {
            ...     'Authorization': 'Bearer #{$.\'auth_response\'.access_token}',
            ...     'User-Agent': 'TestClient/1.0',
            ...     'Content-Type': 'application/json',
            ...     'auth_response': {'access_token': 'token123', 'expires_in': 3600}
            ... }
            
            # 经过json_to_path()和relate_sort()处理后的结果
            >>> get_json_relation(api_headers, 'headers')
            [
                ("$.'User-Agent'", 'TestClient/1.0'),  # 普通header先处理
                ("$.'Content-Type'", 'application/json'),
                ("$.'auth_response'.'access_token'", 'token123'),  # 被依赖的数据
                ("$.'auth_response'.'expires_in'", 3600),
                ("$.'Authorization'", 'Bearer #{$.\'auth_response\'.access_token}')  # 依赖项最后处理
            ]
    """
    return relate_sort(json_to_path(data), data_from)


class ExtractValueError(Exception):
    """
    数据提取异常类
    
    当使用JSONPath或正则表达式提取数据失败时抛出此异常。
    包括数据类型不支持、表达式格式错误、匹配失败等情况。
    
    继承自Exception，用于标识数据提取过程中的各种错误。
    
    Example:
        >>> raise ExtractValueError('JSONPath表达式错误: $.invalid.path')
        ExtractValueError: JSONPath表达式错误: $.invalid.path
    """
    pass


class ProxiesError(Exception):
    """
    代理配置异常类
    
    当代理服务器配置不正确时抛出此异常。
    包括代理URL缺失、认证信息不完整、格式错误等情况。
    
    继承自Exception，用于标识代理配置过程中的各种错误。
    
    Example:
        >>> raise ProxiesError('未设置代理网址')
        ProxiesError: 未设置代理网址
        >>> raise ProxiesError('未设置代理账号或密码')
        ProxiesError: 未设置代理账号或密码
    """
    pass
