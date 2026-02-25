# -*- coding: utf-8 -*-
import datetime  # 日期时间处理模块
import io  # 输入输出流处理模块
import sys  # 系统相关功能模块
import unittest  # 单元测试框架


class Result(unittest.TestResult):
    """
        自定义测试结果处理类。
        
        继承自unittest.TestResult，用于收集和处理测试用例的执行结果，
        包括成功、失败、错误和跳过的测试用例信息，并将结果发送到队列中。
    """

    def __init__(self, result, lock, queue):
        """
            初始化测试结果处理器。
            
            Args:
                result (list): 共享的结果列表，用于存储所有测试结果
                lock (threading.Lock): 线程锁，确保多线程环境下的数据安全
                queue (Queue): 结果队列，用于实时传递测试结果
        """
        unittest.TestResult.__init__(self)
        self.stdout_buffer = None  # 标准输出缓冲区
        self.original_stdout = sys.stdout  # 原始标准输出
        self.default_result = result  # 共享结果列表
        self.default_lock = lock  # 线程锁
        self.queue = queue  # 结果队列
        self.result = []  # 当前case的结果列表(用于存放每个case的结果（success,failure,error）)

    def startTest(self, test):
        """
            测试用例开始执行时的处理。
            
            Args:
                test (unittest.TestCase): 要执行的测试用例对象
            
            设置标准输出缓冲区并记录测试开始时间。
        """
        unittest.TestResult.startTest(self, test)
        self.setupStdout()  # 设置标准输出缓冲区
        test.stdout_buffer = self.stdout_buffer  # 将缓冲区绑定到测试用例
        test.start_time = datetime.datetime.now()  # 记录测试开始时间

    def setupStdout(self):
        """
            设置标准输出缓冲区。
            
            如果缓冲区不存在，则创建一个新的StringIO对象用于捕获输出。
        """
        if self.stdout_buffer is None:
            self.stdout_buffer = io.StringIO()  # 创建字符串输入输出流

    def stopTest(self, test):
        """
            测试用例执行结束时的处理。
            
            Args:
                test (unittest.TestCase): 已执行完成的测试用例对象
            
            记录测试结束时间，构建测试结果信息并发送到队列。
        """
        unittest.TestResult.stopTest(self, test)
        test.stop_time = datetime.datetime.now()  # 记录测试结束时间
        
        # 使用线程锁确保数据安全
        if self.default_lock.acquire():
            status, test_case, error = self.result[-1]  # 获取最新的测试结果
            # 构建测试用例信息字典
            case_info = {
                "status": status,  # 测试状态：0成功，1失败，2错误，3跳过
                "startTime": test_case.start_time.timestamp()*1000,  # 开始时间戳(毫秒)
                "endTime": test_case.stop_time.timestamp()*1000,  # 结束时间戳(毫秒)
                "collectionId": test_case.__class__.__doc__.split("_")[-1],  # 用例集ID
                "caseId": getattr(test, "case_name", " _ ").split("_")[1],  # 用例ID
                "caseType": getattr(test, "case_type", "API"),  # 用例类型
                "caseName": getattr(test, "test_case_name", "未知"),  # 用例名称
                "caseDesc": getattr(test, "test_case_desc", None),  # 用例描述
                "index": int(getattr(test, "case_name", " _0").split("_")[-1]),  # 用例索引
                "runTimes": getattr(test, "run_index", 1),  # 运行次数
                "transactionList": test_case.trans_list  # 事务列表
            }
            self.default_result.append(case_info)  # 添加到共享结果列表
            self.queue.put(case_info)  # 发送到结果队列
            self.default_lock.release()  # 释放线程锁

    def restoreStdout(self):
        """
            恢复标准输出缓冲区。
            
            将缓冲区指针重置到开始位置并清空内容，
            为下一次测试用例的输出捕获做准备。
        """
        self.stdout_buffer.seek(0)  # 将指针移动到缓冲区开始位置
        self.stdout_buffer.truncate()  # 清空缓冲区内容

    def addSuccess(self, test):
        """
            处理测试成功的情况。
            
            Args:
                test (unittest.TestCase): 测试成功的用例对象
            
            将成功状态(0)记录到结果中。
        """
        unittest.TestResult.addSuccess(self, test)
        self.mergeResult(0, test, "")  # 状态码0表示成功，无错误信息

    def addFailure(self, test, err):
        """
            处理测试失败的情况。
            
            Args:
                test (unittest.TestCase): 测试失败的用例对象
                err (tuple): 异常信息元组，包含异常类型、值和追踪信息
            
            将失败状态(1)和错误信息记录到结果中。
        """
        unittest.TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]  # 获取最新的失败信息
        self.mergeResult(1, test, _exc_str)  # 状态码1表示失败

    def addError(self, test, err):
        """
            处理测试错误的情况。
            
            Args:
                test (unittest.TestCase): 发生错误的用例对象
                err (tuple): 异常信息元组，包含异常类型、值和追踪信息
            
            将错误状态(2)和错误信息记录到结果中。
        """
        unittest.TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]  # 获取最新的错误信息
        self.mergeResult(2, test, _exc_str)  # 状态码2表示错误

    def addSkip(self, test, reason):
        """
            处理测试跳过的情况。
            
            Args:
                test (unittest.TestCase): 被跳过的用例对象
                reason (str): 跳过的原因说明
            
            将跳过状态(3)和跳过原因记录到结果中。
        """
        unittest.TestResult.addSkip(self, test, reason)
        self.mergeResult(3, test, reason)  # 状态码3表示跳过

    def mergeResult(self, n, test, e):
        """
            合并测试结果信息。
            
            Args:
                n (int): 测试状态码 (0:成功, 1:失败, 2:错误, 3:跳过)
                test (unittest.TestCase): 测试用例对象
                e (str): 错误或跳过的详细信息
            
            将测试结果以元组形式添加到结果列表中。
        """
        self.result.append((n, test, e))  # 将状态、测试对象和错误信息组成元组存储
