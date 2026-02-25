# -*- coding: utf-8 -*-

import datetime
import time
import os
import shutil           # 高级文件操作：目录树删除和文件移动

from app.api import LMApi
from app.log import DebugLogger, ErrorLogger
from app.config import DATA_PATH


class LMReport(object):
    """
        测试结果报告处理类。
        
        负责监控测试用例执行结果，将结果上传到测试平台，
        并在任务完成后进行清理工作。
    """
    
    def __init__(self, message_queue, case_result_queue):
        """
            初始化报告处理器。
            
            Args:
                message_queue (Queue): 消息队列，用于与任务管理器通信
                case_result_queue (Queue): 用例结果队列，接收测试执行结果
        """
        self.case_result_queue = case_result_queue  # 用例结果队列
        self.message_queue = message_queue  # 消息队列
        self.api = LMApi()  # API接口实例

    def monitor_result(self):
        """
            监控测试结果并上传到平台。
        """
        not_send_result = []  # 待发送的结果列表
        last_send_time = datetime.datetime.now()  # 上次发送时间
        
        while True:
            try:
                message = self.case_result_queue.get()
            except Exception as e:
                DebugLogger("获取执行结果报错 错误信息%s" % str(e))
            else:
                # 处理字符串类型的控制消息
                if isinstance(message, str):
                    # run_all_start
                    if "run_all_start" in message:
                        # 解析任务启动消息
                        task_id = message.split("--")[1]
                        data_type = message.split("--")[-1]     # 这里其实并没有实现（BUG）
                        DebugLogger("任务执行启动 开始监听执行结果 任务id: %s" % task_id)

                    # run_all_stop
                    elif "run_all_stop" in message:
                        # 任务结束，上传剩余结果并清理
                        if len(not_send_result) != 0:
                            self.api.upload_result(task_id, data_type, not_send_result)
                        self.post_stop(task_id)  # 执行结束清理

                        # 通知任务管理器任务完成
                        self.message_queue.put({"type": "completed", "data": task_id})
                        time.sleep(2)
                        break

                    # 处理重试执行消息 start_run_index--n
                    else:
                        # 上传当前批次结果
                        if len(not_send_result) != 0:
                            self.api.upload_result(task_id, data_type, not_send_result)
                            not_send_result.clear()
                        index = int(message.split("--")[-1])
                        if index > 0:
                            DebugLogger("用例有执行错误 重试执行 任务id: %s" % task_id)

                # 处理测试结果数据，控制上传频率
                else:
                    result = message
                    not_send_result.append(result)
                    current_time = datetime.datetime.now()

                    # 计算发送的时间间隔
                    during = (current_time - last_send_time).seconds
                    if during < 3:
                        pass  # 间隔小于3秒，继续累积结果
                    else:
                        # 达到发送间隔，上传结果
                        self.api.upload_result(task_id, data_type, not_send_result)
                        last_send_time = current_time
                        not_send_result.clear()

    def post_stop(self, task_id=None):
        DebugLogger("任务结束 调用接口通知平台 任务id: %s" % task_id)

        # 调用API通知平台任务完成
        self.api.complete_task(task_id)

        # 清理本地测试数据目录
        data = os.path.join(DATA_PATH, str(task_id))
        if os.path.exists(data):
            try:
                shutil.rmtree(data)  # 递归删除整个目录树
            except Exception as e:
                ErrorLogger("删除测试数据失败 失败原因：%s 任务id: %s" % (str(e), task_id))
