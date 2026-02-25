#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 标准库导入
import base64  # Base64编码解码，用于文件上传时的编码转换
import requests  # HTTP请求库，用于与测试平台API通信
import time  # 时间处理，用于生成时间戳

# 项目内部模块导入
from app.config import *  # 配置管理模块，提供配置读取和路径常量
from app.log import DebugLogger, ErrorLogger  # 日志记录模块，提供调试和错误日志功能


class Api(object):
    """
        基础API通信类，提供HTTP请求和token管理功能。
        
        负责处理与测试平台的基础HTTP通信，包括POST/GET请求、
        token的保存和加载、请求头的管理等基础功能。
        
        使用示例:
            api = Api()
            api.save_token("your_token")
            response = api.request(url, data)
    """

    def __init__(self):
        # 加载引擎配置
        config = LMConfig()

        # 标准化URL
        self.url = config.url[:-1] if config.url.endswith("/") else config.url

        # 加载引擎认证信息
        self.engine = config.engine
        self.secret = config.secret

        # 初始化代理配置为空
        self.proxy = None

    def request(self, url, data):
        header = self.load_header()
        response = requests.post(url=url, json=data, headers=header, proxies=self.proxy, timeout=30)
        return response

    def download(self, url):
        """
            发送GET请求下载文件。

            Args:
                url (str): 下载URL
                
            Returns:
                requests.Response: HTTP响应对象
        """
        # 加载认证请求头
        header = self.load_header()
        # 发起流式GET请求，stream=True启用流式下载
        response = requests.get(url=url, headers=header, proxies=self.proxy, stream=True, timeout=30)
        return response

    @staticmethod
    def save_token(token):
        """
            保存访问令牌到配置文件。
            
            Args:
                token (str): 访问令牌字符串
        """
        reader = IniReader()
        DebugLogger("更新token")
        reader.modify("Header", "token", token)

    @staticmethod
    def load_header():
        # 配置读取类，读取[header]并返回
        config = LMConfig()
        header = config.header
        return header


class LMApi(Api):
    """
        测试平台API客户端类，继承自Api基类。
    """

    def apply_token(self):
        """
            申请访问令牌，保存响应头的token
        """
        url = self.url + "/openapi/engine/token/apply"
        data = {
            "engineCode": self.engine,      # 引擎唯一标识码
            "engineSecret": self.secret,    # 引擎认证密钥
            "timestamp": int(time.time()),  # 当前时间戳，用于防重放攻击
        }
        try:
            res = self.request(url=url, data=data)
            if res.status_code == 200:
                status = res.json()["status"]
                if status == 0:
                    token = res.json()["data"]
                    self.save_token(token)
                elif status == 2050:
                    DebugLogger("申请token接口 引擎id或秘钥错误")
                else:
                    DebugLogger("申请token接口 token生成失败")
            else:
                DebugLogger("调用申请token接口 响应状态为：%s" % res.status_code)
        except Exception as e:
            ErrorLogger("调用申请token接口 发生错误 错误信息为：%s" % e)

    def fetch_task(self):
        """
            获取待执行的测试任务。
            Returns:
                dict: 任务数据字典
        """
        # 构建任务获取的API端点URL
        url = self.url + "/openapi/engine/task/fetch"

        # 最多重试2次（初次请求 + 1次重试）
        for index in range(2):
            data = {
                "engineCode": self.engine,      # 引擎唯一标识码
                "timestamp": int(time.time())   # 当前时间戳
            }
            try:
                # 第二次
                if index > 0:
                    DebugLogger("-------重试调用获取引擎任务接口--------")

                res = self.request(url, data)
                if res.status_code == 200:
                    status = res.json()["status"]
                    if status == 0:
                        return res.json()["data"]
                    elif status in (2020, 2030, 2040):
                        # token校验错误状态码：2020-token无效，2030-token过期，2040-权限不足
                        DebugLogger("token校验错误 重新申请token")
                        self.apply_token()
                        continue
                    else:
                        DebugLogger("获取引擎任务请求失败")
                else:
                    DebugLogger("调用获取引擎任务接口 响应状态为：%s" % res.status_code)
            except Exception as e:
                ErrorLogger("调用获取引擎任务接口 发生错误 错误信息为：%s" % e)
            break

    def upload_result(self, task_id, data_type, result):
        """
            上传测试执行结果。
            
            Args:
                task_id (str): 任务ID
                data_type (str): 数据类型标识
                result (list): 测试用例执行结果列表
                
            Returns:
                bool: 上传成功返回True，失败返回None
        """
        # 构建结果上传的API端点URL
        url = self.url + "/openapi/engine/result/upload"
        # 最多重试2次（初次请求 + 1次重试）
        for index in range(2):
            data = {
                "engineCode": self.engine,      # 引擎唯一标识码
                "timestamp": int(time.time()),  # 当前时间戳
                "taskId": task_id,              # 任务ID
                "caseResultList": result        # 测试用例执行结果列表
            }
            try:
                # 记录重试操作
                if index > 0:
                    DebugLogger("-------重试调用上传执行结果接口--------")
                res = self.request(url, data)
                if res.status_code == 200:
                    status = res.json()["status"]
                    if status == 0:
                        return True
                    elif status in (2020, 2030, 2040):
                        DebugLogger("token校验错误 重新申请token")
                        self.apply_token()
                        continue
                    else:
                        DebugLogger("上传执行结果请求失败")
                else:
                    DebugLogger("调用上传执行结果接口 响应状态为：%s" % res.status_code)
            except Exception as e:
                ErrorLogger("调用上传执行结果接口 发生错误 错误信息为：%s" % e)
            break

    def complete_task(self, task_id):
        """
            反馈任务执行完成状态。
            
            向测试平台反馈指定任务已执行完成，用于任务状态管理。
            支持token过期时自动重新申请token并重试。
            
            Args:
                task_id (str): 已完成的任务ID
                
            Returns:
                bool: 反馈成功返回True，失败返回None
        """
        url = self.url + "/openapi/engine/task/complete"
        # 最多重试2次（初次请求 + 1次重试）
        for index in range(2):
            data = {
                "engineCode": self.engine,
                "timestamp": int(time.time()),
                "taskId": task_id
            }
            try:
                if index > 0:
                    DebugLogger("-------重试调用反馈任务结束接口--------")
                res = self.request(url, data)

                # 状态码200
                if res.status_code == 200:
                    status = res.json()["status"]
                    if status == 0:
                        return True
                    elif status in (2020, 2030, 2040):
                        DebugLogger("token校验错误 重新申请token")
                        self.apply_token()
                        continue
                    else:
                        DebugLogger("反馈任务结束请求失败")

                # HTTP状态码异常
                else:
                    DebugLogger("调用反馈任务结束接口 响应状态为：%s" % res.status_code)
            except Exception as e:
                ErrorLogger("调用反馈任务结束接口 发生错误 错误信息为：%s" % e)
            break

    def download_task_file(self, path):
        """
            下载任务相关文件。
            
            Args:
                path (str): 文件下载路径
                
            Returns:
                requests.Response: 包含文件内容的响应对象；失败返回None
        """
        # 构建完整的文件下载URL
        url = self.url + path
        # 最多重试2次
        for index in range(2):
            try:
                if index > 0:   # 第2次
                    DebugLogger("-------重试调用下载任务文件接口--------")
                # 发起文件下载请求
                res = self.download(url)

                if res.status_code == 200:
                    # 检查响应内容是否为有效的文件数据（bytes类型）
                    # 如果不是bytes类型，说明返回的是错误信息的JSON格式
                    if not isinstance(res.content, bytes):
                        status = res.json()["status"]
                        if status in (2020, 2030, 2040):
                            DebugLogger("token校验错误 重新申请token")
                            self.apply_token()
                            continue
                        else:
                            DebugLogger("下载任务文件失败")
                    else:
                        # 文件下载成功，返回响应对象
                        return res
                else:
                    DebugLogger("调用下载任务文件接口 响应状态为：%s" % res.status_code)
            except Exception as e:
                ErrorLogger("调用下载任务文件接口 发生错误 错误信息为：%s" % e)
            # 非token错误时跳出重试循环
            break

    def download_test_file(self, uuid):
        """
            根据UUID下载测试文件。
            
            使用文件UUID从测试平台下载指定的测试文件。支持token过期时
            自动重新申请token并重试。
            
            Args:
                uuid (str): 文件唯一标识符
                
            Returns:
                requests.Response: 包含文件内容的响应对象；失败返回None
        """
        # 构建测试文件下载的API端点URL
        url = self.url + "/openapi/download/test/file/" + uuid
        # 最多重试2次（初次请求 + 1次重试）
        for index in range(2):
            try:
                # 记录重试操作
                if index > 0:
                    DebugLogger("-------重试调用下载测试文件接口--------")
                # 发起文件下载请求
                res = self.download(url)
                if res.status_code == 200:
                    # 检查响应内容是否为有效的文件数据（bytes类型）
                    if not isinstance(res.content, bytes):
                        status = res.json()["status"]
                        if status in (2020, 2030, 2040):
                            DebugLogger("token校验错误 重新申请token")
                            self.apply_token()
                            continue
                        else:
                            DebugLogger("下载测试文件失败")
                    else:
                        # 文件下载成功，返回响应对象
                        return res
                else:
                    DebugLogger("调用下载测试文件接口 响应状态为：%s" % res.status_code)
            except Exception as e:
                ErrorLogger("调用下载测试文件接口 发生错误 错误信息为：%s" % e)
            # 非token错误时跳出重试循环
            break

    def upload_screen_shot(self, task_image_path, uuid, log_path):
        """
            上传测试执行截图。

            Args:
                task_image_path (str): 截图文件所在目录路径
                uuid (str): 截图文件的唯一标识符（不含扩展名）
                log_path (str): 日志文件路径，用于记录上传状态
                
            Returns:
                bool: 上传成功返回True，失败返回False
        """
        url = self.url + "/openapi/engine/screenshot/upload"
        # 最多重试2次（初次请求 + 1次重试）
        for index in range(2):
            data = {
                "fileName": "%s.png" % uuid,       # 截图文件名，使用UUID作为文件名
                "engineCode": self.engine,         # 引擎唯一标识码
                "timestamp": int(time.time())      # 当前时间戳
            }
            # 读取截图文件并进行Base64编码
            with open(os.path.join(task_image_path, "%s.png" % uuid), "rb") as f:
                # 读取二进制文件内容并转换为Base64编码字符串
                file = base64.b64encode(f.read()).decode()
                data["base64String"] = file
            try:
                # 发送截图上传请求（JSON格式包含Base64编码的文件数据）
                res = self.request(url, data)
                # 检查HTTP响应状态码
                if res.status_code == 200:
                    # 解析JSON响应数据，获取业务状态码
                    status = res.json()["status"]
                    if status == 0:
                        # 截图上传成功
                        DebugLogger("截图%s上传成功" % uuid, file_path=log_path)
                        return True
                    elif status in (2020, 2030, 2040):
                        # token校验错误，重新申请token并继续重试
                        DebugLogger("token校验错误 重新申请token", file_path=log_path)
                        self.apply_token()
                        continue
                    else:
                        # 其他业务错误
                        ErrorLogger("截图%s上传失败" % uuid, file_path=log_path)
                else:
                    # HTTP状态码异常
                    DebugLogger("调用上传截图接口 响应状态为：%s" % res.status_code, file_path=log_path)
            except Exception as e:
                ErrorLogger("调用上传截图接口 发生错误 错误信息为：%s" % e, file_path=log_path)
            # 非token错误时跳出重试循环
            break
        else:
            # 所有重试都失败，记录错误并返回False
            ErrorLogger("截图%s上传失败" % uuid, file_path=log_path)
            return False

