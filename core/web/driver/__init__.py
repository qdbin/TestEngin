# -*- coding: utf-8 -*-
"""
Web操作基础模块

该模块定义了Web自动化测试的基础操作类Operation，
提供了元素定位的核心功能。所有具体的Web操作类都继承自此基类。

主要功能：
- 元素定位：支持多种定位方式（ID、Name、XPath、CSS选择器等）
- 异常处理：统一的异常捕获和日志记录
- 日志记录：详细的操作日志和调试信息
"""

from selenium.webdriver.common.by import By  # Selenium元素定位方式枚举
from selenium.common.exceptions import NoSuchElementException  # 元素未找到异常


class Operation:
    """
    Web操作基础类
    
    提供Web自动化测试的基础功能，主要负责元素定位操作。
    所有具体的Web操作类（如Browser、Assertion、Condition等）都继承自此类。
    
    使用示例：
        operation = Operation()
        element = operation.find_element({'by': 'id', 'value': 'username'})
    """
    
    def __init__(self, test, driver):
        """
        初始化操作基础类
        
        Args:
            test: 测试实例，提供日志记录功能
            driver: WebDriver实例，用于执行浏览器操作
        """
        self.driver = driver  # WebDriver实例
        self.test = test      # 测试实例
        self.print = print    # 打印函数引用

    def find_element(self, element):
        """
        根据定位信息查找单个页面元素
        
        @param {dict} element - 元素定位信息字典，包含定位方式和定位值
        @return {WebElement} 找到的页面元素对象
        支持多种定位方式：id、name、xpath、css_selector、class_name、tag_name、link_text、partial_link_text
        
        element = {'by': 'id', 'value': 'username'}
        """
        try:
            # 根据定位方式选择对应的By类型
            if element["by"] == "id":
                return self.driver.find_element(By.ID, element["value"])  # 通过ID定位
            elif element["by"] == "name":
                return self.driver.find_element(By.NAME, element["value"])  # 通过name属性定位
            elif element["by"] == "xpath":
                return self.driver.find_element(By.XPATH, element["value"])  # 通过XPath定位
            elif element["by"] == "css_selector":
                return self.driver.find_element(By.CSS_SELECTOR, element["value"])  # 通过CSS选择器定位
            elif element["by"] == "class_name":
                return self.driver.find_element(By.CLASS_NAME, element["value"])  # 通过class属性定位
            elif element["by"] == "tag_name":
                return self.driver.find_element(By.TAG_NAME, element["value"])  # 通过标签名定位
            elif element["by"] == "link_text":
                return self.driver.find_element(By.LINK_TEXT, element["value"])  # 通过链接文本定位
            elif element["by"] == "partial_link_text":
                return self.driver.find_element(By.PARTIAL_LINK_TEXT, element["value"])  # 通过部分链接文本定位
        except NoSuchElementException as e:
            # 记录元素未找到的错误日志
            self.test.errorLog("无法定位到元素: %s" % element)
            raise e

    def find_elements(self, element):
        """
        根据定位信息查找多个页面元素
        
        @param {dict} element - 元素定位信息字典，包含定位方式和定位值
        @return {list} 找到的页面元素列表
        返回匹配条件的所有元素，如果没有找到则返回空列表
        
        element = {'by': 'class_name', 'value': 'menu-item'}
        """
        try:
            # 根据定位方式选择对应的By类型
            if element["by"] == "id":
                return self.driver.find_elements(By.ID, element["value"])  # 通过ID查找多个元素
            elif element["by"] == "name":
                return self.driver.find_elements(By.NAME, element["value"])  # 通过name属性查找多个元素
            elif element["by"] == "xpath":
                return self.driver.find_elements(By.XPATH, element["value"])  # 通过XPath查找多个元素
            elif element["by"] == "css_selector":
                return self.driver.find_elements(By.CSS_SELECTOR, element["value"])  # 通过CSS选择器查找多个元素
            elif element["by"] == "class_name":
                return self.driver.find_elements(By.CLASS_NAME, element["value"])  # 通过class属性查找多个元素
            elif element["by"] == "tag_name":
                return self.driver.find_elements(By.TAG_NAME, element["value"])  # 通过标签名查找多个元素
            elif element["by"] == "link_text":
                return self.driver.find_elements(By.LINK_TEXT, element["value"])  # 通过链接文本查找多个元素
            elif element["by"] == "partial_link_text":
                return self.driver.find_elements(By.PARTIAL_LINK_TEXT, element["value"])  # 通过部分链接文本查找多个元素
        except Exception as e:
            # 记录查找元素时的异常
            self.test.errorLog("查找元素时发生异常: %s" % str(e))
            raise e

