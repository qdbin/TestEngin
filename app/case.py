# -*- coding: utf-8 -*-
import io  # 用于字符串缓冲区操作
import os  # 文件和目录操作
import datetime  # 日期时间处理
import sys  # 系统相关功能
import time  # 时间相关功能
import unittest  # 单元测试框架
import traceback  # 异常追踪信息
from uuid import uuid1  # 生成唯一标识符
from core.api.testcase import ApiTestCase  # API测试用例执行器
from core.web.testcase import WebTestCase  # Web测试用例执行器
from core.app.testcase import AppTestCase  # App测试用例执行器
from app.config import IMAGE_PATH, LMConfig  # 配置管理和图片路径


class LMCase(unittest.TestCase):
    """
        测试用例执行类，继承自unittest.TestCase。
        
        负责管理测试用例的执行流程，包括事务管理、日志记录、截图保存和结果处理。
        支持API、Web和App三种类型的测试用例执行。
        
        使用示例:
            case = LMCase("test_login", test_data, "API")
            case.testEntrance()  # 执行测试
    """

    def __init__(self, case_name, test_data, case_type="API"):
        """
            初始化测试用例。
            
            Args:
                case_name (str): 测试用例名称
                test_data (dict): 测试数据
                case_type (str): 测试类型，可选值为API、WEB、APP
        """
        self.test_data = test_data  # 测试数据
        self.trans_list = []  # 事务列表，记录测试步骤
        self.case_name = case_name  # 测试用例名称
        self.case_type = case_type  # 测试类型
        unittest.TestCase.__init__(self, case_name)

    def testEntrance(self):
        """
            测试用例执行入口。
            
            根据测试类型选择对应的测试执行器进行测试。
        """
        # 根据测试类型选择对应的执行器
        if self.case_type == "API":
            ApiTestCase(test=self).execute()
        elif self.case_type == "WEB":
            WebTestCase(test=self).execute()
        else:
            AppTestCase(test=self).execute()

    def doCleanups(self):
        """
            测试清理方法，在测试结束后执行。
            
            调用父类清理方法并处理测试结果。
        """
        unittest.TestCase.doCleanups(self)
        self.handleResult()  # 处理测试结果

    def debugLog(self, log_info):
        """
            记录调试日志到当前事务。
            
            Args:
                log_info (str): 日志信息
        """
        if len(self.trans_list) > 0:
            current_time = datetime.datetime.now()
            # 格式化日志时间戳
            log = "%s - Debug - %s" % (current_time.strftime('%Y-%m-%d %H:%M:%S.%f'), log_info)
            # 根据测试类型添加不同的换行符
            if self.trans_list[-1]["log"] != "":
                if self.case_type == "API":
                    log = "<br><br>" + log
                else:
                    log = "<br>" + log
            # 追加日志到当前事务
            self.trans_list[-1]["log"] = self.trans_list[-1]["log"] + log

    def errorLog(self, log_info):
        """
            记录错误日志到当前事务。
            
            Args:
                log_info (str): 错误信息
        """
        if len(self.trans_list) > 0:
            current_time = datetime.datetime.now()
            # 格式化错误日志时间戳
            log = "%s - Error - %s" % (current_time.strftime('%Y-%m-%d %H:%M:%S.%f'), log_info)
            # 根据测试类型添加不同的换行符
            if self.trans_list[-1]["log"] != "":
                if self.case_type == "API":
                    log = "<br><br>" + log
                else:
                    log = "<br>" + log
            # 追加错误日志到当前事务
            self.trans_list[-1]["log"] = self.trans_list[-1]["log"] + log

    def recordTransDuring(self, during):
        """
            记录当前事务的执行时长。
            
            Args:
                during (float): 事务执行时长（秒）
        """
        if len(self.trans_list) > 0:
            self.trans_list[-1]["during"] = during

    def defineTrans(self, id, name, content="", desc=None):
        """
            定义新的测试事务。
            
            Args:
                id (str): 事务ID
                name (str): 事务名称
                content (str): 事务内容
                desc (str): 事务描述
        """
        # 完成上一个事务的输出处理
        if len(self.trans_list) > 0:
            self.complete_output()
            # 如果上一个事务没有状态，设为成功
            if self.trans_list[-1]["status"] == "":
                self.trans_list[-1]["status"] = 0
        # 创建新事务字典
        trans_dict = {
            "id": id,
            "name": name,
            "content": content,
            "description": desc,
            "log": "",
            "during": 0,
            "status": "",
            "screenShotList": []
        }
        self.trans_list.append(trans_dict)

    def complete_output(self):
        """
            获取并记录控制台输出到当前事务日志。
            
            将缓冲区中的控制台输出转换为HTML格式并记录到调试日志中。
        """
        # 获取标准输出缓冲区，如果不存在则创建新的
        stdout_buffer = getattr(self, "stdout_buffer", io.StringIO())
        output = stdout_buffer.getvalue()
        stdout_buffer.truncate(0)  # 清空缓冲区
        if output:
            # 将换行符转换为HTML换行标签
            output = output.replace("\n", "<br>")
            self.debugLog("控制台输出:<br> %s" % output)

    def deleteTrans(self, index):
        """
            删除指定索引的事务。
            
            Args:
                index (int): 要删除的事务索引
        """
        if len(self.trans_list) > index:
            del self.trans_list[index]

    def updateTransStatus(self, status):
        """
        更新当前事务的状态。
        
        Args:
            status (int): 事务状态，0-成功，1-失败，2-错误，3-跳过
        """
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = status

    def recordFailStatus(self, exc_info=None):
        """
        记录断言失败状态。
        
        Args:
            exc_info (tuple): 异常信息元组
        """
        self._outcome.errors.append((self, exc_info))
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = 1  # 记录当前事务为失败
            self.errorLog(str(exc_info[1]))

    def recordErrorStatus(self, exc_info=None):
        """
        记录程序错误状态。
        
        Args:
            exc_info (tuple): 异常信息元组
        """
        self._outcome.errors.append((self, exc_info))
        if len(self.trans_list) > 0:
            self.trans_list[-1]["status"] = 2  # 记录当前事务为错误
            self.errorLog(str(exc_info[1]))
            # 如果启用了详细错误信息，记录完整的异常堆栈
            if LMConfig().enable_stderr.lower() == "true":
                # 使用TracebackException格式化异常信息
                tb_e = traceback.TracebackException(exc_info[0], exc_info[1], exc_info[2])
                msg_lines = list(tb_e.format())
                err_msg = "程序错误信息: "
                for msg in msg_lines:
                    err_msg = err_msg + "<br>" + msg
                self.errorLog(str(err_msg))

    def saveScreenShot(self, name, screen_shot):
        """
        保存测试截图到文件系统。
        
        Args:
            name (str): 截图名称
            screen_shot (bytes): 截图二进制数据
        """
        # 生成唯一的截图文件名
        uuid = time.strftime("%Y%m%d") + "_" +str(uuid1())
        task_id = getattr(self, "task_id")
        task_image_path = os.path.join(IMAGE_PATH, task_id)
        try:
            filename = "%s.png" % uuid
            # 确保目录存在
            if not os.path.exists(task_image_path):
                os.makedirs(task_image_path)
            file_path = os.path.join(task_image_path, filename)
            # 写入截图文件
            with open(file_path, 'wb') as f:
                f.write(screen_shot)
        except:
            self.errorLog("Fail: Failed to save screen shot %s" % name)
        else:
            # 将截图UUID添加到当前事务的截图列表
            if len(self.trans_list) > 0:
                self.trans_list[-1]["screenShotList"].append(uuid)

    def handleResult(self):
        """
        处理测试结果，分析错误和失败状态。
        
        分析测试执行过程中的异常信息，确定最终的测试状态，确定时失败还是异常，并记录最重要的错误信息！
        并更新事务状态和测试结果。
        """
        # 如果没有事务，创建一个默认事务
        if len(self.trans_list) == 0:
            self.defineTrans(self.case_name.split("_")[1], "未知", "未知")
        self.complete_output()
        
        # 初始化状态变量
        isFail = False
        isError = False
        error_type = None
        error_value = None
        error_tb = None     # traceback
        
        # 遍历所有错误信息，判断用例最终状态
        for index, (test, exc_info) in enumerate(self._outcome.errors):
            if exc_info is not None:
                if issubclass(exc_info[0], AssertionError):
                    isFail = True
                    # 若存在除了AssertionError的其他错误，则忽略后续的错误信息
                    if not isError:  # 错误优先级高于失败
                        error_type = AssertionError
                        error_value = exc_info[1]
                        error_tb = exc_info[2]
                else:
                    isError = True
                    error_type = exc_info[0]
                    error_value = exc_info[1]
                    error_tb = exc_info[2]
        
        # 根据用例原始成功状态处理最终结果
        if self._outcome.success is True:
            # 如果最后一个事务没有状态，设为成功
            if self.trans_list[-1]["status"] == "":
                self.trans_list[-1]["status"] = 0
            # 如果有错误或失败，清空所有错误，只保留最重要的错误，修改用例状态
            if isError or isFail:
                self._outcome.errors.clear()    # 清空所有错误
                self._outcome.errors.append((self, (error_type, error_value, error_tb)))
                self._outcome.success = False
        else:
            # 用例执行失败，处理最后一个事务的状态
            exc_info = self._outcome.errors[-2][-1]  # 获取最后一个事务的异常信息
            if issubclass(exc_info[0], AssertionError):
                self.trans_list[-1]["status"] = 1  # 设为失败
            else:
                self.errorLog(str(exc_info[1]))
                self.trans_list[-1]["status"] = 2  # 设为错误
                # 如果启用详细错误信息，记录完整堆栈
                if LMConfig().enable_stderr.lower() == "true":
                    tb_e = traceback.TracebackException(exc_info[0], exc_info[1], exc_info[2])
                    msg_lines = list(tb_e.format())
                    err_msg = "程序错误信息: "
                    for msg in msg_lines:
                        err_msg = err_msg + "<br>" + msg
                    self.errorLog(str(err_msg))
            # 清理并重新设置错误信息
            self._outcome.errors.clear()
            self._outcome.errors.append((self, (error_type, error_value, error_tb)))
