# -*- coding: utf-8 -*-
import os  # 操作系统接口库
import logging  # Python标准日志库
import threading  # 线程同步库
from app.config import LOG_PATH  # 导入日志目录路径配置


class LMLogger(object):
    """
        引擎日志记录器类。
        
        提供统一的日志记录功能，支持自定义日志格式、文件路径和日志级别。
        自动创建日志目录，确保日志文件能够正常写入。
        
        使用示例:
            logger = LMLogger("TestLogger")
            handler = logger.get_handler("/path/to/log.txt")
    """

    def __init__(self, logger_name='Auto Test'):
        """
            初始化日志记录器。
            
            Args:
                logger_name (str): 日志记录器名称，默认为'Auto Test'
        """
        self.logger = logging.getLogger(logger_name)
        # 设置日志格式：时间戳 - 日志级别 - 消息内容
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)-4s - %(message)s")
        # 设置日志级别为INFO，记录INFO及以上级别的日志
        self.logger.setLevel(logging.DEBUG)

    def get_handler(self, file_path):
        """
            创建文件日志处理器。
            
            Args:
                file_path (str): 日志文件的完整路径
                
            Returns:
                logging.FileHandler: 配置好的文件日志处理器
        """
        # 分离文件路径和文件名
        p, f = os.path.split(file_path)
        # 如果目录不存在则创建目录
        if not (os.path.exists(p)):
            os.makedirs(p)
        # 创建文件处理器，指定UTF-8编码确保中文正确显示
        file_handler = logging.FileHandler(file_path, encoding="utf8")
        file_handler.setFormatter(self.formatter)
        return file_handler


# 创建全局日志记录器实例
my_logger = LMLogger()
default_log_path = os.path.join(LOG_PATH, "engine_run.log")     # 默认日志文件路径
my_lock = threading.RLock()     # 创建可重入锁，确保多线程环境下日志记录的线程安全


def DebugLogger(log_info, file_path=default_log_path):
    """
        记录调试信息日志。
        
        使用INFO级别记录调试信息，支持自定义日志文件路径。
        采用线程锁确保多线程环境下的日志记录安全。
        
        Args:
            log_info (str): 要记录的日志信息
            file_path (str): 日志文件路径，默认使用全局默认路径
    """
    try:
        # 获取线程锁，确保日志记录的原子性
        if my_lock.acquire():
            file_handler = my_logger.get_handler(file_path)
            my_logger.logger.addHandler(file_handler)
            my_logger.logger.info(log_info)
            # 移除处理器避免重复添加
            my_logger.logger.removeHandler(file_handler)
            my_lock.release()
    except Exception as e:
        print("Failed to record debug log. Reason:\n %s" % str(e))


def ErrorLogger(log_info, file_path=default_log_path):
    """
        记录错误信息日志。
        
        使用ERROR级别记录错误信息，支持自定义日志文件路径。
        采用线程锁确保多线程环境下的日志记录安全。
        
        Args:
            log_info (str): 要记录的错误信息
            file_path (str): 日志文件路径，默认使用全局默认路径
    """
    try:
        # 获取线程锁，确保日志记录的原子性
        if my_lock.acquire():
            file_handler = my_logger.get_handler(file_path)
            my_logger.logger.addHandler(file_handler)
            my_logger.logger.error(log_info)
            # 移除处理器避免重复添加
            my_logger.logger.removeHandler(file_handler)
            my_lock.release()
    except Exception as e:
        print("Failed to record error log. Reason:\n %s" % str(e))
