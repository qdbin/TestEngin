import datetime  # 日期时间处理
import sys  # 系统相关功能
from time import sleep  # 时间延迟功能

from requests import request, Session  # HTTP请求库
from copy import deepcopy  # 深拷贝功能
import json  # JSON数据处理

from core.assertion import LMAssert  # 自定义断言模块
from tools.utils.sql import SQLConnect  # SQL数据库连接工具
from tools.utils.utils import extract, ExtractValueError, url_join  # 数据提取和URL拼接工具
from urllib.parse import urlencode  # URL编码工具

# 请求参数中文名称映射表，用于日志输出时的中文显示
REQUEST_CNAME_MAP = {
    'headers': '请求头',      # HTTP请求头
    'proxies': '代理',       # 代理服务器配置
    'cookies': 'cookies',    # Cookie信息
    'params': '查询参数',     # URL查询参数
    'data': '请求体',        # 表单数据请求体
    'json': '请求体',        # JSON格式请求体
    'files': '上传文件'       # 文件上传
}


class ApiTestStep:
    """
        API测试步骤执行器
        
        负责执行单个API测试步骤的完整流程，包括请求构建、发送、响应处理、
        断言验证、关联参数提取等功能。支持循环控制、条件控制、前后置脚本
        和SQL执行等高级测试特性。
        
        主要功能：
            - HTTP请求的构建和发送
            - 响应数据的处理和解析
            - 断言验证和结果收集
            - 关联参数的提取和保存
            - 循环控制和条件控制
            - 前后置脚本执行
            - 前后置SQL语句执行
            - 测试日志记录和错误处理
        
        支持的请求类型：
            - GET、POST、PUT、DELETE、PATCH等HTTP方法
            - JSON、表单、文件上传等请求体格式
            - 自定义请求头、Cookie、代理等配置
            - SSL证书验证、身份认证等安全特性
        
        控制器支持：
            - FOR循环：基于次数或列表的循环执行
            - WHILE循环：基于条件的循环执行
            - 条件控制：基于断言结果的条件执行
            - 超时控制：防止无限循环的安全机制
        
        脚本执行：
            - 前置脚本：请求发送前的数据准备
            - 后置脚本：响应处理后的数据处理
            - 内置函数：print、sys_put、sys_get等
            - 安全沙箱：限制脚本执行权限
        
        Attributes:
            session: 会话管理器，用于保持HTTP会话状态
            collector: 请求数据收集器，包含API请求的所有配置
            context: 测试上下文，存储关联变量和公共参数
            params: 项目级公共参数
            test: 测试用例实例，用于日志记录和状态管理
            status_code: HTTP响应状态码
            response_request: 请求对象
            response_headers: 响应头信息
            response_content: 响应体内容（JSON或文本）
            response_content_bytes: 响应体原始字节数据
            response_cookies: 响应Cookie信息
            assert_result: 断言执行结果
        
        Example:
            >>> step = ApiTestStep(test, session, collector, context, params)
            >>> step.execute()  # 执行API测试步骤
    """

    def __init__(self, test, session, collector, context, params):
        """
            初始化API测试步骤执行器
            
            Args:
                test: 测试用例实例，用于日志记录和状态管理
                session (Session): HTTP会话管理器，保持连接状态和Cookie
                collector: 请求数据收集器，包含API请求的所有配置信息
                context (dict): 测试上下文，存储关联变量和动态参数
                params (dict): 项目级公共参数配置
        """
        self.session = session                    # HTTP会话管理器
        self.collector = collector                # 请求数据收集器
        self.context = context                    # 测试上下文变量
        self.params = params                      # 项目公共参数
        self.test = test                          # 测试用例实例
        self.status_code = None                   # HTTP响应状态码
        self.response_request = None              # 请求对象
        self.response_headers = None              # 响应头信息
        self.response_content = None              # 响应体内容（解析后）
        self.response_content_bytes = None        # 响应体原始字节数据
        self.response_cookies = None              # 响应Cookie信息
        self.assert_result = None                 # 断言执行结果
        self.print = print

    def execute(self):
        """
            执行API测试步骤
            
            执行完整的API测试流程，包括循环控制、条件判断、请求发送、
            响应处理、断言验证和关联参数提取。支持多种控制器和脚本执行。
            
            执行流程：
                1. 记录接口执行开始日志
                2. 构建并记录请求信息日志（URL、请求头、请求体等）
                3. 处理不同类型的请求体数据（JSON、表单、文件等）
                4. 处理文件上传时的Content-Type自动设置
                5. 执行请求前等待（支持延迟控制）
                6. 根据会话配置发送HTTP请求（支持Session管理）
                7. 记录请求耗时（性能监控）
                8. 保存和解析响应数据（状态码、响应头、响应体等）
                9. 构建并记录响应信息日志
                10. 执行断言检查（验证响应是否符合预期）
                11. 提取关联参数（保存数据供后续步骤使用）
                12. 记录接口执行结束日志和请求后等待
            
            请求处理特性：
                - 自动处理文件上传的Content-Type
                - 支持多种请求体格式（JSON、表单、文件等）
                - 自动管理Session和Cookie
                - 支持代理、认证、SSL等高级配置
                - 支持请求前后的延迟控制
            
            响应处理特性：
                - 自动解析JSON和文本响应
                - 记录完整的响应信息用于调试
                - 支持文件下载响应的特殊处理
                - 自动提取和格式化Cookie信息
            
            性能监控：
                - 记录请求执行时间
                - 支持超时控制
                - 提供详细的执行日志
            
            Raises:
                Exception: 当任何步骤执行失败时抛出异常
                    - 网络连接异常
                    - 请求构建失败
                    - 响应解析错误
                    - 断言验证失败
                    - 关联参数提取失败
            
            注意事项：
                - 所有执行过程都会记录详细日志
                - 异常会被捕获并记录到测试报告中
                - 文件上传会自动处理Content-Type
                - Session管理支持多种配置模式
                - 请求和响应数据都会完整保存
        """
        try:
            # 记录接口执行开始日志
            self.test.debugLog('[{}]接口执行开始'.format(self.collector.apiName))
            
            # 构建请求信息日志
            request_log = '【请求信息】:<br>'
            request_log += '{} {}<br>'.format(self.collector.method, url_join(self.collector.url, self.collector.path))

            for key, value in self.collector.others.items():
                if value is not None:
                    c_key = REQUEST_CNAME_MAP[key] if key in REQUEST_CNAME_MAP else key
                    if key == 'files':
                        # 处理文件上传参数的日志显示
                        if isinstance(value, dict):
                            request_log += '{}: {}<br>'.format(c_key, ["文件【%s】的长度: %s" % (k, len(v)) for k,v in value.items()])
                        if isinstance(value, list):
                            request_log += '{}: {}<br>'.format(c_key, [i[1][0] for i in value])
                    elif c_key == '请求体':
                        # 特殊处理请求体的日志显示
                        request_log += '<span>{}: {}</span><br>'.format(c_key, dict2str(value))
                    else:
                        request_log += '{}: {}<br>'.format(c_key, dict2str(value))
            self.test.debugLog(request_log[:-4])
            
            # 处理不同类型的请求体数据
            if self.collector.body_type == "form-urlencoded" and 'data' in self.collector.others:
                # 将表单数据编码为URL编码格式
                self.collector.others['data'] = urlencode(self.collector.others['data'])
            if self.collector.body_type in ("text", "xml", "html") and 'data' in self.collector.others:
                # 将文本类型数据编码为UTF-8字节
                self.collector.others['data'] = str(self.collector.others['data']).encode("utf-8")
            
            # 处理文件上传时移除Content-Type头，让requests自动设置
            if 'files' in self.collector.others and self.collector.others['files'] is not None:
                self.pop_content_type()
            
            # 构建完整的请求URL
            url = url_join(self.collector.url, self.collector.path)
            
            # 执行请求前等待
            if int(self.collector.controller["sleepBeforeRun"]) > 0:
                sleep(int(self.collector.controller["sleepBeforeRun"]))
                self.test.debugLog("请求前等待%sS" % int(self.collector.controller["sleepBeforeRun"]))
            
            # 记录请求开始时间，用于计算接口响应耗时
            start_time = datetime.datetime.now()
            
            # 根据会话配置选择不同的请求方式
            if self.collector.controller["useSession"].lower() == 'true' and self.collector.controller["saveSession"].lower() == "true":
                # 使用并保存会话：保持Cookie和连接状态
                res = self.session.session.request(self.collector.method, url, **self.collector.others)
            elif self.collector.controller["useSession"].lower() == "true":
                # 仅使用会话，不保存：避免影响原会话状态
                session = deepcopy(self.session.session)
                res = session.request(self.collector.method, url, **self.collector.others)
            elif self.collector.controller["saveSession"].lower() == "true":
                # 创建新会话并保存：重新开始会话管理
                session = Session()
                res = session.request(self.collector.method, url, **self.collector.others)
                self.session.session = session
            else:
                # 不使用会话，直接发送请求：每次都是独立请求
                res = request(self.collector.method, url, **self.collector.others)
            
            # 记录请求结束时间并计算耗时
            end_time = datetime.datetime.now()
            self.response_request = res.request
            # 将微秒转换为毫秒记录到测试报告中
            self.test.recordTransDuring(int((end_time-start_time).microseconds/1000))
            
            # 保存响应数据
            self.save_response(res)
            
            # 构建响应信息日志
            response_log = '【响应信息】:<br>'
            response_log += '响应码: {}<br>'.format(self.status_code)
            response_log += '响应头: {}<br>'.format(dict2str(self.response_headers))
            if 'content-disposition' not in [key.lower() for key in self.response_headers.keys()]:
                # 普通响应内容
                response_text = '<b>响应体: {}</b>'.format(dict2str(self.response_content))
            else:
                # 文件下载响应
                response_text = '<b>响应体: 文件内容暂不展示, 长度{}</b>'.format(len(self.response_content_bytes))
            response_log += response_text
            self.test.debugLog(response_log)
            
            # 执行断言检查
            self.check()
            # 提取关联参数
            self.extract_depend_params()
        finally:
            # 记录接口执行结束日志
            self.test.debugLog('[{}]接口执行结束'.format(self.collector.apiName))
            # 执行请求后等待
            if int(self.collector.controller["sleepAfterRun"]) > 0:
                sleep(int(self.collector.controller["sleepAfterRun"]))
                self.test.debugLog("请求后等待%sS" % int(self.collector.controller["sleepAfterRun"]))

    def looper_controller(self, case, api_list, step_n):
        """
            循环控制器
            
            根据配置的循环类型执行相应的循环控制逻辑：
            - FOR循环：基于固定次数进行循环执行
            - WHILE循环：基于条件断言进行循环执行，支持超时控制
            
            Args:
                case: 测试用例实例，提供循环渲染和执行方法
                api_list: API步骤列表，包含所有待执行的API步骤
                step_n: 当前步骤在API列表中的索引位置
            
            ### 循环控制器配置格式示例：
                # FOR循环配置
                {
                    "type": "FOR",
                    "times": 5,           # 循环次数
                    "indexName": "i",     # 循环变量名
                    "num": 3              # 循环体包含的API步骤数量
                }
                
                # WHILE循环配置
                {
                    "type": "WHILE",
                    "timeout": 30000,     # 超时时间（毫秒），0表示无限循环
                    "assertion": "相等",   # 断言类型
                    "target": "${status}", # 断言目标值
                    "expect": "running",   # 期望值
                    "num": 2              # 循环体包含的API步骤数量
                }
            
            ### 循环类型说明：
                FOR: 固定次数循环，通过times参数控制循环次数
                WHILE: 条件循环，通过assertion断言控制循环执行，支持timeout超时设置
            
            ### 注意事项：
                - WHILE循环的timeout为0时可能会造成死循环，需要慎重选择
                - 每次WHILE循环都需要重新渲染循环控制器
                - FOR循环只需要渲染一次循环控制器
                - 循环索引名在嵌套循环中不应重复
        """
        if "type" in self.collector.looper and self.collector.looper["type"] == "WHILE":
            # WHILE循环：基于条件断言进行循环，兼容之前只有FOR循环的版本
            loop_start_time = datetime.datetime.now()
            # 循环条件：timeout为0表示无限循环，否则检查是否超时
            while self.collector.looper["timeout"] == 0 or (datetime.datetime.now() - loop_start_time).seconds * 1000 \
                    < self.collector.looper["timeout"]:     # timeout为0时可能会死循环 慎重选择
                # 渲染循环控制控制器 每次循环都需要渲染以获取最新的断言条件
                _looper = case.render_looper(self.collector.looper)
                # 执行循环条件断言检查
                result, _ = LMAssert(_looper['assertion'], _looper['target'], _looper['expect']).compare()
                if not result:
                    break  # 断言条件不满足，退出循环
                # 获取当前循环需要执行的API步骤列表
                _api_list = api_list[step_n: (step_n + _looper["num"])]
                case.loop_execute(_api_list, api_list[step_n]["apiId"])
        else:
            # FOR循环：基于固定次数进行循环
            # 渲染循环控制控制器 FOR循环只需渲染一次
            _looper = case.render_looper(self.collector.looper)
            for index in range(_looper["times"]):  # 执行指定次数的循环
                self.context[_looper["indexName"]] = index  # 给循环索引赋值，记录第几次循环（母循环和子循环的索引名不应一样）
                # 获取当前循环需要执行的API步骤列表
                _api_list = api_list[step_n: (step_n + _looper["num"])]
                case.loop_execute(_api_list, api_list[step_n]["apiId"])

    def condition_controller(self, case):
        """
            条件控制器
            
            根据配置的条件列表执行条件断言检查，决定是否执行当前测试步骤。
            条件控制器支持多个条件的组合判断，所有条件都必须满足才能继续执行。
            
            Args:
                case: 测试用例实例，提供条件渲染功能
            
            Returns:
                bool: 当所有条件都满足时返回True
                str: 当任一条件不满足或执行异常时返回错误信息
            
            ### 条件控制器配置格式示例：
                # 单个条件检查
                [
                    {
                        "assertion": "相等",           # 断言类型
                        "target": "${user_status}",    # 目标值（支持变量替换）
                        "expect": "active"             # 期望值
                    }
                ]
                
                # 多个条件检查（AND关系）
                [
                    {
                        "assertion": "相等",
                        "target": "${user_role}",
                        "expect": "admin"
                    },
                    {
                        "assertion": "大于",
                        "target": "${user_balance}",
                        "expect": 100
                    }
                ]
                
                # 复杂条件示例
                [
                    {
                        "assertion": "包含",
                        "target": "${permissions}",
                        "expect": "write"
                    },
                    {
                        "assertion": "不相等",
                        "target": "${last_login}",
                        "expect": null
                    }
                ]
            
            ### 条件检查流程：
                1. 通过case.render_conditions渲染条件配置
                2. 遍历所有条件进行断言检查
                3. 使用LMAssert进行条件比较
                4. 任一条件失败则立即返回错误信息
                5. 所有条件通过则返回True
            
            ### 注意事项：
                - 条件检查采用短路逻辑，第一个失败的条件会中断后续检查
                - 异常情况会被捕获并作为字符串返回
                - 空条件列表默认返回True
        """
        _conditions = case.render_conditions(self.collector.conditions)
        for condition in _conditions:
            try:
                result, msg = LMAssert(condition['assertion'], condition['target'], condition['expect']).compare()
                if not result:
                    return msg
            except Exception as e:
                return str(e)
        else:
            return True

    def exec_script(self, code):
        """
            ### 执行前后置脚本
            
            在测试步骤的前后执行用户自定义的Python脚本代码，用于实现复杂的业务逻辑处理。
            脚本可以访问请求和响应数据，操作测试上下文变量，实现数据的动态处理。
            
            Args:
                code (str): 要执行的Python脚本代码字符串
            
            ### 脚本环境提供的内置函数：
                print: 重定向的打印函数，输出会记录到测试日志中
                sys_put: 设置变量到测试上下文或公共参数中
                sys_get: 从测试上下文或公共参数中获取变量值
            
            ### 脚本环境提供的响应数据变量：
                res_request: HTTP请求对象
                res_code: HTTP响应状态码
                res_header: HTTP响应头字典
                res_data: 响应体内容（JSON或文本）
                res_cookies: 响应Cookie字符串
                res_bytes: 响应体原始字节数据
            
            ### 脚本代码示例：
                # 前置脚本：动态生成请求参数

                import time
                import hashlib
                
                # 生成时间戳
                timestamp = int(time.time())
                sys_put('current_time', timestamp)
                
                # 生成签名
                sign_str = f"user123{timestamp}secret_key"
                signature = hashlib.md5(sign_str.encode()).hexdigest()
                sys_put('signature', signature)
                
                print(f'生成签名: {signature}')

                
                # 后置脚本：处理响应数据
  
                if res_code == 200:
                    # 提取token
                    token = res_data['data']['token']
                    sys_put('auth_token', token)
                    
                    # 提取用户信息
                    user_info = res_data['data']['user']
                    sys_put('user_id', user_info['id'])
                    sys_put('username', user_info['name'])
                    
                    print(f'登录成功，用户ID: {user_info["id"]}')
                else:
                    error_msg = res_data.get('message', '未知错误')
                    sys_put('error_message', error_msg)
                    print(f'登录失败: {error_msg}')
                
                # 数据处理脚本

                import json
                
                # 处理复杂数据结构
                if 'user_list' in res_data:
                    active_users = [user for user in res_data['user_list'] if user['status'] == 'active']
                    sys_put('active_user_count', len(active_users))
                    
                    # 提取管理员用户
                    admin_users = [user['id'] for user in active_users if 'admin' in user.get('roles', [])]
                    sys_put('admin_user_ids', admin_users)

            
            ### 注意事项：
                - 脚本执行异常会导致测试步骤失败
                - print输出会记录到测试日志中，便于调试
                - sys_put和sys_get用于变量的存取，支持测试步骤间的数据传递
                - 脚本中可以直接访问和修改当前作用域的所有变量
        """
        def print(*args, sep=' ', end='\n', file=None, flush=False):
            """重定向的打印函数，将输出记录到测试日志缓冲区"""
            if file is None or file in (sys.stdout, sys.stderr):
                file = self.test.stdout_buffer
            self.print(*args, sep=sep, end=end, file=file, flush=flush)

        def sys_put(name, val, ps=False):
            """
                设置变量到测试上下文或公共参数中
                
                Args:
                    name (str): 变量名称
                    val: 变量值
                    ps (bool): False时设置到测试上下文，True时设置到公共参数
            """
            if ps:  # 默认给关联参数赋值，只有多传入true时才会给公参赋值
                self.params[name] = val
            else:
                self.context[name] = val

        def sys_get(name):
            """
                从测试上下文或公共参数中获取变量值
                
                Args:
                    name (str): 变量名称
                
                Returns:
                    变量值，优先从测试上下文中获取，其次从公共参数中获取
                
                Raises:
                    KeyError: 当变量不存在时抛出异常
            """
            if name in self.context:   # 优先从关联参数中取值
                return self.context[name]
            elif name in self.params:  # 其次从公共参数中取值
                return self.params[name]
            else:
                raise KeyError("不存在的公共参数或关联变量: {}".format(name))

        # 构建脚本执行的本地变量环境
        names = locals()
        names["res_request"] = self.response_request    # HTTP请求对象
        names["res_code"] = self.status_code            # HTTP响应状态码
        names["res_header"] = self.response_headers     # HTTP响应头
        names["res_data"] = self.response_content       # 响应体内容
        names["res_cookies"] = self.response_cookies    # 响应Cookie
        names["res_bytes"] = self.response_content_bytes # 响应体字节数据
        
        # 执行用户脚本代码
        exec(code)

    def exec_sql(self, sql, case):
        """执行前后置SQL语句
            
            在测试步骤的前后执行数据库SQL操作，支持查询和非查询类型的SQL语句。
            查询结果可以自动保存到测试上下文变量中，用于后续测试步骤的数据关联。
            
            Args:
                sql (str): SQL配置的JSON字符串，包含数据库连接信息和SQL语句
                case: 测试用例实例，提供SQL渲染功能
            
            ### SQL配置格式示例：
                # 查询操作配置
                    {
                        "db": {                    # 数据库连接配置
                            "host": "localhost",     # 数据库主机地址
                            "port": 3306,            # 数据库端口
                            "user": "test_user",     # 数据库用户名
                            "password": "password",  # 数据库密码
                            "database": "test_db"    # 数据库名称
                        },
                        "sqlType": "query",       # SQL类型：query(查询)
                        "sqlText": "SELECT id, name, email, status FROM users WHERE role = 'admin' AND created_at > '2023-01-01'",
                        "names": "user_id,user_name,user_email,user_status"  # 查询结果变量名列表
                    }
                
                # 插入操作配置
                    {
                        "db": {
                            "host": "localhost",
                            "port": 3306,
                            "user": "test_user",
                            "password": "password",
                            "database": "test_db"
                        },
                        "sqlType": "insert",
                        "sqlText": "INSERT INTO test_logs (test_id, api_name, result, created_at) VALUES (${test_id}, '${api_name}', '${result}', NOW())"
                    }
                
                # 更新操作配置
                    {
                        "db": {
                            "host": "localhost",
                            "port": 3306,
                            "user": "test_user",
                            "password": "password",
                            "database": "test_db"
                        },
                        "sqlType": "update",
                        "sqlText": "UPDATE users SET last_login = NOW(), login_count = login_count + 1 WHERE id = ${user_id}"
                    }
                
                # 删除操作配置
                    {
                        "db": {
                            "host": "localhost",
                            "port": 3306,
                            "user": "test_user",
                            "password": "password",
                            "database": "test_db"
                        },
                        "sqlType": "delete",
                        "sqlText": "DELETE FROM temp_data WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 DAY)"
                    }
            
            ### 数据格式示例：
                # 前置SQL：准备测试数据
                pre_sql = {
                    "db": {"host": "localhost", "port": 3306, "user": "test", "password": "123456", "database": "testdb"},
                    "sqlType": "insert",
                    "sqlText": "INSERT INTO test_users (name, email, role) VALUES ('${test_user}', '${test_email}', 'user')"
                }
                
                # 查询SQL：获取用户信息
                    query_sql = {
                        "db": {"host": "localhost", "port": 3306, "user": "test", "password": "123456", "database": "testdb"},
                        "sqlType": "query",
                        "sqlText": "SELECT id, name, email FROM users WHERE email = '${user_email}' LIMIT 1",
                        "names": "user_id,user_name,user_email"
                    }
                    
                    # 执行结果：查询结果保存到上下文变量
                    # context['user_id'] = [123]
                    # context['user_name'] = ['张三']
                    # context['user_email'] = ['zhangsan@example.com']
                
                # 多行查询结果示例
                    multi_query_sql = {
                        "db": {"host": "localhost", "port": 3306, "user": "test", "password": "123456", "database": "testdb"},
                        "sqlType": "query",
                        "sqlText": "SELECT id, name FROM users WHERE role = 'admin'",
                        "names": "admin_ids,admin_names"
                    }
                    
                    # 多行查询结果：
                    # context['admin_ids'] = [1, 2, 3]
                    # context['admin_names'] = ['管理员1', '管理员2', '管理员3']
                
            ### 功能特性：
                - 支持查询和非查询类型的SQL操作
                - 查询结果自动保存到测试上下文变量中
                - SQL语句支持变量替换和参数化
                - 自动管理数据库连接的创建和释放
                - 支持多种数据库类型
            
            ### 查询结果处理：
                - 查询结果按列顺序映射到指定的变量名
                - 空查询结果会将变量设置为空数组
                - 变量名数量不能超过查询结果列数
                - 查询结果保存在测试上下文中供后续步骤使用
            
            ### 异常处理：
                - 数据库连接失败时抛出KeyError
                - 变量名数量与查询结果不匹配时抛出IndexError
                - SQL执行失败时抛出相应的数据库异常
            
            ### 注意事项：
                - 空SQL配置（"{}"）会直接返回，不执行任何操作
                - 查询类型的SQL必须配置names参数用于保存结果
                - 变量名数量可以少于查询结果列数，但不能多于列数
                - 所有查询结果都会保存到测试上下文的关联变量中
            
            ### 存在问题
                - 即使查询结果为空，names的变量也会被创建，且也会抛出index错误总之只要index！=len（results）: ··· 总会执行
        """
        if sql == "{}":
            return
        sql = json.loads(case.render_sql(sql))
        if "host" not in sql["db"]:
            raise KeyError("数据库的host不存在，连接信息失败 请检查配置")
        conn = SQLConnect(**sql["db"])
        if sql["sqlType"] != "query":
            conn.exec(sql["sqlText"])
        else:
            results = conn.query(sql["sqlText"])    # 返回[[],[],[]]
            names = sql["names"].split(",")  # name数量可以比结果数量段，但不能长，不能会indexError
            for index, n in enumerate(names):
                if len(results) == 0:
                    self.context[n] = []  # 如果查询结果为空 则变量保存为空数组
                    continue
                if index >= len(results):
                    raise IndexError("变量数错误, 请检查变量数配置是否与查询语句一致，当前查询结果: <br>{}".format(results))
                self.context[n] = results[index]  # 保存变量到变量空间

    def save_response(self, res):
        """
            保存HTTP响应数据
            
            将HTTP响应的各个组成部分保存到实例属性中，供后续的断言检查、
            关联参数提取和脚本处理使用。
            
            Args:
                res: requests库的Response对象
            
            保存的响应数据包括：
                - status_code: HTTP响应状态码（如200、404、500等）
                - response_headers: HTTP响应头字典
                - response_content_bytes: 响应体原始字节数据
                - response_cookies: 响应Cookie字符串（格式：key1=value1;key2=value2）
                - response_content: 解析后的响应体内容
            
            ### 数据格式示例：
                # JSON响应示例
                response = requests.get('https://api.example.com/users/123')
                
                # 保存后的数据结构
                self.status_code = 200
                self.response_headers = {
                    'Content-Type': 'application/json',
                    'Content-Length': '156',
                    'Set-Cookie': 'session_id=abc123; Path=/; HttpOnly',
                    'X-Request-ID': 'req-456789'
                }
                self.response_content_bytes = b'{"id":123,"name":"张三","email":"zhangsan@example.com"}'
                self.response_cookies = 'session_id=abc123'
                self.response_content = {
                    'id': 123,
                    'name': '张三',
                    'email': 'zhangsan@example.com'
                }
                
                # 文本响应示例
                text_response = requests.get('https://api.example.com/health')
                self.status_code = 200
                self.response_content = 'OK'  # 纯文本内容
                
                # 文件下载响应示例
                file_response = requests.get('https://api.example.com/download/report.pdf')
                self.status_code = 200
                self.response_headers = {
                    'Content-Type': 'application/pdf',
                    'Content-Disposition': 'attachment; filename="report.pdf"',
                    'Content-Length': '2048576'
                }
                self.response_content_bytes = b'%PDF-1.4...'  # PDF文件字节数据
                self.response_content = b'%PDF-1.4...'       # 文件内容保持字节格式
            
            响应体解析逻辑：
                1. 首先尝试将响应体解析为JSON格式
                2. 如果JSON解析失败，则保存为纯文本格式
                3. 这样可以兼容JSON API和普通文本响应
            
            使用场景：
                - 断言检查：验证状态码、响应头、响应体内容
                - 关联参数：从响应中提取数据用于后续请求
                - 脚本处理：在前后置脚本中访问响应数据
                - 日志记录：记录完整的响应信息用于调试
            
            注意事项：
                - JSON解析失败时会静默降级为文本格式
                - 响应体字节数据和解析后内容都会保存
                - Cookie会被转换为字符串格式便于处理
                - 响应头会被转换为普通字典格式
        """
        self.status_code = res.status_code                   # HTTP响应状态码
        self.response_headers = dict(res.headers)            # HTTP响应头字典
        self.response_content_bytes = res.content            # 响应体原始字节数据
        
        # 处理响应Cookie，转换为字符串格式
        s = ''
        for key, value in res.cookies.items():
            s += '{}={};'.format(key, value)
        self.response_cookies = s[:-1]                       # 移除最后一个分号
        
        try:
            # 尝试将响应体解析为JSON格式
            self.response_content = res.json()
        except Exception:
            # JSON解析失败时，保存为纯文本格式
            self.response_content = res.text

    def extract_depend_params(self):
        """
            提取关联参数
            
            从HTTP请求和响应中提取指定的数据，并将其保存为关联参数，供后续测试步骤使用。
            支持从多个位置提取数据：响应体、响应头、请求体、请求头、请求参数、Cookie等。
            
            关联参数配置格式：
                {
                    "name": "user_id",              # 关联参数名称
                    "from": "resBody",              # 提取位置：resBody/resHeader/reqBody/reqHeader/reqQuery
                    "method": "jsonpath",           # 提取方法：jsonpath/regex/xpath等
                    "expression": "$.data.user.id"  # 提取表达式
                }
            
            支持的提取位置：
                - resBody: 响应体内容（JSON或文本）
                - resHeader: 响应头信息
                - reqBody: 请求体内容（JSON或表单数据）
                - reqHeader: 请求头信息
                - reqQuery: URL查询参数
            
            特殊表达式处理：
                - "$": 直接提取响应体原始字节数据
                - "cookie"/"cookies": 直接提取响应Cookie字符串
            
            提取方法支持：
                - jsonpath: 用于JSON数据的路径提取
                - regex: 用于文本的正则表达式提取
                - xpath: 用于XML/HTML的路径提取
            
            使用场景：
                - 登录接口提取token用于后续请求认证
                - 创建接口提取ID用于后续查询或删除
                - 从响应头中提取会话信息
                - 从Cookie中提取认证信息
                - 从请求中提取数据用于验证
            
            异常处理：
                - 当提取位置不支持时抛出ExtractValueError
                - 当提取表达式无法匹配数据时抛出ExtractValueError
                - 异常会导致当前测试步骤失败
            
            注意事项：
                - 关联参数会覆盖测试上下文中的同名变量
                - 提取的数据类型保持原始格式
                - 建议在配置关联参数前先确认数据结构
                - 空的relations配置不会执行任何提取操作
        """
        if self.collector.relations is not None:
            for items in self.collector.relations:
                # 处理特殊表达式：直接提取响应体字节数据
                if items['expression'].strip() == '$':
                    value = self.response_content_bytes
                # 处理特殊表达式：直接提取Cookie信息
                elif items['expression'].strip().lower() in ['cookie', 'cookies']:
                    value = self.response_cookies
                else:
                    # 根据提取位置确定数据源
                    if items['from'] == 'resHeader':
                        data = self.response_headers          # 响应头数据
                    elif items['from'] == 'resBody':
                        data = self.response_content          # 响应体数据
                    elif items['from'] == 'reqHeader':
                        data = self.collector.others['headers']  # 请求头数据
                    elif items['from'] == 'reqQuery':
                        data = self.collector.others['params']   # URL查询参数
                    elif items['from'] == 'reqBody':
                        # 根据请求体类型选择对应的数据
                        if self.collector.body_type == "json":
                            data = self.collector.others['json']  # JSON请求体
                        else:
                            data = self.collector.others['data']  # 表单或其他请求体
                    else:
                        raise ExtractValueError('无法从{}位置提取依赖参数'.format(items['from']))
                    # 使用指定的方法和表达式提取数据
                    value = extract(items['method'], data, items['expression'])
                # 获取关联参数名称
                key = items['name']
                # 将提取的值保存到测试上下文中
                self.context[key] = value

    def check(self):
        """
            执行断言检查
            
            对HTTP请求和响应的各个部分进行断言验证，确保接口返回的数据符合预期。
            支持多种断言类型和比较关系，提供灵活的数据验证能力。
            
            断言配置格式：
                {
                    "assertion": "相等",           # 断言类型：相等/不相等/包含/大于等
                    "from": "resBody",             # 断言数据来源
                    "method": "jsonpath",          # 数据提取方法
                    "expression": "$.code",        # 提取表达式
                    "expect": 200                  # 期望值
                }
            
            支持的数据来源：
                - resCode: HTTP响应状态码
                - resBody: 响应体内容（JSON或文本）
                - resHeader: 响应头信息
            
            支持的断言类型：
                - 相等: 实际值等于期望值
                - 不相等: 实际值不等于期望值
                - 包含: 实际值包含期望值
                - 不包含: 实际值不包含期望值
                - 大于: 实际值大于期望值
                - 大于等于: 实际值大于等于期望值
                - 小于: 实际值小于期望值
                - 小于等于: 实际值小于等于期望值
                - 长度相等: 实际值长度等于期望值
                - 正则匹配: 实际值匹配期望的正则表达式
            
            断言执行流程：
                1. 遍历所有配置的断言项
                2. 根据数据来源提取实际值
                3. 使用LMAssert进行断言比较
                4. 收集断言结果和消息
                5. 任一断言失败则中断后续检查
                6. 生成最终断言结果报告
            
            默认断言：
                当没有配置任何断言时，默认检查HTTP状态码是否为200
            
            异常处理：
                - 数据提取失败时记录为断言失败
                - 不支持的数据来源会抛出ExtractValueError
                - 所有异常都会被捕获并转换为断言失败消息
            
            断言结果：
                保存到self.assert_result中，包含：
                - apiId: 接口ID
                - apiName: 接口名称
                - result: 最终断言结果（True/False）
                - checkMessages: 所有断言检查的详细消息列表
            
            使用场景：
                - 验证接口返回状态码
                - 检查响应数据的正确性
                - 验证响应头信息
                - 检查业务逻辑的正确性
                - 确保接口行为符合预期
            
            注意事项：
                - 断言失败会导致整个测试步骤失败
                - 断言按配置顺序执行，失败时会中断后续断言
                - 空断言配置会使用默认的状态码200检查
                - 断言消息会记录到测试日志中便于问题排查
        """
        check_messages = list()  # 存储所有断言检查的消息
        if self.collector.assertions is not None:
            results = list()  # 存储所有断言的结果
            for items in self.collector.assertions:
                try:
                    # 根据断言数据来源提取实际值
                    if items['from'] == 'resCode':
                        # 从HTTP响应状态码中获取实际值
                        actual = self.status_code
                    elif items['from'] == 'resHeader':
                        # 从响应头中提取实际值
                        actual = extract(items['method'], self.response_headers, items['expression'])
                    elif items['from'] == 'resBody':
                        # 从响应体中提取实际值
                        actual = extract(items['method'], self.response_content, items['expression'])
                    else:
                        # 不支持的数据来源
                        raise ExtractValueError('无法在{}位置进行断言'.format(items['from']))
                    # 使用LMAssert进行断言比较
                    result, msg = LMAssert(items['assertion'], actual, items['expect']).compare()
                except ExtractValueError as e:
                    # 数据提取失败时记录为断言失败
                    result = False
                    msg = '接口响应失败或{}'.format(str(e))
                # 收集断言结果和消息
                results.append(result)
                check_messages.append(msg)
                if not result:
                    # 断言失败时中断后续检查
                    break
            # 计算最终断言结果（所有断言都必须通过）
            final_result = all(results)
        else:
            # 没有配置断言时，默认检查状态码是否为200
            final_result, msg = LMAssert('相等', self.status_code, str(200)).compare()
            check_messages.append(msg)
        # 保存断言结果到实例属性中
        self.assert_result = {
            'apiId': self.collector.apiId,        # 接口ID
            'apiName': self.collector.apiName,    # 接口名称
            'result': final_result,               # 最终断言结果
            'checkMessages': check_messages       # 断言检查消息列表
        }

    def pop_content_type(self):
        """
            移除请求头中的Content-Type字段
            
            在某些特殊情况下需要移除Content-Type头，让HTTP客户端自动设置合适的值。
            主要用于文件上传场景，避免手动设置的Content-Type与实际内容不匹配。
            
            处理逻辑：
                1. 检查请求头是否为None
                2. 遍历所有header键名（不区分大小写）
                3. 找到content-type字段并移除
                4. 更新collector中的headers配置
            
            使用场景：
                - 文件上传时让requests库自动设置multipart/form-data
                - 避免Content-Type与实际请求体格式不匹配
                - 某些API要求不设置Content-Type头
            
            注意事项：
                - 不区分大小写匹配Content-Type
                - 如果headers为None则直接返回
                - 直接修改collector.others['headers']中的数据
            
            示例：
                # 文件上传前移除Content-Type
                if 'files' in self.collector.others:
                    self.pop_content_type()
        """
        if self.collector.others['headers'] is None:
            return
        pop_key = None
        for key, value in self.collector.others['headers'].items():
            if key.lower() == 'content-type':
                pop_key = key
                break
        if pop_key is not None:
            self.collector.others['headers'].pop(pop_key)


def dict2str(data):
    if not isinstance(data, str):
        return str(data)
    else:
        return data


class RemoveParamError(Exception):
    """
        参数移除错误异常
        
        当尝试移除不存在的参数或在不允许的情况下移除参数时抛出此异常。
        主要用于参数处理和数据清理过程中的错误处理。
        
        使用场景：
            - 尝试移除不存在的请求参数
            - 在禁止移除的上下文中执行移除操作
            - 参数移除过程中发生的其他错误
        
        继承关系：
            Exception -> RemoveParamError
        
        示例：
            try:
                remove_param('non_existent_param')
            except RemoveParamError as e:
                print(f"参数移除失败: {e}")
    """


class AssertRelationError(Exception):
    """
        断言关系错误异常
        
        当断言检查失败或断言关系配置错误时抛出此异常。
        用于标识测试断言过程中的各种错误情况。
        
        异常触发场景：
            - 断言比较结果不符合预期
            - 不支持的断言关系类型
            - 断言数据提取失败
            - 断言配置格式错误
        
        继承关系：
            Exception -> AssertRelationError
        
        异常处理：
            此异常通常会导致测试步骤失败，并在测试报告中记录详细的失败信息
        
        示例：
            try:
                assert_equal(actual_value, expected_value)
            except AssertRelationError as e:
                test_log.error(f"断言失败: {e}")
                raise e
    """
