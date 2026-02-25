# -*- coding: utf-8 -*-

import json
import os
from ws4py.client.threadedclient import WebSocketClient
from app.config import LOG_PATH
from app.log import DebugLogger


class Client(WebSocketClient):
    """
        WebSocket客户端类
        
        Attributes:
            queue: 消息队列，用于存储接收到的平台消息
            log_path (str): 心跳状态日志文件路径
    """

    def __init__(self, url, queue):
        self.queue = queue                      # 存储消息队列引用，用于消息传递
        WebSocketClient.__init__(self, url)     # 调用父类构造函数初始化连接
        
        # 设置心跳状态日志文件路径
        self.log_path = os.path.join(LOG_PATH, "engine_status.log")

    def opened(self):
        DebugLogger("--------------------------------------------------", file_path=self.log_path)
        DebugLogger("心跳连接成功", file_path=self.log_path)
        DebugLogger("--------------------------------------------------", file_path=self.log_path)

    def closed(self, code, reason=None):
        DebugLogger("--------------------------------------------------", file_path=self.log_path)
        DebugLogger("心跳关闭 原因%s %s" % (code, reason), file_path=self.log_path)
        DebugLogger("--------------------------------------------------", file_path=self.log_path)

    def received_message(self, resp):
        self.queue.put(json.loads(str(resp)))   # 解析JSON格式的消息并放入队列

