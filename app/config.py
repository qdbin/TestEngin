#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser

# 项目根目录路径
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据存储目录
DATA_PATH = os.path.join(BASE_PATH, "data")

# 文件存储目录
FILE_PATH = os.path.join(BASE_PATH, "file")

# 日志存储目录
LOG_PATH = os.path.join(BASE_PATH, "log")

# 配置文件路径
CONFIG_PATH = os.path.join(BASE_PATH, "config", "config.ini")

# 图片存储目录
IMAGE_PATH = os.path.join(BASE_PATH, "image")

# 浏览器驱动目录
BROWSER_PATH = os.path.join(BASE_PATH, "browser")


class IniReader:
    def __init__(self, config_ini=CONFIG_PATH):
        # 检查配置文件是否存在
        if os.path.exists(config_ini):
            self.ini_file = config_ini      # 配置文件路径，默认使用全局CONFIG_PATH
        else:
            raise FileNotFoundError('文件不存在！')

    def data(self, section, option):
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        config.read(self.ini_file, encoding="utf-8")

        # 获取指定节和选项的值
        value = config.get(section, option)
        return value

    def safe_data(self, section, option, default=None):
        config = configparser.ConfigParser()
        config.read(self.ini_file, encoding="utf-8")
        if not config.has_section(section):
            return default
        if not config.has_option(section, option):
            return default
        return config.get(section, option)

    def option(self, section):
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        config.read(self.ini_file, encoding="utf-8")

        # 获取指定节下的所有选项名列表,这里获得的是keys，没有value！！！
        if not config.has_section(section):
            return {}
        options = config.options(section)

        # 用于存储选项名和值的映射
        option = {}
        for key in options:
            option[key] = self.data(section, key)
        return option

    def modify(self, section, option, value):
        # 创建配置解析器实例
        config = configparser.ConfigParser()
        config.read(self.ini_file, encoding="utf-8")

        # 设置指定节和选项的新值
        config.set(section, option, value)

        # 将修改后的配置写回文件，使用r+模式覆盖原文件
        config.write(open(self.ini_file, "r+", encoding="utf-8"))


class LMConfig(object):
    def __init__(self, path=CONFIG_PATH):
        # 创建INI文件读取器实例
        reader = IniReader(path)
        
        # 加载平台配置：服务器地址和错误输出控制
        self.url = reader.data("Platform", "url")
        self.enable_stderr = reader.data("Platform", "enable-stderr")
        
        # 加载引擎认证配置：引擎标识和密钥
        self.engine = reader.data("Engine", "engine-code")
        self.secret = reader.data("Engine", "engine-secret")
        
        self.header = reader.option("Header")

        self.browser_opt = reader.safe_data("WebDriver", "options", default="")
        webdriver_path = reader.safe_data("WebDriver", "path", default="")
        if self.browser_opt == "remote" or "/" in webdriver_path:
            self.browser_path = webdriver_path
        elif webdriver_path:
            self.browser_path = os.path.join(BROWSER_PATH, webdriver_path)
        else:
            self.browser_path = ""
        
        # 加载运行时配置：最大并发执行数量
        self.max_run = reader.data("RunSetting", "max-run")
