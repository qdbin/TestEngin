#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Web操作信息收集模块

        该模块负责从UI数据中收集和解析Web自动化测试操作的相关信息，
        包括操作类型、元素定位、操作数据等，为测试步骤执行提供数据支持。
        
        主要功能：
        1. 操作信息收集：从UI数据中提取操作的各种属性
        2. 元素定位解析：将元素定位信息转换为Selenium可识别的格式
        3. 数据格式化：处理和格式化操作相关的数据
        4. 统一数据接口：为测试执行器提供标准化的数据访问接口
        
        作者: LiuMa团队
        日期: 2024-01-26
"""

from selenium.webdriver.common.by import By  # Selenium元素定位方式枚举


# 元素定位方式映射字典
# 将UI界面中的定位方式字符串映射为Selenium WebDriver可识别的定位器
locator = {
    "ID": By.ID,                      # ID定位：通过元素的id属性定位
    "XPATH": "xpath",                 # XPath定位：通过XPath表达式定位
    "LINK": "link text",              # 链接文本定位：通过完整链接文本定位
    "PARTIAL": "partial link text",   # 部分链接文本定位：通过部分链接文本定位
    "NAME": "name",                   # Name定位：通过元素的name属性定位
    "TAG": "tag name",                # 标签名定位：通过HTML标签名定位
    "CLASS": "class name",            # Class定位：通过元素的class属性定位
    "CSS": "css selector"             # CSS选择器定位：通过CSS选择器定位
}


class WebOperationCollector:
    """Web操作信息收集器
    
        负责从UI数据中收集和解析Web自动化测试操作的各种信息，
        包括操作ID、类型、名称、事务名称、元素定位信息、操作数据和操作代码等。
        
        主要功能：
        1. 解析UI数据中的操作信息
        2. 转换元素定位信息为Selenium格式
        3. 收集和存储操作相关的所有数据
        4. 提供统一的数据访问接口
        
        属性说明：
        - id: 操作唯一标识符
        - opt_type: 操作类型（如assertion、condition等）
        - opt_name: 操作名称
        - opt_trans: 操作事务名称（用于日志显示）
        - opt_element: 元素定位信息字典
        - opt_data: 操作数据字典
        - opt_code: 操作代码
    """

    def __init__(self):
        """初始化Web操作信息收集器
        
            初始化所有操作相关的属性为None，等待后续收集和赋值
        """
        self.id = None           # 操作唯一标识符
        self.opt_type = None     # 操作类型（assertion/condition/normal等）
        self.opt_name = None     # 操作名称
        self.opt_trans = None    # 操作事务名称（用于日志显示）
        self.opt_element = None  # 元素定位信息字典
        self.opt_data = None     # 操作数据字典
        self.opt_code = None     # 操作代码

    @staticmethod
    def __parse(ui_data: dict, name):
        """解析UI数据中的指定字段
        
            从UI数据字典中安全地获取指定字段的值
            
            Args:
                ui_data (dict): UI数据字典
                name (str): 要获取的字段名称
                
            Returns:
                任意类型或None: 字段值，如果字段不存在则返回None
        """
        # 检查字段是否存在于UI数据中
        if name not in ui_data:
            return None
        # 安全获取字段值
        return ui_data.get(name)

    def collect_id(self, ui_data):
        """收集操作ID
        
            从UI数据中提取操作的唯一标识符
            
            Args:
                ui_data (dict): UI数据字典
        """
        # 从UI数据中解析操作ID
        self.id = WebOperationCollector.__parse(ui_data, "operationId")

    def collect_opt_type(self, ui_data):
        """收集操作类型
        
            从UI数据中提取操作类型（如assertion、condition、normal等）
            
            Args:
                ui_data (dict): UI数据字典
        """
        # 从UI数据中解析操作类型
        self.opt_type = WebOperationCollector.__parse(ui_data, "operationType")

    def collect_opt_name(self, ui_data):
        """收集操作名称
        
            从UI数据中提取操作的名称标识
            
            Args:
                ui_data (dict): UI数据字典
        """
        # 从UI数据中解析操作名称
        self.opt_name = WebOperationCollector.__parse(ui_data, "operationName")

    def collect_opt_trans(self, ui_data):
        """收集操作事务名称
        
            从UI数据中提取操作的事务名称，主要用于日志显示
            
            Args:
                ui_data (dict): UI数据字典
        """
        # 从UI数据中解析操作事务名称
        self.opt_trans = WebOperationCollector.__parse(ui_data, "operationTrans")

    def collect_opt_code(self, ui_data):
        """收集操作代码
        
            从UI数据中提取操作相关的代码信息
            
            Args:
                ui_data (dict): UI数据字典
        """
        # 从UI数据中解析操作代码
        self.opt_code = WebOperationCollector.__parse(ui_data, "operationCode")

    def collect_opt_element(self, ui_data):
        """收集操作元素定位信息
        
            从UI数据中提取元素定位信息，并转换为Selenium可识别的格式
            
            Args:
                ui_data (dict): UI数据字典
                
            处理逻辑：
            1. 解析UI数据中的元素定位信息
            2. 检查数据有效性（非空且有内容）
            3. 遍历每个元素，转换定位方式和表达式
            4. 构建标准化的元素定位字典
        """
        # 从UI数据中解析元素定位信息
        opt_element = WebOperationCollector.__parse(ui_data, "operationElement")
        
        # 检查元素定位信息是否为空
        if opt_element is None or len(opt_element) == 0:
            self.opt_element = None
        else:
            elements = {}  # 初始化元素定位字典
            
            # 遍历每个元素定位信息
            for name, element in opt_element.items():
                # 转换为Selenium格式：(定位方式, 定位表达式)
                elements[name] = (locator[element["by"]], element["expression"])
            
            # 保存转换后的元素定位信息
            self.opt_element = elements

    def collect_opt_data(self, ui_data):
        """收集操作数据
        
            从UI数据中提取操作相关的数据信息
            
            Args:
                ui_data (dict): UI数据字典
                
            处理逻辑：
            1. 解析UI数据中的操作数据
            2. 检查数据有效性（非空且有内容）
            3. 直接保存操作数据字典
        """
        # 从UI数据中解析操作数据
        opt_data = WebOperationCollector.__parse(ui_data, "operationData")
        
        # 检查操作数据是否为空
        if opt_data is None or len(opt_data) == 0:
            self.opt_data = None
        else:
            # 直接保存操作数据
            self.opt_data = opt_data

    def collect(self, ui_data):
        """收集所有操作信息
        
            统一收集UI数据中的所有操作相关信息
            
            Args:
                ui_data (dict): UI数据字典
                
            收集内容：
            1. 操作ID - 唯一标识符
            2. 操作类型 - 操作分类（assertion/condition/normal等）
            3. 操作名称 - 操作标识名称
            4. 操作事务名称 - 用于日志显示的名称
            5. 元素定位信息 - 页面元素的定位方式和表达式
            6. 操作数据 - 操作相关的参数数据
            7. 操作代码 - 操作相关的代码信息
        """
        # 按顺序收集所有操作信息
        self.collect_id(ui_data)          # 收集操作ID
        self.collect_opt_type(ui_data)    # 收集操作类型
        self.collect_opt_name(ui_data)    # 收集操作名称
        self.collect_opt_trans(ui_data)   # 收集操作事务名称
        self.collect_opt_element(ui_data) # 收集元素定位信息
        self.collect_opt_data(ui_data)    # 收集操作数据
        self.collect_opt_code(ui_data)    # 收集操作代码
