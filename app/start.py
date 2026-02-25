#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import threading
from multiprocessing import Process, Queue, Value

import psutil  # 进程管理

from app.api import LMApi
from app.config import LOG_PATH, IMAGE_PATH, LMConfig
from app.log import DebugLogger, ErrorLogger
from app.report import LMReport
from app.setting import LMSetting
from app.upload import LMUpload
from app.ws import Client


class Start(object):
    """
        测试引擎核心启动

        负责引擎的初始化、多进程管理、任务调度和WebSocket通信
    """

    def __init__(self):
        # 创建API通信客户端，用于与测试平台进行HTTP/WebSocket通信
        self.api = LMApi()

        # 加载引擎配置信息，包括平台地址、引擎编码、密钥等
        self.config = LMConfig()

        # 初始化执行进程管理字典，用于跟踪和管理正在执行的任务进程;
        # 示例: {task_id: [run_process, report_process, upload_process]}
        self.exec_processes = {}

    def main(self):
        """
            引擎主入口方法
            
            启动多线程和多进程架构，包括心跳监控、任务调度和测试执行等功能
        """
        # 创建消息队列，用于线程间传递控制消息（启动、停止、完成等）
        message_queue = Queue()

        # 启动心跳线程，维持与测试平台的WebSocket连接
        status_thread = threading.Thread(target=self.send_heartbeat, args=(message_queue,))
        status_thread.start()

        # 创建任务队列，用于存储从平台拉取的待执行任务
        task_queue = Queue()

        # 启动任务拉取线程，定时从平台获取新的测试任务
        task_thread = threading.Thread(target=self.fetch_task, args=(task_queue,))
        task_thread.start()  # 初始化一次任务拉取，避免任务遗漏

        # 启动消息监控线程，处理平台下发的控制指令（启动、停止任务等）
        monitor_thread = threading.Thread(target=self.monitor_message, args=(message_queue, task_queue))
        monitor_thread.start()

        # 主循环：持续监听任务队列，为每个任务创建执行进程组
        while True:
            try:
                # 从任务队列获取任务，设置1秒超时避免无限阻塞
                task = task_queue.get(True, 1)
            except:
                # 队列为空或超时，继续下一次循环
                continue
            else:
                # 成功获取任务，记录日志并启动执行进程组
                DebugLogger("接受任务成功 启动执行进程 任务id: %s" % task["taskId"])

                # 创建用例结果队列，用于测试执行进程向结果上报进程传递数据
                case_result_queue = Queue()

                # 创建共享执行状态变量：0-执行中，1-执行结束
                current_exec_status = Value("i", 0)

                # 创建测试执行进程，负责具体的测试用例执行
                run_process = Process(target=self.run_test, args=(task, case_result_queue, current_exec_status))
                run_process.start()

                # 创建结果上报进程，负责将测试结果实时上报到平台
                report_process = Process(target=self.push_result, args=(message_queue, case_result_queue))
                report_process.start()

                # 创建图片上传进程，负责上传测试过程中产生的截图文件
                upload_process = Process(target=self.upload_image, args=(task, current_exec_status))
                upload_process.start()

                # 将进程组保存到管理字典中，便于后续的进程控制和资源管理
                self.exec_processes[task["taskId"]] = [run_process, report_process, upload_process]

    def send_heartbeat(self, queue):
        """
            通过WebSocket连接维持与平台的实时通信，每30秒发送一次心跳
            
            Args:
                queue: 消息队列，用于接收平台下发的控制指令
        """

        while True:
            # 设置心跳状态日志文件路径
            log_path = os.path.join(LOG_PATH, "engine_status.log")

            # 处理配置URL，确保格式正确（移除末尾斜杠）
            domain = self.config.url[:-1] if self.config.url.endswith("/") else self.config.url

            # 构建WebSocket心跳连接URL，将HTTP协议替换为WS协议
            # 包含引擎编码和密钥作为认证参数
            url = domain.replace("http", "ws") + "/websocket/engine/heartbeat?engineCode={}&engineSecret={}". \
                format(self.config.engine, self.config.secret)

            try:
                # 创建WebSocket客户端实例，传入消息队列用于双向通信
                ws = Client(url, queue)

                # 建立WebSocket连接到测试平台
                ws.connect()

                # 心跳发送循环
                while True:
                    # 等待30秒后发送下一次心跳
                    time.sleep(30)

                    # 发送心跳数据包（空字节数据）
                    ws.send(bytes(0))  # 每隔30秒更新心跳

                    # 记录心跳成功日志，使用分隔线便于查看
                    DebugLogger("-------------------------------------------------", file_path=log_path)
                    DebugLogger("心跳更新成功", file_path=log_path)
                    DebugLogger("-------------------------------------------------", file_path=log_path)

            except KeyboardInterrupt:
                # 捕获键盘中断信号（Ctrl+C），优雅关闭连接
                ws.close()

            except Exception as e:
                # 捕获所有其他异常，记录错误信息并准备重连
                DebugLogger("-------------------------------------------------", file_path=log_path)
                ErrorLogger("心跳连接失败 1秒钟后重试 失败原因:%s" % e, file_path=log_path)
                DebugLogger("-------------------------------------------------", file_path=log_path)

            # 连接失败后等待1秒再重试，避免频繁重连占用资源
            time.sleep(1)

    def fetch_task(self, queue):
        """
            从测试平台拉取待执行任务，根据引擎最大并发数限制，定时获取新的测试任务

            Args:
                queue: 任务队列，用于存储获取到的任务
        """

        while True:
            # 检查当前执行进程数量是否小于配置的最大并发数
            if len(self.exec_processes) < int(self.config.max_run):
                # 通过API客户端从平台拉取新的测试任务（请求任务接口的响应数据的data字段）
                task = self.api.fetch_task()

                # 检查是否成功获取到任务
                if task:
                    # 为新任务初始化空的进程列表，用于后续存储执行进程
                    self.exec_processes[task["taskId"]] = []

                    # 记录任务获取成功的日志信息
                    DebugLogger("引擎获取任务成功 任务id: %s" % (task["taskId"]))

                    # 将任务放入队列，等待主循环创建执行进程
                    queue.put(task)
                else:
                    # 没有可执行任务时停止获取，避免无效轮询
                    break
            else:
                # 当前执行进程数已达到最大限制，等待3秒后重试
                # 这样可以在有进程结束后及时获取新任务
                time.sleep(3)

    def monitor_message(self, message_queue, task_queue):
        """
            监控WebSocket消息队列
            
            处理平台下发的控制指令，包括启动任务、停止任务等
            
            Args:
                message_queue: WebSocket消息队列
                task_queue: 任务队列，用于触发新任务拉取
        """

        while True:
            try:
                # 从消息队列获取控制指令，设置0.1秒超时避免长时间阻塞
                message = message_queue.get(True, 0.1)
            except:
                # 队列为空或超时，继续下一次监听循环
                continue
            else:
                # 处理启动指令：创建新的任务拉取线程
                if message["type"] == "start":
                    task_thread = threading.Thread(target=self.fetch_task, args=(task_queue,))
                    task_thread.start()

                # 处理停止指令：终止指定任务的所有相关进程
                elif message["type"] == "stop":
                    # 检查任务是否存在于执行进程字典中
                    if message["data"] in self.exec_processes:
                        # 获取任务对应的进程列表
                        processes = self.exec_processes[message["data"]]

                        # 遍历任务对应的所有进程（执行、上报、上传）
                        for process in processes:
                            # 检查进程是否仍在运行
                            if process.is_alive():
                                # 安全终止进程
                                process.terminate()

                        # 从进程字典中删除任务记录，释放内存
                        del self.exec_processes[message["data"]]
                        DebugLogger("引擎终止任务成功 任务id: %s" % message["data"])

                # 处理停止所有任务指令：终止所有正在执行的任务
                elif message["type"] == "stopAll":
                    # 遍历所有执行中的任务
                    for task_id, processes in self.exec_processes.items():
                        # 终止每个任务的所有进程
                        for process in processes:
                            if process.is_alive():
                                process.terminate()
                        DebugLogger("引擎终止任务成功 任务id: %s" % task_id)

                    # 清空所有进程记录
                    self.exec_processes.clear()

                else:  # completed - 任务完成指令
                    # 任务正常完成，清理进程记录
                    if message["data"] in self.exec_processes:
                        del self.exec_processes[message["data"]]

    @staticmethod
    def run_test(task, queue, current_exec_status):
        """
            执行测试任务
            
            解析任务配置，创建测试执行计划并启动多线程执行
            
            Args:
                task: 测试任务配置信息
                queue: 用例结果队列，用于传递测试结果
                current_exec_status: 共享变量，标记执行状态
        """
        # 创建任务设置实例，用于解析和处理测试任务
        s = LMSetting(task)

        # 分析任务内容，生成详细的测试执行计划
        plan = s.task_analysis()

        # 根据执行计划创建多线程执行测试用例
        # 测试结果会通过queue传递给结果上报进程
        s.create_thread(plan, queue, current_exec_status)

    @staticmethod
    def push_result(message_queue, case_result_queue):
        """
            推送测试结果到平台
            
            监控结果队列，实时将测试结果上报到测试平台
            
            Args:
                message_queue: WebSocket消息队列
                case_result_queue: 测试结果队列
        """
        # 创建结果处理实例，传入消息队列和结果队列
        report = LMReport(message_queue, case_result_queue)

        # 开始结果监控主循环，持续处理队列中的结果并推送到平台
        report.monitor_result()

    @staticmethod
    def upload_image(task, current_exec_status):
        """
            上传测试截图文件
            
            监控任务截图目录，实时上传新生成的截图文件到平台
            
            Args:
                task: 测试任务配置信息
                current_exec_status: 共享变量，标记执行状态
        """
        # 设置图片上传日志文件路径，用于记录上传过程和状态
        log_path = os.path.join(LOG_PATH, "engine_image.log")

        # 获取当前进程对象，用于监控父进程状态和进程管理
        current_process = psutil.Process(os.getpid())

        # 构建任务专用的截图存储目录路径
        task_image_path = os.path.join(IMAGE_PATH, task["taskId"])

        # 检查并创建截图存储目录
        if not os.path.exists(task_image_path):
            os.makedirs(task_image_path)

        # 文件监控主循环
        while True:
            # 检查父进程是否还存在，防止成为孤儿进程
            if current_process.parent() is None:
                current_process.kill()

            # 获取截图目录中的所有文件列表
            files = os.listdir(task_image_path)

            # 检查是否有新的截图文件需要上传
            if len(files) > 0:
                # 记录上传开始日志
                DebugLogger("-------------------------------------------------", file_path=log_path)
                DebugLogger("上传截图", file_path=log_path)

                # 创建上传实例并执行文件上传
                LMUpload(files, log_path).set_upload(task_image_path)

                # 记录上传完成日志
                DebugLogger("-------------------------------------------------", file_path=log_path)
            else:
                # 没有文件且测试已结束，清理目录并退出
                if current_exec_status.value:
                    os.rmdir(task_image_path)
                    current_process.terminate()

            # 等待1秒后进行下一次检查，避免过度占用CPU资源
            time.sleep(1)
