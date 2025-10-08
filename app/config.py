#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 标准库导入
import os  # 操作系统接口，用于路径操作
import configparser  # 配置文件解析器，用于读取INI格式配置

# 项目根目录路径，通过当前文件位置向上两级目录获取
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据存储目录，用于存放测试数据文件
DATA_PATH = os.path.join(BASE_PATH, "data")

# 文件存储目录，用于存放临时文件和下载文件
FILE_PATH = os.path.join(BASE_PATH, "file")

# 日志存储目录，用于存放各类日志文件
LOG_PATH = os.path.join(BASE_PATH, "log")

# 配置文件路径，引擎的主配置文件位置
CONFIG_PATH = os.path.join(BASE_PATH, "config", "config.ini")

# 图片存储目录，用于存放测试截图
IMAGE_PATH = os.path.join(BASE_PATH, "image")

# 浏览器驱动目录，用于存放WebDriver可执行文件
BROWSER_PATH = os.path.join(BASE_PATH, "browser")


class IniReader:
    """
        INI配置文件读取器类。
        
        提供读取、修改INI格式配置文件的功能，支持按节和选项获取配置值，
        以及动态修改配置项的值。
        
        使用示例:
            reader = IniReader("config.ini")
            value = reader.data("section", "option")
            reader.modify("section", "option", "new_value")
    """
    def __init__(self, config_ini=CONFIG_PATH):
        """
            初始化INI文件读取器。
            
            Args:
                config_ini (str): 配置文件路径，默认使用全局CONFIG_PATH
                
            Raises:
                FileNotFoundError: 当指定的配置文件不存在时抛出异常
        """
        # 检查配置文件是否存在
        if os.path.exists(config_ini):
            self.ini_file = config_ini
        else:
            raise FileNotFoundError('文件不存在！')

    def data(self, section, option):
        """
            获取指定节和选项的配置值。
            
            Args:
                section (str): 配置文件中的节名
                option (str): 节中的选项名
                
            Returns:
                str: 配置项的值
        """
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        # 读取配置文件，指定UTF-8编码确保中文正确解析
        config.read(self.ini_file, encoding="utf-8")
        # 获取指定节和选项的值
        value = config.get(section, option)
        return value

    def option(self, section):
        """
            获取指定节下的所有选项和值。
            
            Args:
                section (str): 配置文件中的节名
                
            Returns:
                dict: 包含该节所有选项名和值的字典
        """
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        # 读取配置文件，指定UTF-8编码
        config.read(self.ini_file, encoding="utf-8")
        # 获取指定节下的所有选项名列表,这里获得的是keys，没有value！！！
        options = config.options(section)
        # 创建空字典用于存储选项名和值的映射
        option = {}
        # 遍历所有选项名，获取对应的值并存储到字典中
        for key in options:
            option[key] = self.data(section, key)
        return option

    def modify(self, section, option, value):
        """
            修改指定节和选项的配置值。
            
            Args:
                section (str): 配置文件中的节名
                option (str): 节中的选项名
                value (str): 新的配置值
        """
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        # 读取当前配置文件内容
        config.read(self.ini_file, encoding="utf-8")
        # 设置指定节和选项的新值
        config.set(section, option, value)
        # 将修改后的配置写回文件，使用r+模式覆盖原文件
        config.write(open(self.ini_file, "r+", encoding="utf-8"))


class LMConfig(object):
    """
        配置管理类。
    """
    def __init__(self, path=CONFIG_PATH):
        # 创建INI文件读取器实例
        reader = IniReader(path)
        
        # 加载平台配置：服务器地址和错误输出控制
        self.url = reader.data("Platform", "url")
        self.enable_stderr = reader.data("Platform", "enable-stderr")
        
        # 加载引擎认证配置：引擎标识和密钥
        self.engine = reader.data("Engine", "engine-code")
        self.secret = reader.data("Engine", "engine-secret")
        
        # 加载HTTP请求头配置，返回完整的头部字典
        self.header = reader.option("Header")
        
        # 加载浏览器驱动配置
        self.browser_opt = reader.data("WebDriver", "options")
        # 根据驱动选项决定路径处理方式：remote模式或绝对路径直接使用，否则拼接到browser目录
        if self.browser_opt == "remote" or "/" in reader.data("WebDriver", "path"):
            self.browser_path = reader.data("WebDriver", "path")
        else:
            self.browser_path = os.path.join(BROWSER_PATH, reader.data("WebDriver", "path"))
        
        # 加载运行时配置：最大并发执行数量
        self.max_run = reader.data("RunSetting", "max-run")