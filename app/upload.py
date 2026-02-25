# -*- coding: utf-8 -*-

import os
import threading
from app.api import LMApi


class LMUpload(object):
    """
        测试截图文件上传管理类
        
        负责批量上传测试过程中生成的截图文件到测试平台，支持多线程并发上传
    """

    def __init__(self, files, log_path):
        """
            Args:
                files (list): 待上传的文件名列表
                log_path (str): 上传操作的日志文件路径
        """
        self.files = files          # 存储待上传的文件列表
        self.log_path = log_path    # 存储日志文件路径
        self.api = LMApi()          # 创建API客户端实例，用于文件上传

    def set_upload(self, task_image_path):
        """
            设置并执行批量文件上传
            
            筛选PNG格式的截图文件，创建多线程并发上传，删除非PNG文件
            
            Args:
                task_image_path (str): 任务截图文件存储目录路径
            
            处理流程:
                1. 遍历文件列表，筛选PNG格式文件
                2. 为每个PNG文件创建上传线程
                3. 删除非PNG格式的无效文件
                4. 启动所有上传线程并等待完成
        """
        threads = []  # 存储上传线程的列表
        
        # 遍历所有待处理文件
        for file in self.files:
            if file.endswith(".png"):  # 只处理PNG格式的截图文件
                # 从文件名提取UUID（去掉.png后缀）
                uuid = file[:-4]
                
                # 创建文件上传线程
                thread = threading.Thread(target=self.upload, args=(task_image_path, uuid, file))
                threads.append(thread)
            else:
                os.remove(os.path.join(task_image_path, file))  # 删除非PNG格式的无效文件
        else:
            # 启动所有上传线程，实现并发上传
            for t in threads:
                t.start()

            # 等待所有上传线程完成
            for t in threads:
                t.join()

    def upload(self, task_image_path, uuid, file):
        """
            执行单个文件的上传操作
            
            通过API客户端上传指定的截图文件，上传成功后删除本地文件
            
            Args:
                task_image_path (str): 文件所在目录路径
                uuid (str): 文件的唯一标识符
                file (str): 文件名
            
            注意:
                - 上传失败时会静默处理，不抛出异常
                - 上传成功后会自动删除本地文件以节省存储空间
        """
        try:
            # 调用API上传截图文件到测试平台
            self.api.upload_screen_shot(task_image_path, uuid, self.log_path)
            
            # 上传成功后删除本地文件，释放存储空间
            os.remove(os.path.join(task_image_path, file))
        except:
            # 上传失败时静默处理，避免影响其他文件的上传
            pass

