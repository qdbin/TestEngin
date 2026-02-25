import re  # 正则表达式模块，用于模板变量匹配
import sys  # 系统模块，用于异常信息处理

from core.api.collector import ApiRequestCollector  # API请求数据收集器
from core.template import Template  # 模板渲染引擎
from core.api.teststep import ApiTestStep, dict2str  # API测试步骤和字典转字符串工具
from jsonpath_ng.parser import JsonPathParser  # JSON路径解析器

from tools.utils.utils import get_case_message, get_json_relation, handle_params_data  # 工具函数


class ApiTestCase:
    """
        API测试用例执行器
        
        负责执行完整的API测试用例，包括多个API接口的顺序执行、循环控制、
        条件判断、模板渲染、断言验证和关联提取等功能。
        
        主要功能:
            - 测试用例数据解析和初始化
            - API接口列表的循环执行
            - 循环控制器和条件控制器处理
            - 请求参数的模板渲染
            - 前置/后置脚本和SQL执行
            - 断言结果验证和错误处理
            - 接口间的数据关联和依赖提取
        
        Attributes:
            test: 测试实例对象
            case_message (dict): 测试用例消息数据
            session: HTTP会话对象
            context (dict): 测试上下文数据
            id (str): 测试用例ID
            name (str): 测试用例名称
            functions (dict): 自定义函数集合
            params (dict): 测试参数数据
            template (Template): 模板渲染引擎实例
            json_path_parser (JsonPathParser): JSON路径解析器实例
            comp (Pattern): 模板变量匹配的正则表达式
        
        Example:
            >>> test_case = ApiTestCase(test_instance)
            >>> test_case.execute()  # 执行完整的测试用例
    """

    def __init__(self, test):
        """
            初始化API测试用例执行器
            
            解析测试用例数据，初始化各种组件和属性，为测试用例执行做准备。
            
            Args:
                test: 测试实例对象，包含测试数据、会话、上下文等信息
            
            Raises:
                KeyError: 当测试数据中缺少必要字段时
                ValueError: 当测试数据格式不正确时
        """
        self.test = test  # 保存测试实例引用
        self.case_message = get_case_message(test.test_data)  # 解析测试用例消息数据
        self.session = test.session  # HTTP会话对象，用于接口请求
        self.context = test.context  # 测试上下文，存储全局变量和状态
        self.id = self.case_message['caseId']  # 测试用例唯一标识
        self.name = self.case_message['caseName']  # 测试用例名称
        setattr(test, 'test_case_name', self.case_message['caseName'])  # 设置测试实例的用例名称属性
        setattr(test, 'test_case_desc', self.case_message['comment'])  # 设置测试实例的用例描述属性
        self.functions = self.case_message['functions']  # 自定义函数集合，用于模板渲染
        self.params = handle_params_data(self.case_message['params'])  # 处理并存储测试公共参数
        self.template = Template(self.test, self.context, self.functions, self.params)  # 初始化模板渲染引擎
        self.json_path_parser = JsonPathParser()  # JSON路径解析器，用于数据提取和更新
        self.comp = re.compile(r"\{\{.*?\}\}")  # 编译模板变量匹配的正则表达式

    def execute(self):
        """
            测试用例执行入口函数
            
            检查API列表数据的有效性，然后调用循环执行方法开始执行测试用例。
            
            Raises:
                RuntimeError: 当无法获取API相关数据时
            
            Example:
                >>> test_case = ApiTestCase(test_instance)
                >>> test_case.execute()  # 开始执行测试用例
        """
        if self.case_message['apiList'] is None:  # 检查API列表是否存在
            raise RuntimeError("无法获取API相关数据, 请重试!!!")  # 抛出运行时错误
        self.loop_execute(self.case_message['apiList'], "root")  # 从根循环开始执行API列表

    def loop_execute(self, api_list, loop_id, step_n=0):
        """
            循环执行API接口列表
            
            按顺序执行API接口列表中的每个接口，支持循环控制、条件判断、
            前后置脚本执行、断言验证等功能。处理嵌套循环和错误继续执行的逻辑。
            
            Args:
                api_list (list): API接口数据列表
                loop_id (str): 循环标识符，用于区分根循环和子循环
                step_n (int): 当前执行的步骤索引，默认为0
            
            ### API接口列表数据格式示例：
                [
                    {
                        "apiId": "api_001",
                        "apiName": "用户登录接口",
                        "method": "POST",
                        "path": "/api/login",
                        "apiDesc": "用户登录验证",
                        "looper": {
                            "type": "for",
                            "times": 3,
                            "interval": 1000
                        },
                        "conditions": [
                            {
                                "expression": "{{login_status}} == 'success'",
                                "operator": "and"
                            }
                        ],
                        "controller": {
                            "errorContinue": "true",
                            "pre": [
                                {"name": "preScript", "value": "print('执行前置脚本')"}
                            ],
                            "post": [
                                {"name": "postScript", "value": "print('执行后置脚本')"}
                            ]
                        }
                    }
                ]
            
            Note:
                - 支持循环控制器，避免循环套循环时的死循环
                - 支持条件控制器，根据条件决定是否执行接口
                - 支持错误继续执行模式，失败后可继续执行后续接口
                - 处理前置/后置脚本和SQL的执行
        """
        while step_n < len(api_list):  # 遍历API接口列表
            api_data = api_list[step_n]  # 获取当前步骤的API数据

            # 创建API请求数据收集器实例
            collector = ApiRequestCollector()

            # 创建API测试步骤实例，传入必要的依赖
            step = ApiTestStep(self.test, self.session, collector, self.context, self.params)
            # 收集循环控制器配置，依据其是否进入子循环
            step.collector.collect_looper(api_data)

            # 检查是否需要执行子循环控制
            if len(step.collector.looper) > 0 and not (loop_id != "root" and step_n == 0):
                # 非根循环且并非循环第一个接口时才执行循环，避免循环套循环的死循环
                step.looper_controller(self, api_list, step_n)  # 执行循环控制逻辑
                step_n = step_n + step.collector.looper["num"]  # 跳过本次循环中已执行的接口
                continue  # 继续下一轮循环，确保母循环能正确处理所有接口
            step_n += 1  # 递增步骤索引

            # 定义测试事务，用于结果统计和日志记录
            self.test.defineTrans(api_data['apiId'], api_data['apiName'], api_data['path'], api_data['apiDesc'])
            # 收集条件控制器配置
            step.collector.collect_conditions(api_data)
            # 检查是否配置了条件控制器
            if len(step.collector.conditions) > 0:
                result = step.condition_controller(self)  # 执行条件判断
                if result is not True:  # 条件不满足时跳过接口执行
                    self.test.updateTransStatus(3)  # 更新事务状态为跳过
                    self.test.debugLog('[{}]接口条件控制器判断为否: {}'.format(api_data['apiName'], result))
                    continue  # 跳过当前接口，继续执行下一个

            # 收集完整的API请求数据（URL、方法、参数、断言等）
            step.collector.collect(api_data)
            try:
                # 执行前置脚本和SQL语句
                if step.collector.controller["pre"] is not None:
                    for pre in step.collector.controller["pre"]:
                        if pre['name'] == 'preScript':  # 执行前置脚本
                            step.exec_script(pre["value"])
                        else:  # 执行前置SQL
                            step.exec_sql(pre["value"], self)

                # 渲染请求内容（URL、参数、请求体等模板变量替换）
                self.render_content(step)

                # 执行测试步骤：参数处理、发送请求、响应处理、断言验证、关联提取
                step.execute()

                # 执行后置脚本和SQL语句
                if step.collector.controller["post"] is not None:
                    for post in step.collector.controller["post"]:
                        if post['name'] == 'postScript':  # 执行后置脚本
                            step.exec_script(post["value"])
                        else:  # 执行后置SQL
                            step.exec_sql(post["value"], self)
                # 检查断言结果并记录日志
                if step.assert_result['result']:  # 断言成功
                    self.test.debugLog('[{}]接口断言成功: {}'.format(step.collector.apiName,
                                                                   dict2str(step.assert_result['checkMessages'])))
                else:  # 断言失败
                    self.test.errorLog('[{}]接口断言失败: {}'.format(step.collector.apiName,
                                                                   dict2str(step.assert_result['checkMessages'])))
                    raise AssertionError(dict2str(step.assert_result['checkMessages']))  # 抛出断言错误
            except Exception as e:
                error_info = sys.exc_info()  # 获取异常详细信息
                if collector.controller["errorContinue"].lower() == "true":  # 检查是否配置为错误后继续执行
                    # 根据异常类型记录不同的状态
                    if issubclass(error_info[0], AssertionError):  # 断言失败
                        self.test.recordFailStatus(error_info)
                    else:  # 其他错误（如网络错误、脚本错误等）
                        self.test.recordErrorStatus(error_info)
                else:  # 错误后停止执行
                    raise e  # 重新抛出异常，终止测试用例执行

    def render_looper(self, looper):
        """
            渲染循环控制器配置
            
            对循环控制器中的模板变量进行渲染，特别处理循环次数的类型转换。
            
            Args:
                looper (dict): 循环控制器配置数据
            
            Returns:
                dict: 渲染后的循环控制器配置
            
            Example:
                looper_config = {
                    "type": "for",
                    "times": "{{loop_count}}",
                    "interval": 1000,
                    "condition": "{{loop_condition}}"
                }
                rendered = test_case.render_looper(looper_config)
                # 返回: {"type": "for", "times": 5, "interval": 1000, "condition": "true"}
            
            ### 循环控制器配置格式示例：
                {
                    "type": "for",           # 循环类型：for/while
                    "times": "{{times}}",    # 循环次数（for循环）
                    "interval": 1000,        # 循环间隔（毫秒）
                    "condition": "{{cond}}", # 循环条件（while循环）
                    "timeout": 30000         # 超时时间（毫秒）
                }
        """
        self.template.init(looper)  # 初始化模板数据
        _looper = self.template.render()  # 执行模板渲染
        if "times" in _looper:  # 处理循环次数字段
            try:
                times = int(_looper["times"])  # 尝试转换为整数
            except:
                times = 1  # 转换失败时默认为1次
            _looper["times"] = times  # 更新循环次数
        return _looper  # 返回渲染后的配置

    def render_conditions(self, conditions):
        """
            渲染条件控制器配置
            
            对条件控制器中的模板变量进行渲染，用于条件判断。
            
            Args:
                conditions (dict): 条件控制器配置数据
            
            Returns:
                dict: 渲染后的条件控制器配置
            
            Example:
                conditions = {
                    "expression": "{{status}} == 'success'",
                    "operator": "and"
                }
                rendered = test_case.render_conditions(conditions)
                # 返回: {"expression": "200 == 'success'", "operator": "and"}
            
            ### 条件控制器配置格式示例：
                [
                    {
                        "expression": "{{response_code}} == 200",
                        "operator": "and"
                    },
                    {
                        "expression": "{{user_role}} in ['admin', 'user']",
                        "operator": "or"
                    }
                ]
        """
        self.template.init(conditions)  # 初始化模板数据
        return self.template.render()  # 执行模板渲染并返回结果

    def render_sql(self, sql):
        """
            渲染SQL语句
            
            对SQL语句中的模板变量进行渲染，用于数据库操作。
            
            Args:
                sql (str): 包含模板变量的SQL语句
            
            Returns:
                str: 渲染后的SQL语句
            
            Example:
                >>> sql = "SELECT * FROM users WHERE id = {{user_id}}"
                >>> rendered_sql = test_case.render_sql(sql)
        """
        self.template.init(sql)  # 初始化模板数据
        return self.template.render()  # 执行模板渲染并返回结果

    def render_content(self, step):
        """
            渲染请求内容的所有组成部分
            
            对API请求的各个部分（URL路径、请求头、查询参数、请求体、断言、关联）
            进行模板变量渲染。根据参数间的依赖关系确定渲染顺序，确保引用关系正确处理。
            
            Args:
                step (ApiTestStep): API测试步骤实例，包含收集器和请求数据
            
            Example:
                # 基础模板变量渲染示例
                step_data = {
                    "collector": {
                        "path": "/api/users/{{user_id}}",  # 路径参数
                        "others": {
                            "headers": {
                                "Authorization": "Bearer {{access_token}}",
                                "Content-Type": "application/json",
                                "X-Request-ID": "{{request_id}}"
                            },
                            "params": {
                                "page": "{{page_num}}",
                                "size": "{{page_size}}",
                                "filter": "{{search_filter}}"
                            },
                            "json": {
                                "user": {
                                    "name": "{{user_name}}",
                                    "email": "{{user_email}}",
                                    "profile": {
                                        "age": "{{user_age}}",
                                        "city": "{{user_city}}"
                                    }
                                },
                                "timestamp": "@current_timestamp()",
                                "request_id": "@uuid4()"
                            }
                        }
                    }
                }
                
                # 调用渲染方法
                test_case.render_content(step)
                
                # 渲染后的结果示例：
                # path: "/api/users/12345"
                # headers: {"Authorization": "Bearer abc123token", ...}
                # params: {"page": "1", "size": "20", ...}
                # json: {"user": {"name": "张三", "email": "test@example.com", ...}, ...}
            
            ### 复杂的参数间引用关系示例：
                {
                    "headers": {
                        "Content-MD5": "#{_request_body.user.profile.hash}",  # 引用请求体中的hash值
                        "X-Signature": "@md5(#{_request_body})",  # 对整个请求体计算MD5
                        "Authorization": "Bearer {{token}}"
                    },
                    "params": {
                        "user_id": "#{_request_body.user.id}",  # 引用请求体中的用户ID
                        "timestamp": "{{current_time}}"
                    },
                    "json": {
                        "user": {
                            "id": "{{user_id}}",
                            "name": "{{user_name}}",
                            "profile": {
                                "hash": "@random_string(32)",
                                "created_at": "@current_timestamp()"
                            }
                        },
                        "metadata": {
                            "request_time": "{{current_time}}",
                            "source": "api_test"
                        }
                    }
                }
                
                # 在这个例子中：
                # 1. headers中的Content-MD5引用了请求体中user.profile.hash的值
                # 2. headers中的X-Signature对整个请求体进行MD5计算
                # 3. params中的user_id引用了请求体中user.id的值
                # 4. 函数会根据这些依赖关系自动调整渲染顺序：
                #    先渲染json(body) → 再渲染params(query) → 最后渲染headers
            
            Note:
                - 处理参数间的相互引用关系（如headers引用body、query引用body等）
                - 根据引用关系动态调整渲染顺序
                - 支持不同类型的请求体（json、form-data、form-urlencoded等）
                - 设置模板辅助数据，用于参数间的相互引用

            存在问题:
                - 提取请求体的数据，貌似疏忽了files的数据
        """
        # 渲染URL路径
        self.template.init(step.collector.path)
        step.collector.path = self.template.render()
        
        # 提取请求头数据
        if step.collector.others.get('headers') is not None:
            headers = step.collector.others.pop('headers')  # 从others中移除headers
        else:
            headers = None
        
        # 提取查询参数数据
        if step.collector.others.get('params') is not None:
            query = step.collector.others.pop('params')  # 从others中移除params
        else:
            query = None
        
        # 提取请求体数据，支持data和json两种格式
        if step.collector.others.get('data') is not None:
            body = step.collector.others.pop('data')  # form-data或form-urlencoded格式
            pop_key = 'data'
        elif step.collector.others.get('json') is not None:
            body = step.collector.others.pop('json')  # JSON格式
            pop_key = 'json'
        else:
            body = None
            pop_key = None
        
        # 渲染其他请求参数（如超时、代理等）
        self.template.init(step.collector.others)
        step.collector.others = self.template.render()
        
        # 设置模板辅助数据，用于参数间的相互引用
        self.template.set_help_data(step.collector.url, step.collector.path, headers, query, body)
        
        # 根据参数间的引用关系确定渲染顺序
        # 检查headers是否引用了query或body
        if "#{_request_query" in str(headers).lower() or "#{_request_body" in str(headers).lower():
            if "#{_request_body" in str(query).lower():  # query引用body时，先渲染body
                self.render_json(step, body, "body", pop_key)
                self.render_json(step, query, "query")
                self.render_json(step, headers, "headers")
            else:  # query不引用body时，先渲染query
                self.render_json(step, query, "query")
                self.render_json(step, body, "body", pop_key)
                self.render_json(step, headers, "headers")
        else:  # headers不引用其他参数时
            if "#{_request_body" in str(query).lower():  # query引用body时
                self.render_json(step, headers, "headers")
                self.render_json(step, body, "body", pop_key)
                self.render_json(step, query, "query")
            else:  # 无相互引用时，按默认顺序渲染
                self.render_json(step, headers, "headers")
                self.render_json(step, query, "query")
                self.render_json(step, body, "body", pop_key)
        
        # 渲染断言配置
        if step.collector.assertions is not None:
            self.template.init(step.collector.assertions)
            step.collector.assertions = self.template.render()
        
        # 渲染关联提取配置
        if step.collector.relations is not None:
            self.template.init(step.collector.relations)
            step.collector.relations = self.template.render()

    def render_json(self, step, data, name, pop_key=None):
        """
            渲染JSON格式的请求数据
            
            对指定类型的请求数据进行模板变量渲染，支持深度遍历和按需渲染。
            根据数据类型和请求体格式采用不同的渲染策略，确保模板变量正确替换。
            
            Args:
                step (ApiTestStep): API测试步骤实例，包含收集器和请求配置
                data: 待渲染的数据，可以是字典、列表、字符串等格式
                name (str): 数据类型标识，可选值："headers"、"query"、"body"
                pop_key (str, optional): 请求体的键名，用于区分data和json格式
            
            Example:
                # 场景1：基础模板变量渲染
                request_body = {
                    "username": "{{user_name}}",  # 普通变量
                    "password": "{{password}}",
                    "timestamp": "{{@current_timestamp}}",  # 函数调用
                    "device_id": "{{device.uuid}}",  # 嵌套变量
                    "app_version": "1.0.0"  # 静态值
                }
                # 内部处理流程：
                # 1. get_json_relation() 扁平化数据为JSONPath格式
                # 2. 按依赖关系排序：静态值 -> 普通变量 -> 函数调用 -> 嵌套变量
                # 3. 逐个渲染并使用JsonPathParser.update()更新原数据
                test_case.render_json(step, request_body, "body")
                # 渲染结果: {"username": "admin", "password": "123456", "timestamp": "1640995200", "device_id": "ABC123", "app_version": "1.0.0"}
                
                # 场景2：复杂嵌套JSON结构渲染
                nested_data = {
                    "user": {
                        "profile": {
                            "name": "{{user_info.name}}",
                            "email": "{{user_info.email}}",
                            "avatar": "{{@random_image_url}}"
                        },
                        "preferences": {
                            "theme": "{{@random_choice(['dark', 'light'])}}",
                            "language": "{{locale}}"
                        }
                    },
                    "metadata": {
                        "request_id": "{{@uuid4}}",
                        "timestamp": "{{@current_timestamp}}",
                        "client_version": "{{app.version}}"
                    }
                }
                # 处理过程：JSONPath深度遍历，如 $.'user'.'profile'.'name'
                test_case.render_json(step, nested_data, "body")
                
                # 场景3：请求头渲染（强制字符串类型）
                headers = {
                    "Authorization": "Bearer {{access_token}}",
                    "Content-Type": "application/json",
                    "X-User-ID": "{{user_id}}",  # 数字会被转为字符串
                    "X-Timestamp": "{{@current_timestamp}}",
                    "Accept": "application/json"
                }
                test_case.render_json(step, headers, "headers")
                # 所有值都会被强制转换为字符串类型
                
                # 场景4：参数间引用（headers引用body中的数据）
                headers_with_ref = {
                    "Authorization": "Bearer {{#$.body.auth.token}}",  # 引用body中的token
                    "X-Session-ID": "{{#$.body.session_id}}",  # 引用body中的session_id
                    "Content-Type": "application/json"
                }
                # 注意：引用语法 {{#$.path}} 用于访问其他请求参数
                test_case.render_json(step, headers_with_ref, "headers")
                
                # 场景5：非JSON格式请求体（如XML、纯文本）
                xml_body = "<user><name>{{user_name}}</name><id>{{user_id}}</id></user>"
                # 对于非JSON格式，直接使用Template.render()进行字符串模板渲染
                test_case.render_json(step, xml_body, "body")  # body_type不是json时的处理方式
            
            ### JSONPath表达式和更新机制：
                # get_json_relation()函数会将嵌套数据转换为JSONPath表达式：
                # {"user": {"name": "{{value}}"}} -> [("$.user.name", "{{value}}")]
                # JsonPathParser.parse()解析表达式并创建可更新的路径对象
                # expression.update(data, new_value)在原数据结构中精确更新指定路径的值
                
                # 复杂引用处理示例
                complex_data = {
                    "signature": "@md5(#{_request_body.user.id})",  # 引用其他参数并计算MD5
                    "checksum": "@sha256(#{_request_query.timestamp})",  # 引用查询参数
                    "auth_header": "#{_request_headers.Authorization}",  # 引用请求头
                    "combined": "{{user_name}}-@random_string(8)",  # 混合使用变量和函数
                    "nested_ref": {
                        "parent_id": "#{_request_body.user.profile.id}",
                        "generated_token": "@jwt_encode({{user_claims}})"
                    }
                }
                test_case.render_json(step, complex_data, "headers")
                # 这种复杂引用会根据依赖关系确定渲染顺序
            
            Note:
                - 对于非结构化的请求体（如raw text），直接进行整体渲染
                - 对于结构化数据，使用JSONPath进行深度遍历和按需渲染
                - 请求头的值会强制转换为字符串类型
                - 渲染后的数据会更新到模板引擎的辅助数据中，供其他参数引用
        """
        if data is None:  # 数据为空时直接返回
            return
        
        # 对于非结构化的请求体，进行整体渲染
        if name == "body" and step.collector.body_type not in ("json", "form-urlencoded", "form-data"):
            self.template.init(data)  # 初始化模板数据
            render_value = self.template.render()  # 执行整体渲染
            self.template.request_body = render_value  # 更新模板辅助数据
        else:
            # 对于结构化数据，使用JSONPath进行深度遍历和按需渲染
            for expr, value in get_json_relation(data, name):
                # 检查值是否为字符串且包含模板变量
                if isinstance(value, str) and self.comp.search(value) is not None:
                    self.template.init(value)  # 初始化单个值的模板
                    render_value = self.template.render()  # 渲染单个值
                    
                    # 请求头的值必须是字符串类型
                    if name == "headers":
                        render_value = str(render_value)
                    
                    # 使用JSONPath更新原始数据中的对应位置
                    expression = self.json_path_parser.parse(expr)
                    expression.update(data, render_value)
                    
                    # 更新模板引擎的辅助数据，供其他参数引用
                    if name == "body":
                        self.template.request_body = data
                    elif name == "query":
                        self.template.request_query = data
                    else:
                        self.template.request_headers = data
        
        # 将渲染后的数据重新设置到测试步骤收集器中
        if name == "body":
            step.collector.others.setdefault(pop_key, self.template.request_body)
        elif name == "query":
            step.collector.others.setdefault("params", self.template.request_query)
        else:
            step.collector.others.setdefault("headers", self.template.request_headers)

