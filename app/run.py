# -*- coding: utf-8 -*-
import unittest
import threading
from app import case, result
from app.log import ErrorLogger
from app.config import LMConfig


class LMRun(object):
    """
    测试执行器类。
    
    负责根据测试计划执行测试用例，支持多线程并发执行，
    并将执行结果通过队列传递给结果处理器。
    """
    
    def __init__(self, plan_tuple, run_index, default_result, default_lock, queue):
        """
            初始化测试执行器。
            
            Args:
                plan_tuple (list): 测试计划列表，包含要执行的测试用例信息
                run_index (int): 当前执行轮次索引
                default_result (list): 共享的结果列表
                default_lock (threading.Lock): 线程锁，确保多线程环境下的数据安全
                queue (Queue): 结果队列，用于传递测试结果
        """
        self.plan_tuple = plan_tuple  # 测试计划元组
        self.run_index = run_index  # 执行轮次索引
        self.default_result = default_result  # 共享结果列表
        self.default_lock = default_lock  # 线程锁
        self.queue = queue  # 结果队列

    def run_test(self):

        suite = unittest.TestSuite()  # 创建测试套件
        
        # 遍历测试计划，构建测试用例
        for case in self.plan_tuple:
            cls_name = case["test_class"]  # 获取测试类名
            try:
                # 获取已存在的测试类
                cls = eval(cls_name)
            except:
                """
                    # 如果类不存在，动态创建继承自LMCase的测试类; 等价于手动定义：
                    class UserLoginTest(lm_case.LMCase):
                        '''UserLoginTest'''
                        pass
                """
                cls = type(cls_name, (case.LMCase,), {'__doc__': cls_name})
            
            case_name = case["test_case"]  # 测试用例名称
            case_type = case["test_type"]  # 测试类型(API/WEB/APP)
            
            # 动态设置测试方法，指向LMCase的testEntrance方法
            setattr(cls, case_name, case.LMCase.testEntrance)
            
            case_data = case["test_data"]  # 测试数据

            # 创建测试用例实例
            test_case = cls(case_name, case_data, case_type)
            
            # 设置测试用例的运行时属性
            test_case.task_id = case["task_id"]     # 任务ID
            test_case.driver = case["driver"]       # 浏览器驱动或设备连接
            test_case.session = case["session"]     # 会话对象
            test_case.context = case["context"]     # 上下文信息
            test_case.run_index = self.run_index    # 执行轮次
            
            suite.addTest(test_case)

        # 创建自定义结果处理器
        res = result.Result(self.default_result, self.default_lock, self.queue)

        try:
            suite(res)  # 执行测试套件
        except Exception as ex:
            ErrorLogger("Failed to run test(RunTime:run%s & ThreadName:%s), Error info:%s" %
                        (self.run_index, threading.current_thread().name, ex))
