import json
import re

from tools.utils.utils import proxies_join, handle_form_data, handle_files


class ApiRequestCollector:
    """
        API请求数据收集器
        
        用于收集和处理API测试用例的各种请求参数，包括URL、请求方法、请求头、
        请求体、代理设置、超时配置等。该类将原始的API数据转换为标准化的
        请求参数格式，便于后续的HTTP请求执行。
        
        ### 主要功能：
            - 收集基本请求信息（ID、名称、方法、URL等）
            - 处理请求头和Cookie
            - 解析请求体（JSON、表单、文件等）
            - 配置请求选项（超时、代理、验证等）
            - 收集断言和关联数据
        
        ### Attributes:
            apiId (str): API接口ID
            apiName (str): API接口名称
            method (str): HTTP请求方法
            url (str): 请求URL
            path (str): 请求路径
            protocol (str): 协议类型
            body_type (str): 请求体类型
            others (dict): 其他请求参数
            controller (dict): 控制器配置
            looper (dict): 循环执行配置
            conditions (list): 执行条件列表
            assertions (list): 断言列表
            relations (list): 关联数据列表
        
        ### Example:
            # 基本使用示例
            api_data = {
                "apiId": "get_user_info",
                "apiName": "获取用户信息",
                "protocol": "HTTP",
                "method": "GET",
                "url": "https://api.example.com",
                "path": "/users/{user_id}",
                "rest": {"user_id": "123"},
                "query": {"include": "profile,settings"},
                "headers": {"Authorization": "Bearer ${token}"},
                "controller": {"timeout": 30}
            }
            
            collector = ApiRequestCollector()
            collector.collect(api_data)
            
            # 访问收集结果
            print(collector.method)  # "GET"
            print(collector.path)    # "/users/123"
            print(collector.others["params"])  # {"include": "profile,settings"}
    """

    def __init__(self):
        """
            初始化API请求数据收集器
            
            设置所有属性的初始值，为后续的数据收集做准备。
        """
        self.apiId = None  # API接口ID
        self.apiName = None  # API接口名称
        self.method = None  # HTTP请求方法
        self.url = None  # 请求URL
        self.path = None  # 请求路径
        self.protocol = None  # 协议类型
        self.body_type = None  # 请求体类型
        self.others = {}  # 其他请求参数（headers、params、data等）
        self.controller = {}  # 控制器配置（超时、会话等）
        self.looper = {}  # 循环执行配置
        self.conditions = []  # 执行条件列表
        self.assertions = []  # 断言列表
        self.relations = []  # 关联数据列表

    def collect_flag(self, api_data, arg_name):
        """
            收集必要的标志字段
            
            Args:
                api_data (dict): API数据字典
                arg_name (str): 参数名称
                
            Raises:
                NotExistedFieldError: 当字段不存在或为空时抛出异常
        """
        if arg_name not in api_data or api_data[arg_name] is None:
            raise NotExistedFieldError('接口数据{}字段不存在或为空'.format(arg_name))
        elif type(api_data[arg_name]) is str and len(api_data[arg_name]) == 0:
            raise NotExistedFieldError('接口数据{}字段长度为0'.format(arg_name))
        else:
            setattr(self, arg_name, api_data[arg_name])

    def collect_other(self, api_data, arg_name, func=lambda x: x):
        """
            收集其他可选参数到others字典中
            
            Args:
                api_data (dict): API数据字典
                arg_name (str): 参数名称
                func (callable): 处理函数，默认为恒等函数
            
            ### Example:
                # 收集请求头（无转换函数）
                api_data = {"headers": {"Content-Type": "application/json"}}
                collector.collect_other(api_data, "headers")
                # 结果：self.others["headers"] = {"Content-Type": "application/json"}
                
                # 收集代理配置（带转换函数）
                api_data = {"proxies": "http://proxy.example.com:8080"}
                collector.collect_other(api_data, "proxies", proxies_join)
                # 结果：self.others["proxies"] = {"http": "...", "https": "..."}
                
                # 收集不存在的参数
                api_data = {}
                collector.collect_other(api_data, "missing_key")
                # 结果：self.others["missing_key"] = None
        """
        if arg_name not in api_data or api_data[arg_name] is None or len(api_data[arg_name]) == 0:
            self.others[arg_name] = None
        else:
            self.others[arg_name] = func(api_data[arg_name])

    def collect_context(self, api_data, arg_name):
        """
            收集上下文相关的可选字段
            
            Args:
                api_data (dict): API数据字典
                arg_name (str): 参数名称
            
            ### Example:
                # 收集断言配置
                api_data = {
                    "assertions": '[{"source": "response", "property": "status_code", "operation": "eq", "value": 200}]'
                }
                collector.collect_context(api_data, "assertions")
                # 结果：self.assertions = [{"source": "response", "property": "status_code", "operation": "eq", "value": 200}]
                
                # 收集关联配置
                api_data = {
                    "relations": '[{"source": "response", "property": "body.token", "variable": "auth_token"}]'
                }
                collector.collect_context(api_data, "relations")
                # 结果：self.relations = [{"source": "response", "property": "body.token", "variable": "auth_token"}]
                
                # 配置不存在的情况
                api_data = {}
                collector.collect_context(api_data, "missing_config")
                # 结果：对应属性保持为None
        """
        if arg_name not in api_data or api_data[arg_name] is None or len(api_data[arg_name]) == 0:
            setattr(self, arg_name, None)
        else:
            setattr(self, arg_name, api_data[arg_name])

    def collect_id(self, api_data):
        """
            收集API接口ID
            
            Args:
                api_data (dict): API数据字典
        """
        self.collect_flag(api_data, "apiId")

    def collect_name(self, api_data):
        """
            收集API接口名称
            
            Args:
                api_data (dict): API数据字典
        """
        self.collect_flag(api_data, "apiName")

    def collect_protocol(self, api_data):
        """
            收集协议类型
            
            Args:
                api_data (dict): API数据字典
        """
        self.collect_flag(api_data, "protocol")

    def collect_method(self, api_data):
        """
            收集HTTP请求方法
            
            Args:
                api_data (dict): API数据字典
                
            Raises:
                UnDefinableMethodError: 当请求方法未定义时抛出异常
        """
        if 'method' not in api_data or api_data['method'] is None or len(api_data['method']) == 0:
            raise UnDefinableMethodError("接口{}未定义请求方法".format(api_data['apiId']))
        method = api_data['method'].upper()

        self.method = method

    def collect_url(self, api_data):
        """
            收集请求URL
            
            Args:
                api_data (dict): API数据字典
                
            Raises:
                UnDefinablePathError: 当URL未设置时抛出异常
        """
        if 'url' not in api_data:
            raise UnDefinablePathError("接口{}未设置域名".format(api_data['apiId']))
        else:
            self.url = api_data['url']

    def collect_path(self, api_data):
        """
            收集请求路径并处理路径参数替换
            
            Args:
                api_data (dict): API数据字典
                
            ### 路径参数替换示例：
                # 原始路径配置
                api_data = {
                    "path": "/users/{user_id}/posts/{post_id}",
                    "rest": {
                        "user_id": "123",
                        "post_id": "456"
                    }
                }
                
                # 处理后的路径
                # self.path = "/users/123/posts/456"
                
                # 兼容老版本格式
                api_data = {
                    "path": "/api/#{version}/users/{user_id}",
                    "rest": {
                        "version": "v1",
                        "user_id": "789"
                    }
                }
                
                # 处理后的路径
                # self.path = "/api/v1/users/789"
                
            ### Raises:
                UnDefinablePathError: 当路径未设置时抛出异常

            ### 存在问题
                1. 未处理路径参数匹配rest匹配不到的情况，
        """
        if 'path' not in api_data:
            raise UnDefinablePathError("接口{}未设置路径".format(api_data['apiId']))
        else:
            fields = re.findall(r'\{(.*?)\}', api_data['path'])
            path = api_data['path']
            for field in fields:
                result = "{%s}" % field
                if field in api_data['rest']:
                    result = api_data["rest"][field]  # 将path中的参数替换成rest
                if "#{%s}" % field in path: # 兼容老版本#{name}
                    path = path.replace("#{%s}" % field, result)
                else:
                    path = path.replace("{%s}" % field, result)
            self.path = path

    def collect_controller(self, api_data):
        """
            收集控制器配置
            
            控制器用于配置请求的执行控制参数，如超时设置、会话管理、
            前后置脚本执行、错误处理等。为缺失的配置项设置默认值。
            
            Args:
                api_data (dict): API数据字典
            
            ### 控制器配置格式示例：
                {
                    "sleepBeforeRun": 1000,        # 执行前等待时间（毫秒）
                    "sleepAfterRun": 500,          # 执行后等待时间（毫秒）
                    "useSession": "true",          # 是否使用会话
                    "saveSession": "true",         # 是否保存会话
                    "timeout": 30,                 # 请求超时时间（秒）
                    "requireStream": "false",      # 是否使用流式传输
                    "requireVerify": "true",       # 是否验证SSL证书
                    "errorContinue": "false",      # 错误后是否继续执行
                    "pre": {                       # 前置脚本和SQL配置
                        "script": "print('执行前置脚本')",
                        "sql": {
                            "db": {"host": "localhost", "port": 3306, "user": "test", "password": "123456", "database": "testdb"},
                            "sqlType": "query",
                            "sqlText": "SELECT id FROM users WHERE status = 'active'",
                            "names": "active_user_ids"
                        }
                    },
                    "post": {                      # 后置脚本和SQL配置
                        "script": "print('执行后置脚本')",
                        "sql": {
                            "db": {"host": "localhost", "port": 3306, "user": "test", "password": "123456", "database": "testdb"},
                            "sqlType": "insert",
                            "sqlText": "INSERT INTO test_logs (api_id, result, created_at) VALUES ('${api_id}', '${result}', NOW())"
                        }
                    },
                    "whetherExec": '[{"source": "context", "property": "user_role", "operation": "eq", "value": "admin"}]',  # 执行条件JSON字符串
                    "loopExec": '{"type": "FOR", "start": 1, "end": 5, "step": 1, "variable": "loop_index"}'  # 循环配置JSON字符串
                }
        """
        if "sleepBeforeRun" not in api_data["controller"]:
            api_data["controller"]["sleepBeforeRun"] = 0  # 默认执行前不等待
        if "sleepAfterRun" not in api_data["controller"]:
            api_data["controller"]["sleepAfterRun"] = 0  # 默认执行完成不等待
        if "useSession" not in api_data["controller"]:
            api_data["controller"]["useSession"] = "false"  # 默认不使用session
        if "saveSession" not in api_data["controller"]:
            api_data["controller"]["saveSession"] = "false"  # 默认不保存session
        if "pre" not in api_data["controller"]:
            api_data["controller"]["pre"] = None  # 默认没有前置脚本和sql
        if "post" not in api_data["controller"]:
            api_data["controller"]["post"] = None  # 默认没有后置脚本和sql
        if "errorContinue" not in api_data["controller"]:
            api_data["controller"]["errorContinue"] = "false"  # 默认错误后不再执行
        self.controller = api_data["controller"]

    def collect_conditions(self, api_data):
        """
            ### 收集执行条件配置
            
            从控制器配置中解析执行条件，用于控制API请求是否执行。
            条件配置以JSON格式存储在controller的whetherExec字段中。
            
            Args:
                api_data (dict): API数据字典
            
            ### 执行条件配置格式示例：
                # 单个条件
                [
                    {
                        "source": "context",           # 数据来源：context(上下文变量)
                        "property": "user_role",       # 属性名称
                        "operation": "eq",            # 比较操作：eq(等于)
                        "value": "admin"              # 期望值
                    }
                ]
                
                # 多个条件（AND关系）
                [
                    {
                        "source": "context",
                        "property": "user_status",
                        "operation": "eq",
                        "value": "active"
                    },
                    {
                        "source": "context",
                        "property": "user_level",
                        "operation": "gte",           # 大于等于
                        "value": 5
                    }
                ]
                
                # 响应数据条件
                [
                    {
                        "source": "response",          # 数据来源：response(响应数据)
                        "property": "status_code",     # 响应状态码
                        "operation": "eq",
                        "value": 200
                    },
                    {
                        "source": "response",
                        "property": "body.code",       # 响应体中的字段
                        "operation": "eq",
                        "value": 0
                    }
                ]
        """
        if "whetherExec" in api_data["controller"]:
            self.conditions = json.loads(api_data["controller"]["whetherExec"])

    def collect_looper(self, api_data):
        """
            ### 收集循环执行配置
            
            从控制器配置中解析循环执行参数，用于配置API请求的循环执行逻辑，
            如循环次数、循环条件等。循环配置以JSON格式存储在controller的loopExec字段中。
            
            Args:
                api_data (dict): API数据字典
            
            ### 循环执行配置格式示例：
                # FOR循环配置
                {
                    "type": "FOR",                 # 循环类型：FOR(计数循环)
                    "start": 1,                    # 起始值
                    "end": 10,                     # 结束值
                    "step": 1,                     # 步长
                    "variable": "loop_index"       # 循环变量名
                }
                
                # WHILE循环配置
                {
                    "type": "WHILE",               # 循环类型：WHILE(条件循环)
                    "maxLoop": 100,               # 最大循环次数
                    "conditions": [               # 循环条件列表
                        {
                            "source": "context",
                            "property": "retry_count",
                            "operation": "lt",       # 小于
                            "value": 5
                        },
                        {
                            "source": "response",
                            "property": "status_code",
                            "operation": "ne",       # 不等于
                            "value": 200
                        }
                    ]
                }
                
                # 数据驱动循环配置
                {
                    "type": "DATA",                # 循环类型：DATA(数据驱动)
                    "dataSource": "test_data",     # 数据源变量名
                    "itemVariable": "current_item" # 当前项变量名
                }
        """
        if "loopExec" in api_data["controller"]:
            self.looper = json.loads(api_data["controller"]["loopExec"])

    def collect_query(self, api_data):
        """
            收集查询参数（URL参数）
            
            收集GET请求或其他请求的URL查询参数，如?key=value&key2=value2。
            
            Args:
                api_data (dict): API数据字典
            
            ### 查询参数格式示例：
                # 查询参数配置
                api_data = {
                    "query": {
                        "page": "1",
                        "size": "20",
                        "keyword": "${search_keyword}",
                        "category": "tech",
                        "sort": "created_at",
                        "order": "desc"
                    }
                }
                
                # 处理后的结果
                # self.others["params"] = {
                #     "page": "1",
                #     "size": "20",
                #     "keyword": "${search_keyword}",
                #     "category": "tech",
                #     "sort": "created_at",
                #     "order": "desc"
                # }
                
                # 空查询参数
                api_data = {"query": {}}
                # 处理后：self.others["params"] = None
        """
        if len(api_data["query"]) > 0:
            self.others["params"] = api_data["query"]
        else:
            self.others["params"] = None

    def collect_headers(self, api_data):
        """
            收集请求头信息
            
            收集HTTP请求头，如Content-Type、Authorization等。
            
            Args:
                api_data (dict): API数据字典
            
            ### 请求头格式示例：
                api_data = {
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer ${access_token}",
                        "User-Agent": "TestClient/1.0",
                        "X-Request-ID": "${request_id}",
                        "Accept": "application/json",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
                    }
                }
                
                # 处理后的结果
                # self.others["headers"] = {
                #     "Content-Type": "application/json",
                #     "Authorization": "Bearer ${access_token}",
                #     "User-Agent": "TestClient/1.0",
                #     "X-Request-ID": "${request_id}",
                #     "Accept": "application/json",
                #     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
                # }
        """
        self.collect_other(api_data, 'headers')

    def collect_cookies(self, api_data):
        """
            收集Cookie信息
            
            收集HTTP请求的Cookie数据，并将headers中的cookie字段提取到标准格式。
            
            Args:
                api_data (dict): API数据字典
            
            ### Cookie处理示例：
                # 原始请求头中包含Cookie
                api_data = {
                    "headers": {
                        "Content-Type": "application/json",
                        "Cookie": "sessionid=abc123; csrftoken=xyz789; user_pref=dark_mode",
                        "Authorization": "Bearer token123"
                    }
                }
                
                # 处理后的结果
                # self.others["headers"] = {
                #     "Content-Type": "application/json",
                #     "cookie": "sessionid=abc123; csrftoken=xyz789; user_pref=dark_mode",  # 统一为小写
                #     "Authorization": "Bearer token123"
                # }
                
                # 支持不同大小写的Cookie字段
                api_data = {
                    "headers": {
                        "COOKIE": "session=value1",     # 大写
                        "cookies": "user=value2"        # 复数形式
                    }
                }
                # 都会被统一处理为"cookie"字段
        """
        if self.others['headers'] is not None:
            pop_key = None
            for key in self.others['headers']:
                if key.strip().lower() in ['cookie', 'cookies']:
                    pop_key = key
                    break
            if pop_key is not None:
                value = self.others['headers'].pop(pop_key)
                self.others['headers']['cookie'] = value

    def collect_proxies(self, api_data):
        """
            收集代理配置
            
            收集HTTP代理设置，使用proxies_join函数处理代理格式。
            
            Args:
                api_data (dict): API数据字典
            
            ### 代理配置格式示例：
                api_data = {
                    "proxies": {
                        "http": "http://proxy.example.com:8080",
                        "https": "https://proxy.example.com:8080"
                    }
                }
                
                # 或者简化格式
                api_data = {
                    "proxies": "http://proxy.example.com:8080"
                }
                
                # 带认证的代理
                api_data = {
                    "proxies": {
                        "http": "http://username:password@proxy.example.com:8080",
                        "https": "https://username:password@proxy.example.com:8080"
                    }
                }
                
                # 处理后通过proxies_join函数转换为标准格式
                # self.others["proxies"] = {"http": "...", "https": "..."}
        """
        self.collect_other(api_data, 'proxies', proxies_join)

    def collect_body(self, api_data):
        """
            收集请求体数据
            
            根据不同的请求体类型处理请求体数据，支持多种格式：
            - json: JSON格式数据，解析后存储为json参数
            - form-urlencoded/form-data: 表单数据，分离数据和文件
            - text/xml/html: 文本类型数据，存储为data参数
            - file: 文件上传，处理文件数据
            
            Args:
                api_data (dict): API数据字典，包含body字段
            
            ### 请求体数据格式示例：
                # JSON格式请求体
                {
                    "type": "json",
                    "json": '{"username": "${user_name}", "password": "${user_password}", "remember": true}'
                }
                # 处理后：self.others["json"] = {"username": "${user_name}", "password": "${user_password}", "remember": True}
                
                # 表单数据请求体（form-urlencoded）
                {
                    "type": "form-urlencoded",
                    "form": [
                        {"key": "username", "value": "${user_name}", "type": "text"},
                        {"key": "password", "value": "${user_password}", "type": "text"},
                        {"key": "avatar", "value": "/path/to/avatar.jpg", "type": "file"}
                    ]
                }
                # 处理后：
                # self.others["data"] = {"username": "${user_name}", "password": "${user_password}"}
                # self.others["files"] = {"avatar": ("/path/to/avatar.jpg", open("/path/to/avatar.jpg", "rb"))}
                
                # 多部分表单数据（form-data）
                {
                    "type": "form-data",
                    "form": [
                        {"key": "title", "value": "测试文档", "type": "text"},
                        {"key": "description", "value": "这是一个测试文档", "type": "text"},
                        {"key": "document", "value": "/path/to/document.pdf", "type": "file"},
                        {"key": "thumbnail", "value": "/path/to/thumb.png", "type": "file"}
                    ]
                }
                
                # 原始文本请求体
                {
                    "type": "text",
                    "raw": "这是原始文本数据\n包含换行符"
                }
                # 处理后：self.others["data"] = "这是原始文本数据\n包含换行符"
                
                # XML格式请求体
                {
                    "type": "xml",
                    "raw": "<?xml version='1.0' encoding='UTF-8'?><user><name>${user_name}</name><email>${user_email}</email></user>"
                }
                
                # HTML格式请求体
                {
                    "type": "html",
                    "raw": "<html><body><h1>测试页面</h1><p>用户：${user_name}</p></body></html>"
                }
                
                # 文件上传请求体
                {
                    "type": "file",
                    "file": [
                        {"key": "upload_file", "value": "/path/to/upload.zip"},
                        {"key": "backup_file", "value": "/path/to/backup.tar.gz"}
                    ]
                }
                # 处理后：self.others["files"] = {"upload_file": open("/path/to/upload.zip", "rb"), "backup_file": open("/path/to/backup.tar.gz", "rb")}
        """
        body = api_data["body"]
        if body is None:
            return
        
        self.body_type = body["type"]
        
        if body["type"] == "json":
            # JSON格式数据处理
            if body["json"] != '':
                body_json = json.loads(body["json"])
                if len(body_json) > 0:
                    self.others["json"] = body_json
        elif body["type"] in ("form-urlencoded", "form-data"):
            # 表单数据处理，分离普通数据和文件数据
            body_data, body_file = handle_form_data(body["form"])
            if len(body_data) > 0:
                self.others["data"] = body_data
            if len(body_file) > 0:
                self.others["files"] = body_file
        elif body["type"] in ("text", "xml", "html"):
            # 文本类型数据处理
            if body["raw"] != "":
                self.others["data"] = body["raw"]
        elif body["type"] == "file":
            # 文件上传处理
            files = handle_files(body["file"])
            if len(files) > 0:
                self.others["files"] = files

    def collect_stream(self, api_data):
        """
            收集流式传输配置
            
            配置是否使用流式传输来处理响应数据。从控制器配置中读取requireStream字段。
            
            Args:
                api_data (dict): API数据字典
            
            ### 流式传输配置示例：
                # 启用流式传输
                api_data = {
                    "controller": {
                        "requireStream": "true"
                    }
                }
                # 处理后：self.others["stream"] = True
                
                # 禁用流式传输
                api_data = {
                    "controller": {
                        "requireStream": "false"
                    }
                }
                # 处理后：self.others["stream"] = False
                
                # 未配置流式传输
                api_data = {"controller": {}}
                # 处理后：self.others["stream"] = None
        """
        if "requireStream" in api_data["controller"]:
            if api_data["controller"]["requireStream"].lower() == "true":
                self.others["stream"] = True
            else:
                self.others["stream"] = False
        else:
            self.others["stream"] = None

    def collect_verify(self, api_data):
        """
            收集SSL证书验证配置
            
            配置是否验证SSL证书。从控制器配置中读取requireVerify字段。
            
            Args:
                api_data (dict): API数据字典
            
            ### SSL验证配置示例：
                # 启用SSL证书验证
                api_data = {
                    "controller": {
                        "requireVerify": "true"
                    }
                }
                # 处理后：self.others["verify"] = True
                
                # 禁用SSL证书验证（用于测试环境）
                api_data = {
                    "controller": {
                        "requireVerify": "false"
                    }
                }
                # 处理后：self.others["verify"] = False
                
                # 未配置SSL验证
                api_data = {"controller": {}}
                # 处理后：self.others["verify"] = None
        """
        if "requireVerify" in api_data["controller"]:
            if api_data["controller"]["requireVerify"].lower() == "true":
                self.others["verify"] = True
            else:
                self.others["verify"] = False
        else:
            self.others["verify"] = None

    def collect_auth(self, api_data):
        """
            收集身份认证配置
            
            配置HTTP身份认证信息，如Basic Auth、Digest Auth等。
            当前实现为空，可根据需要扩展。
            
            Args:
                api_data (dict): API数据字典
            
            ### 认证配置格式示例：
                # Basic认证
                api_data = {
                    "auth": {
                        "type": "basic",
                        "username": "admin",
                        "password": "password123"
                    }
                }
                # 处理后：self.others["auth"] = ("admin", "password123")
                
                # Bearer Token认证
                api_data = {
                    "auth": {
                        "type": "bearer",
                        "token": "${access_token}"
                    }
                }
                # 处理后：self.others["headers"]["Authorization"] = "Bearer ${access_token}"
                
                # API Key认证
                api_data = {
                    "auth": {
                        "type": "apikey",
                        "key": "X-API-Key",
                        "value": "${api_key}",
                        "location": "header"  # header或query
                    }
                }
                # 处理后：self.others["headers"]["X-API-Key"] = "${api_key}"
        """
        pass

    def collect_timeout(self, api_data):
        """
            收集超时配置
            
            配置请求超时时间。从控制器配置中读取timeout字段并转换为整数。
            
            Args:
                api_data (dict): API数据字典
            
            ### 超时配置示例：
                api_data = {
                    "controller": {
                        "timeout": "30"  # 字符串格式的超时时间（秒）
                    }
                }
                
                # 处理后的结果
                # self.others["timeout"] = 30  # 转换为整数
                
                # 未配置超时时间
                api_data = {"controller": {}}
                # 处理后：self.others["timeout"] = None
        """
        if "timeout" in api_data["controller"]:
            self.others["timeout"] = int(api_data["controller"]["timeout"])
        else:
            self.others["timeout"] = None

    def collect_allow_redirects(self, api_data):
        """
            收集重定向配置
            
            配置是否允许HTTP重定向。当前实现为空，可根据需要扩展。
            
            Args:
                api_data (dict): API数据字典
            
            ### 重定向配置示例：
                # 允许重定向
                api_data = {
                    "allowRedirects": "true"
                }
                # 处理后：self.others["allow_redirects"] = True
                
                # 禁止重定向
                api_data = {
                    "allowRedirects": "false"
                }
                # 处理后：self.others["allow_redirects"] = False
                
                # 未配置重定向
                api_data = {}
                # 处理后：self.others["allow_redirects"] = None
        """
        pass

    def collect_hooks(self, api_data):
        """
            收集请求钩子配置
            
            配置请求和响应的钩子函数。当前实现为空，可根据需要扩展。
            
            Args:
                api_data (dict): API数据字典
            
            ### 钩子函数配置格式示例：
                api_data = {
                    "hooks": {
                        "pre_request": [
                            {
                                "name": "add_timestamp",
                                "code": "request.headers['X-Timestamp'] = str(int(time.time()))",
                                "params": {"names": ["request"], "types": ["object"]}
                            }
                        ],
                        "post_response": [
                            {
                                "name": "log_response",
                                "code": "print(f'Response status: {response.status_code}')",
                                "params": {"names": ["response"], "types": ["object"]}
                            }
                        ]
                    }
                }
                
                # 处理后：self.others["hooks"] = {
                #     "pre_request": [callable_function1],
                #     "post_response": [callable_function2]
                # }
        """
        pass

    def collect_cert(self, api_data):
        """
            收集客户端证书配置
            
            配置客户端SSL证书路径。当前实现为空，可根据需要扩展。
            
            Args:
                api_data (dict): API数据字典
            
            ### 客户端证书配置示例：
                # 单个证书文件
                api_data = {
                    "cert": "/path/to/client.pem"
                }
                # 处理后：self.others["cert"] = "/path/to/client.pem"
                
                # 证书和私钥分离
                api_data = {
                    "cert": {
                        "cert_file": "/path/to/client.crt",
                        "key_file": "/path/to/client.key"
                    }
                }
                # 处理后：self.others["cert"] = ("/path/to/client.crt", "/path/to/client.key")
                
                # 带密码的私钥
                api_data = {
                    "cert": {
                        "cert_file": "/path/to/client.crt",
                        "key_file": "/path/to/client.key",
                        "password": "key_password"
                    }
                }
                # 处理后：self.others["cert"] = ("/path/to/client.crt", "/path/to/client.key", "key_password")
        """
        pass

    def collect_assertions(self, api_data):
        """
            收集断言配置
            
            收集API响应的断言规则，用于验证响应结果是否符合预期。
            断言配置以JSON格式存储在controller的assertions字段中。
            
            Args:
                api_data (dict): API数据字典
            
            ### 断言配置格式示例：
                [
                    {
                        "source": "response",          # 数据来源：response(响应数据)
                        "property": "status_code",     # 属性路径
                        "operation": "eq",            # 比较操作：eq(等于)
                        "value": 200,                 # 期望值
                        "message": "状态码应为200"      # 断言失败消息
                    },
                    {
                        "source": "response",
                        "property": "body.code",       # JSON路径
                        "operation": "eq",
                        "value": 0,
                        "message": "响应码应为0"
                    },
                    {
                        "source": "response",
                        "property": "body.data.user.name",
                        "operation": "contains",       # 包含操作
                        "value": "张",
                        "message": "用户名应包含'张'字"
                    },
                    {
                        "source": "response",
                        "property": "headers.Content-Type",
                        "operation": "eq",
                        "value": "application/json",
                        "message": "响应类型应为JSON"
                    }
                ]
        """
        self.collect_context(api_data, "assertions")

    def collect_relations(self, api_data):
        """
            收集关联数据配置
            
            收集API响应的关联数据提取规则，用于从响应中提取数据供后续请求使用。
            关联配置以JSON格式存储在controller的relations字段中。
            
            Args:
                api_data (dict): API数据字典
            
            ### 关联数据配置格式示例：
                [
                    {
                        "source": "response",          # 数据来源：response(响应数据)
                        "property": "body.token",      # 提取路径
                        "variable": "auth_token",      # 保存到的变量名
                        "expression": "jsonpath"       # 提取表达式类型
                    },
                    {
                        "source": "response",
                        "property": "body.data.user.id",
                        "variable": "current_user_id",
                        "expression": "jsonpath"
                    },
                    {
                        "source": "response",
                        "property": "headers.Set-Cookie",
                        "variable": "session_cookie",
                        "expression": "regex",         # 正则表达式提取
                        "pattern": "sessionid=([^;]+)" # 正则表达式模式
                    },
                    {
                        "source": "request",           # 从请求数据提取
                        "property": "body.username",
                        "variable": "last_username",
                        "expression": "jsonpath"
                    },
                    {
                        "source": "response",
                        "property": "body.data.list",
                        "variable": "user_list",
                        "expression": "jsonpath",
                        "index": 0                     # 提取数组第一个元素
                    }
                ]
        """
        self.collect_context(api_data, "relations")

    def collect(self, api_data):
        """
            执行完整的API数据收集流程
            
            按照固定顺序收集所有API请求相关的数据，包括基本信息、请求参数、
            控制配置、断言和关联等。这是该类的主要入口方法。
            
            Args:
                api_data (dict): 完整的API数据字典
                
            ### Example:
                api_data = {
                    "apiId": "user_login_001",
                    "apiName": "用户登录接口",
                    "protocol": "HTTP",
                    "method": "POST",
                    "url": "https://api.example.com",
                    "path": "/auth/login",
                    "rest": {},
                    "query": {},
                    "headers": {
                        "Content-Type": "application/json",
                        "User-Agent": "TestClient/1.0"
                    },
                    "body": {
                        "type": "json",
                        "json": '{"username": "${username}", "password": "${password}"}'
                    },
                    "controller": {
                        "timeout": 30,
                        "useSession": "true",
                        "errorContinue": "false"
                    },
                    "assertions": [
                        {
                            "source": "response",
                            "property": "status_code",
                            "operation": "eq",
                            "value": 200
                        }
                    ],
                    "relations": [
                        {
                            "source": "response",
                            "property": "body.token",
                            "variable": "auth_token"
                        }
                    ]
                }
                
                collector = ApiRequestCollector()
                collector.collect(api_data)
                
                # 收集结果
                # collector.apiId = "user_login_001"
                # collector.method = "POST"
                # collector.url = "https://api.example.com"
                # collector.path = "/auth/login"
                # collector.others = {
                #     "headers": {"Content-Type": "application/json", "User-Agent": "TestClient/1.0"},
                #     "json": {"username": "${username}", "password": "${password}"},
                #     "timeout": 30
                # }
            
            ### 收集顺序：
                1. 基本信息：ID、名称、协议、方法、URL、路径
                2. 控制配置：控制器、条件、循环器
                3. 请求参数：查询参数、请求头、Cookie、代理、请求体
                4. 请求选项：流传输、SSL验证、认证、超时、重定向、钩子、证书
                5. 测试配置：断言、关联
                
            ### Raises:
                UnDefinableMethodError: 当请求方法未定义时
                UnDefinablePathError: 当URL或路径未设置时
                NotExistedFieldError: 当必需字段不存在时
                NotExistedFileUploadType: 当文件上传类型不存在时
        """
        # 收集基本信息
        self.collect_id(api_data)           # 收集后为self.apiId        // 通过collect_flag（）的setattr设置添加
        self.collect_name(api_data)         # 收集后为self.name         // 通过collect_flag（）的setattr设置添加
        self.collect_protocol(api_data)     # 收集后为self.protocol     // 通过collect_flag（）的setattr设置添加
        self.collect_method(api_data)       # 收集后为self.method
        self.collect_url(api_data)          # 收集后为self.path
        self.collect_path(api_data)         # 收集后为self.path         // example：/api/users/{{user_name}}
        
        # 收集控制配置
        self.collect_controller(api_data)   # 收集后为self.controller["sleepBeforeRun" | "sleepAfterRun" | "useSession" | "saveSession" | "pre" | "post" | "errorContinue"]
        self.collect_conditions(api_data)   # 收集后为self.conditions
        self.collect_looper(api_data)       # 收集后为self.looper
        
        # 收集请求参数
        self.collect_query(api_data)        # 收集后为self.other["params"]
        self.collect_headers(api_data)      # 收集后为self.other["headers"]
        self.collect_cookies(api_data)      # 收集后为self.other["headers"]["cookies"]
        self.collect_proxies(api_data)      # 收集后为self.other["proxies"]
        self.collect_body(api_data)         # 收集后为self.other["json"]、self.other["data"]、self.other["files"]
        
        # 收集请求选项
        self.collect_stream(api_data)       # 收集后为self.other["stream"]
        self.collect_verify(api_data)       # 收集后为self.other["verify"]
        self.collect_timeout(api_data)      # 收集后为self.other["timeout"]
        self.collect_auth(api_data)         # 未实现，收集身份认证配置
        self.collect_allow_redirects(api_data)  # 未实现，收集重定向配置
        self.collect_hooks(api_data)        # 未实现，收集请求前后置钩子
        self.collect_cert(api_data)         # 未实现，收集客户端证书配置
        
        # 收集测试配置
        self.collect_assertions(api_data)   # 收集后为self.assertions
        self.collect_relations(api_data)    # 收集后为self.relations


class UnDefinableMethodError(Exception):
    """
        请求方法未定义异常
        
        当API接口的HTTP请求方法（GET、POST、PUT等）未定义或为空时抛出此异常。
        
        Attributes:
            message (str): 异常信息
        
        Example:
            >>> raise UnDefinableMethodError("接口123未定义请求方法")
    """
    pass


class UnDefinablePathError(Exception):
    """
        请求路径未定义异常
        
        当API接口的URL或请求路径未设置时抛出此异常。
        
        Attributes:
            message (str): 异常信息
        
        Example:
            >>> raise UnDefinablePathError("接口123未设置域名")
    """
    pass


class NotExistedFieldError(Exception):
    """
        必需字段不存在异常
        
        当API数据中缺少必需的字段或字段值为空时抛出此异常。
        
        Attributes:
            message (str): 异常信息
        
        Example:
            >>> raise NotExistedFieldError("接口数据apiId字段不存在或为空")
    """
    pass


class NotExistedFileUploadType(Exception):
    """
        文件上传类型不存在异常
        
        当文件上传配置中指定的文件类型不存在或不支持时抛出此异常。
        
        Attributes:
            message (str): 异常信息
        
        Example:
            >>> raise NotExistedFileUploadType("不支持的文件上传类型：unknown")
    """
    pass
