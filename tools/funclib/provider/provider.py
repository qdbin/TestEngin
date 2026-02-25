# -*- coding: utf-8 -*-
"""
    LiuMa自定义Faker数据提供者模块

    本模块定义了LiuMa测试平台专用的Faker数据提供者类，扩展了Faker库的功能。
    提供了文件操作、编码解码、时间处理、数据结构操作等多种实用的数据生成方法。

"""

import os
from functools import reduce
from faker.providers import BaseProvider
import time
from app.api import LMApi
from pypinyin import lazy_pinyin
import base64
import datetime
import json
from dateutil.relativedelta import relativedelta
from app.config import FILE_PATH


class LiuMaProvider(BaseProvider):
    """
        LiuMa自定义Faker数据提供者类
        
        继承自Faker的BaseProvider类，为LiuMa测试平台提供专用的数据生成功能。
        包含文件操作、编码解码、时间处理、数据结构操作等多种实用方法。
        
        主要功能分类：
        - 文件操作：loadfile, savefile
        - Base64编解码：b64encode_str, b64encode_bytes, b64encode_file, b64decode_toStr, b64decode_toBytes
        - 数学运算：arithmetic
        - 时间处理：current_time, year_shift, month_shift, week_shift, date_shift, hour_shift, minute_shift, second_shift
        - 数据结构操作：lenof, indexof, keyof
        - 字符串处理：pinyin, substing, extract, replace
        - 数据序列化：map_dumps, array_dumps
    """

    @staticmethod
    def loadfile(uuid: str) -> bytes:
        """
            从LiuMa平台下载测试文件并返回文件内容
            
            Args:
                uuid (str): 文件的唯一标识符
                
            Returns:
                bytes: 文件的二进制内容
                
            Raises:
                Exception: 当文件下载失败时抛出异常
                
            Example:
                >>> provider = LiuMaProvider()
                >>> content = provider.loadfile("test-file-uuid-123")
                >>> print(type(content))  # <class 'bytes'>
        """
        try:
            # 调用LiuMa API下载测试文件
            res = LMApi().download_test_file(uuid)
        except:
            # 下载失败时抛出异常
            raise Exception("拉取测试文件失败")
        else:
            # 返回文件的二进制内容
            return res.content

    @staticmethod
    def savefile(uuid: str) -> str:
        """
            从LiuMa平台下载测试文件并保存到本地，返回文件路径
            
            Args:
                uuid (str): 文件的唯一标识符
                
            Returns:
                str: 保存到本地的文件完整路径
                
            Raises:
                Exception: 当文件下载失败时抛出异常
                
            Example:
                >>> provider = LiuMaProvider()
                >>> file_path = provider.savefile("test-file-uuid-123")
                >>> print(file_path)  # /path/to/files/test-file-uuid-123/filename.txt
        """
        try:
            # 调用LiuMa API下载测试文件
            res = LMApi().download_test_file(uuid)
        except:
            # 下载失败时抛出异常
            raise Exception("拉取测试文件失败")
        else:
            # 从响应头中提取文件名
            file_name = res.headers.get("Content-Disposition").split("=")[1][1:-1]
            # 构建目录路径（以uuid为目录名）
            dir_path = os.path.join(FILE_PATH, uuid)
            # 构建完整文件路径
            file_path = os.path.join(dir_path, file_name)
            # 检查目录是否存在，不存在则创建
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)  # 创建目录
                # 以二进制写入模式打开文件
                with open(file_path, 'wb+') as f:
                    # 分块写入文件内容，避免大文件内存溢出
                    for chunk in res.iter_content(chunk_size=1024):
                        if chunk:  # 过滤空块
                            f.write(chunk)
                f.close()  # 关闭文件
            # 返回文件完整路径
            return file_path

    @staticmethod
    def b64encode_str(s: str) -> str:
        """
            将字符串进行Base64编码
            
            Args:
                s (str): 要编码的字符串
                
            Returns:
                str: Base64编码后的字符串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> encoded = provider.b64encode_str("Hello World")
                >>> print(encoded)  # SGVsbG8gV29ybGQ=
        """
        # 先将字符串编码为UTF-8字节，再进行Base64编码，最后解码为字符串
        return base64.b64encode(s.encode('utf-8')).decode()

    @staticmethod
    def b64encode_bytes(s: bytes) -> str:
        """
            将字节数据进行Base64编码
            
            Args:
                s (bytes): 要编码的字节数据
                
            Returns:
                str: Base64编码后的字符串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> encoded = provider.b64encode_bytes(b"Hello World")
                >>> print(encoded)  # SGVsbG8gV29ybGQ=
        """
        # 直接对字节数据进行Base64编码，然后解码为字符串
        return base64.b64encode(s).decode()

    def b64encode_file(self, uuid: str) -> str:
        """
            将文件内容进行Base64编码
            
            Args:
                uuid (str): 文件的唯一标识符
                
            Returns:
                str: 文件内容Base64编码后的字符串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> encoded = provider.b64encode_file("test-file-uuid-123")
                >>> print(type(encoded))  # <class 'str'>
        """
        # 先加载文件内容（字节格式）
        content = self.loadfile(uuid)
        # 对文件内容进行Base64编码
        return base64.b64encode(content).decode()

    @staticmethod
    def b64decode_toStr(s: str) -> str:
        """
            将Base64编码的字符串解码为普通字符串
            
            Args:
                s (str): Base64编码的字符串
                
            Returns:
                str: 解码后的普通字符串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> decoded = provider.b64decode_toStr("SGVsbG8gV29ybGQ=")
                >>> print(decoded)  # Hello World
        """
        # 先进行Base64解码得到字节，再解码为UTF-8字符串
        return base64.b64decode(s).decode()

    @staticmethod
    def b64decode_toBytes(s: str) -> bytes:
        """
            将Base64编码的字符串解码为字节数据
            
            Args:
                s (str): Base64编码的字符串
                
            Returns:
                bytes: 解码后的字节数据
                
            Example:
                >>> provider = LiuMaProvider()
                >>> decoded = provider.b64decode_toBytes("SGVsbG8gV29ybGQ=")
                >>> print(decoded)  # b'Hello World'
        """
        # 直接进行Base64解码，返回字节数据
        return base64.b64decode(s)

    @staticmethod
    def arithmetic(expression: str):
        """
            执行数学表达式计算
            
            Args:
                expression (str): 要计算的数学表达式字符串
                
            Returns:
                计算结果（类型取决于表达式）
                
            Raises:
                Exception: 当表达式语法错误或无法计算时抛出异常
                
            Example:
                >>> provider = LiuMaProvider()
                >>> result = provider.arithmetic("2 + 3 * 4")
                >>> print(result)  # 14
                >>> result = provider.arithmetic("(10 + 5) / 3")
                >>> print(result)  # 5.0
        """
        try:
            # 使用eval函数计算数学表达式
            return eval(expression)
        except Exception:
            # 计算失败时抛出异常，包含错误的表达式信息
            raise Exception("四则运算表达式错误:%s" % expression)

    @staticmethod
    def current_time(s: str = '%Y-%m-%d') -> str:
        """
            获取当前时间
            
            Args:
                s (str): 时间格式字符串，默认为'%Y-%m-%d'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 格式化的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> time_str = provider.current_time()
                >>> print(time_str)  # 2024-01-15
                >>> time_str = provider.current_time('%Y-%m-%d %H:%M:%S')
                >>> print(time_str)  # 2024-01-15 14:30:25
                >>> timestamp = provider.current_time('none')
                >>> print(timestamp)  # 1705305025000
        """
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(time.time() * 1000)
        # 否则按指定格式返回时间字符串
        return time.strftime(s)

    @staticmethod
    def year_shift(shift: float, s: str = '%Y-%m-%d') -> str:
        """
            获取相对当前时间偏移指定年数后的时间
            
            Args:
                shift (float): 年份偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.year_shift(1)  # 一年后
                >>> print(future_time)  # 2025-01-15
                >>> past_time = provider.year_shift(-2, '%Y-%m-%d %H:%M:%S')  # 两年前
                >>> print(past_time)  # 2022-01-15 14:30:25
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用relativedelta进行年份偏移（支持月份边界处理）
        shift_date = now_date + relativedelta(years=shift)
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def month_shift(shift: float, s: str = '%Y-%m-%d') -> str:
        """
            获取相对当前时间偏移指定月数后的时间
            
            Args:
                shift (float): 月份偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.month_shift(3)  # 三个月后
                >>> print(future_time)  # 2024-04-15
                >>> past_time = provider.month_shift(-6)  # 六个月前
                >>> print(past_time)  # 2023-07-15
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用relativedelta进行月份偏移（支持月份天数差异处理）
        shift_date = now_date + relativedelta(months=shift)
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def week_shift(shift: float, s: str = '%Y-%m-%d') -> str:
        """
            获取相对当前时间偏移指定周数后的时间
            
            Args:
                shift (float): 周数偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.week_shift(2)  # 两周后
                >>> print(future_time)  # 2024-01-29
                >>> past_time = provider.week_shift(-1)  # 一周前
                >>> print(past_time)  # 2024-01-08
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用timedelta进行周数偏移（1周=7天）
        delta = datetime.timedelta(weeks=shift)
        shift_date = now_date + delta
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def date_shift(shift: float, s: str = '%Y-%m-%d') -> str:
        """
            获取相对当前时间偏移指定天数后的时间
            
            Args:
                shift (float): 天数偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.date_shift(7)  # 七天后
                >>> print(future_time)  # 2024-01-22
                >>> past_time = provider.date_shift(-3)  # 三天前
                >>> print(past_time)  # 2024-01-12
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用timedelta进行天数偏移
        delta = datetime.timedelta(days=shift)
        shift_date = now_date + delta
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def hour_shift(shift: float, s: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
            获取相对当前时间偏移指定小时数后的时间
            
            Args:
                shift (float): 小时偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d %H:%M:%S'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.hour_shift(5)  # 五小时后
                >>> print(future_time)  # 2024-01-15 19:30:25
                >>> past_time = provider.hour_shift(-2)  # 两小时前
                >>> print(past_time)  # 2024-01-15 12:30:25
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用timedelta进行小时偏移
        delta = datetime.timedelta(hours=shift)
        shift_date = now_date + delta
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def minute_shift(shift: float, s: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
            获取相对当前时间偏移指定分钟数后的时间
            
            Args:
                shift (float): 分钟偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d %H:%M:%S'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.minute_shift(30)  # 三十分钟后
                >>> print(future_time)  # 2024-01-15 15:00:25
                >>> past_time = provider.minute_shift(-15)  # 十五分钟前
                >>> print(past_time)  # 2024-01-15 14:15:25
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用timedelta进行分钟偏移
        delta = datetime.timedelta(minutes=shift)
        shift_date = now_date + delta
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def second_shift(shift: float, s: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
            获取相对当前时间偏移指定秒数后的时间
            
            Args:
                shift (float): 秒数偏移量，正数表示未来，负数表示过去
                s (str): 时间格式字符串，默认为'%Y-%m-%d %H:%M:%S'。
                        当值为'none'时返回时间戳（毫秒）
                
            Returns:
                str: 偏移后的时间字符串或时间戳
                
            Example:
                >>> provider = LiuMaProvider()
                >>> future_time = provider.second_shift(120)  # 两分钟后
                >>> print(future_time)  # 2024-01-15 14:32:25
                >>> past_time = provider.second_shift(-60)  # 一分钟前
                >>> print(past_time)  # 2024-01-15 14:29:25
        """
        # 获取当前时间
        now_date = datetime.datetime.now()
        # 使用timedelta进行秒数偏移
        delta = datetime.timedelta(seconds=shift)
        shift_date = now_date + delta
        # 如果格式参数为'none'，返回毫秒级时间戳
        if s.lower() == "none":
            return int(shift_date.timestamp() * 1000)
        # 否则按指定格式返回时间字符串
        return shift_date.strftime(s)

    @staticmethod
    def lenof(data) -> int:
        """
            获取数据结构的长度
            
            Args:
                data: 支持len()函数的数据结构（如字符串、列表、字典、元组等）
                
            Returns:
                int: 数据结构的长度
                
            Example:
                >>> provider = LiuMaProvider()
                >>> length = provider.lenof([1, 2, 3, 4])  # 列表长度
                >>> print(length)  # 4
                >>> str_length = provider.lenof("hello")  # 字符串长度
                >>> print(str_length)  # 5
        """
        # 返回数据结构的长度
        return len(data)

    @staticmethod
    def indexof(data, index: int):
        """
            通过索引获取数据结构中的元素
            
            Args:
                data: 支持索引访问的数据结构（如列表、元组、字符串等）
                index (int): 索引位置，支持负数索引
                
            Returns:
                任意类型: 指定索引位置的元素
                
            Example:
                >>> provider = LiuMaProvider()
                >>> element = provider.indexof([10, 20, 30], 1)  # 获取索引1的元素
                >>> print(element)  # 20
                >>> char = provider.indexof("hello", -1)  # 获取最后一个字符
                >>> print(char)  # 'o'
        """
        # 通过索引返回对应位置的元素
        return data[index]

    @staticmethod
    def keyof(data, key: str):
        """
            通过键名获取字典中的值
            
            Args:
                data: 字典类型的数据结构
                key (str): 字典的键名
                
            Returns:
                任意类型: 指定键对应的值
                
            Example:
                >>> provider = LiuMaProvider()
                >>> value = provider.keyof({"name": "张三", "age": 25}, "name")
                >>> print(value)  # "张三"
                >>> age = provider.keyof({"user": {"id": 1}}, "user")
                >>> print(age)  # {"id": 1}
        """
        # 通过键名返回字典中对应的值
        return data[key]

    @staticmethod
    def pinyin(cname: str) -> str:
        """
            将中文文本转换为拼音
            
            Args:
                cname (str): 需要转换的中文文本
                
            Returns:
                str: 转换后的拼音字符串（不带声调）
                
            Example:
                >>> provider = LiuMaProvider()
                >>> result = provider.pinyin("你好世界")
                >>> print(result)  # "nihaoshijie"
                >>> result2 = provider.pinyin("测试数据")
                >>> print(result2)  # "ceshishuju"
        """
        # 使用pypinyin库的lazy_pinyin方法将中文转换为拼音，并连接所有拼音
        return reduce(lambda x, y: x + y, lazy_pinyin(cname))

    @staticmethod
    def substing(s: str, start: int = 0, end: int = -1) -> str:
        """
            截取字符串的子串
            
            Args:
                s (str): 原始字符串
                start (int): 起始位置（包含），默认为0
                end (int): 结束位置（不包含），默认为-1表示到字符串末尾
                
            Returns:
                str: 截取的子串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> result = provider.substing("hello world", 0, 5)
                >>> print(result)  # "hello"
                >>> result2 = provider.substing("hello world", 6)
                >>> print(result2)  # "world"
        """
        # 使用Python切片语法截取字符串
        return s[start:end]

    @staticmethod
    def extract(data):
        """
            提取数据（直接返回原数据）
            
            Args:
                data: 任意类型的数据
                
            Returns:
                任意类型: 原始数据
                
            Example:
                >>> provider = LiuMaProvider()
                >>> result = provider.extract({"key": "value"})
                >>> print(result)  # {"key": "value"}
        """
        # 直接返回原数据，用于数据提取或传递
        return data

    @staticmethod
    def replace(s: str, old: str, new: str) -> str:
        """
            替换字符串中的指定内容
            
            Args:
                s (str): 原始字符串
                old (str): 需要被替换的子串
                new (str): 用于替换的新子串
                
            Returns:
                str: 替换后的字符串
                
            Example:
                >>> provider = LiuMaProvider()
                >>> result = provider.replace("hello world", "world", "python")
                >>> print(result)  # "hello python"
                >>> result2 = provider.replace("测试-数据-处理", "-", "_")
                >>> print(result2)  # "测试_数据_处理"
        """
        # 使用字符串的replace方法进行替换
        return s.replace(old, new)

    @staticmethod
    def map_dumps(data: dict) -> str:
        """
            将字典数据序列化为JSON字符串
            
            Args:
                data (dict): 需要序列化的字典数据
                
            Returns:
                str: JSON格式的字符串，支持中文字符
                
            Example:
                >>> provider = LiuMaProvider()
                >>> data = {"name": "张三", "age": 25, "city": "北京"}
                >>> result = provider.map_dumps(data)
                >>> print(result)  # '{"name": "张三", "age": 25, "city": "北京"}'
        """
        # 使用json.dumps序列化字典，ensure_ascii=False保证中文字符正常显示
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def array_dumps(data: list) -> str:
        """
            将列表数据序列化为JSON字符串
            
            Args:
                data (list): 需要序列化的列表数据
                
            Returns:
                str: JSON格式的字符串，支持中文字符
                
            Example:
                >>> provider = LiuMaProvider()
                >>> data = ["苹果", "香蕉", "橙子"]
                >>> result = provider.array_dumps(data)
                >>> print(result)  # '["苹果", "香蕉", "橙子"]'
                >>> data2 = [{"id": 1, "name": "产品A"}, {"id": 2, "name": "产品B"}]
                >>> result2 = provider.array_dumps(data2)
                >>> print(result2)  # '[{"id": 1, "name": "产品A"}, {"id": 2, "name": "产品B"}]'
        """
        # 使用json.dumps序列化列表，ensure_ascii=False保证中文字符正常显示
        return json.dumps(data, ensure_ascii=False)
