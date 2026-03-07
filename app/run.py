# -*- coding: utf-8 -*-
"""
测试执行器模块

支持两种执行模式：
    1. Pytest模式：API测试，使用pytest框架执行
    2. Unittest模式：Web/App测试，使用原有unittest框架执行

设计说明：
    - 根据test_type自动选择执行模式
    - 保持向后兼容，Web/App测试不受影响
    - API测试使用pytest，支持插件扩展
    - Pytest模式下仍使用原有result.py进行结果回传，确保平台推送功能正常
"""

import unittest
import pytest
import threading
import os
import sys
import datetime
from app import case, result
from app.log import ErrorLogger, DebugLogger
from app.config import LMConfig


class LMRun(object):
    """
    测试执行器类。

    负责根据测试计划执行测试用例，支持多线程并发执行，
    并将执行结果通过队列传递给结果处理器。

    支持两种执行模式：
        - Pytest模式：test_type为API时使用
        - Unittest模式：test_type为WEB/APP时使用
    """

    def __init__(self, test_case_list, run_index, default_result, default_lock, queue):
        """
            初始化测试执行器。

            Args:
                plan_tuple (list): 测试计划列表，包含要执行的测试用例信息
                run_index (int): 当前执行轮次索引
                default_result (list): 共享的结果列表
                default_lock (threading.Lock): 线程锁，确保多线程环境下的数据安全
                queue (Queue): 结果队列，用于传递测试结果
        """
        self.test_case_tuple = test_case_list    # 一个测试集合
        self.run_index = run_index      # 执行轮次索引
        self.default_result = default_result    # 共享结果列表
        self.default_lock = default_lock        # 线程锁
        self.queue = queue          # 结果队列
        self.config = LMConfig()    # 配置对象
        self.task_id = ""           # 任务ID，用于结果回传

    def run_test(self):
        """
        执行测试的主入口方法

        根据测试类型自动选择执行模式：
            - API类型：使用Pytest执行
            - WEB/APP类型：使用Unittest执行（原有逻辑）
        """
        # 检查测试类型，确定执行模式
        test_types = set(case.get("test_type", "API") for case in self.test_case_tuple)

        # 获取task_id用于结果回传
        if self.test_case_tuple:
            self.task_id = self.test_case_tuple[0].get("task_id", "")

        if len(test_types) == 1 and "API" in test_types:
            self._run_with_pytest()
        else:
            self._run_with_unittest()

    def _run_with_pytest(self):
        """
        使用Pytest执行API测试

        调用pytest API执行测试，支持插件扩展。
        结果通过result queue回传给平台（原有机制）。
        """
        # 准备测试目录和数据
        test_dirs = set()
        for case in self.test_case_tuple:
            case_data_path = case.get("test_data", "")
            if case_data_path and os.path.exists(case_data_path):
                test_dirs.add(os.path.dirname(case_data_path))

        if not test_dirs:
            ErrorLogger("No valid test data found for pytest execution")
            return

        # 获取测试数据目录
        test_dir = list(test_dirs)[0]

        # 构建pytest参数
        pytest_args = [
            "-v",
            "--tb=short",
            "--strict-markers",
            "-p", "app.pytest_hooks",  # 加载自定义钩子
            test_dir
        ]

        # 创建自定义结果处理器（确保平台推送正常）
        res = result.Result(self.default_result, self.default_lock, self.queue)

        # 执行pytest
        try:
            DebugLogger(f"Running pytest with args: {pytest_args}")

            # 使用pytest的内部API执行，这样可以更好地集成result
            # 注意：这里我们让pytest直接执行，不使用unittest的result机制
            # 因为我们使用pytest_hooks中的钩子来收集结果
            exit_code = pytest.main(pytest_args)

            # 根据退出码记录日志
            if exit_code == 0:
                DebugLogger("Pytest execution completed successfully")
            else:
                DebugLogger(f"Pytest execution finished with exit code: {exit_code}")

        except Exception as e:
            ErrorLogger(f"Failed to run pytest: {str(e)}")
            # 降级到unittest执行
            self._run_with_unittest()

    def _run_with_unittest(self):
        """
        使用Unittest执行WEB/APP测试

        这是原有的执行逻辑，保持不变。
        """
        suite = unittest.TestSuite()

        # 遍历测试计划，构建测试用例
        for case in self.test_case_tuple:
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


class PytestResultCollector:
    """
    Pytest结果收集器

    用于在Pytest执行模式下，将测试结果转换为平台要求的格式，
    并通过queue回传给平台。

    这个类作为result.py的补充，确保Pytest模式下的结果能正确回传。
    """

    @staticmethod
    def convert_to_platform_format(pytest_result, case_info, task_id):
        """
        将Pytest测试结果转换为平台格式

        Args:
            pytest_result: pytest的测试结果对象
            case_info: 用例信息字典
            task_id: 任务ID

        Returns:
            dict: 平台格式的测试结果
        """
        # 根据pytest结果状态转换为平台状态码
        # 0=成功, 1=失败, 2=错误, 3=跳过
        status_map = {
            "passed": 0,
            "failed": 1,
            "error": 2,
            "skipped": 3
        }

        status = status_map.get(pytest_result.outcome, 0)

        # 构建平台格式的结果
        platform_result = {
            "status": status,
            "caseId": case_info.get("case_id", ""),
            "caseName": case_info.get("case_name", ""),
            "caseType": case_info.get("case_type", "API"),
            "collectionId": "",
            "index": case_info.get("index", 0),
            "runTimes": 1,
            "startTime": int(datetime.datetime.now().timestamp() * 1000),
            "endTime": int(datetime.datetime.now().timestamp() * 1000),
            "transactionList": case_info.get("trans_list", [])
        }

        return platform_result

    @staticmethod
    def push_to_queue(platform_result, queue, default_result, lock):
        """
        将结果推送到队列

        Args:
            platform_result: 平台格式的测试结果
            queue: 结果队列
            default_result: 共享结果列表
            lock: 线程锁
        """
        if lock.acquire():
            default_result.append(platform_result)
            queue.put(platform_result)
            lock.release()
