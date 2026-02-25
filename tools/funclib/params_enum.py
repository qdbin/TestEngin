# -*- coding: utf-8 -*-
"""
    Faker函数参数类型枚举模块

    本模块定义了Faker库中各种数据生成函数的参数类型映射。
    用于在运行时验证函数调用的参数类型，确保数据生成的正确性。

    作者: LiuMa团队
    日期: 2024
"""

# Faker函数参数类型枚举字典
# 键: 函数名（字符串）
# 值: 参数类型列表，按参数顺序排列
PARAMS_ENUM = {
    # === 基础数据生成函数 ===
    "bothify": [str, str],  # 生成包含字母和数字的字符串 (模板, 字母集)
    "lexify": [str, str],   # 生成包含字母的字符串 (模板, 字母集)
    "numerify": [str],      # 生成包含数字的字符串 (模板)
    
    # === 数字生成函数 ===
    "random_int": [int, int, int],    # 生成随机整数 (最小值, 最大值, 步长)
    "random_number": [int, bool],     # 生成随机数字 (位数, 是否固定位数)
    
    # === 地理位置相关函数 ===
    "country_code": [str],            # 生成国家代码 (表示形式)
    
    # === 商品标识函数 ===
    "ean": [int],                     # 生成EAN条码 (长度)
    "localized_ean": [int],           # 生成本地化EAN条码 (长度)
    
    # === 颜色相关函数 ===
    "color": [str, str, str],         # 生成颜色 (色彩模式, 亮度, 格式)
    
    # === 信用卡相关函数 ===
    "credit_card_full": [str],        # 生成完整信用卡信息 (卡类型)
    "credit_card_number": [str],      # 生成信用卡号 (卡类型)
    "credit_card_provider": [str],    # 生成信用卡提供商 (卡类型)
    "credit_card_security_code": [str],  # 生成信用卡安全码 (卡类型)
    
    # === 日期时间函数 ===
    "date": [str],                    # 生成日期 (格式)
    "time": [str],                    # 生成时间 (格式)
    
    # === 文件相关函数 ===
    "file_extension": [str],          # 生成文件扩展名 (类别)
    "file_name": [str, str],          # 生成文件名 (类别, 扩展名)
    "file_path": [int, str, str],     # 生成文件路径 (深度, 类别, 扩展名)
    "mime_type": [str],               # 生成MIME类型 (类别)
    "unix_device": [str],             # 生成Unix设备名 (前缀)
    "unix_partition": [str],          # 生成Unix分区名 (前缀)
    
    # === 网络相关函数 ===
    "domain_name": [int],             # 生成域名 (级别数)
    "email": [str],                   # 生成邮箱地址 (域名)
    "hostname": [int],                # 生成主机名 (级别数)
    "image_url": [int, int],          # 生成图片URL (宽度, 高度)
    "ipv4": [bool, str, bool],        # 生成IPv4地址 (是否私有, 网络, 是否地址)
    "ipv4_private": [bool, str],      # 生成私有IPv4地址 (是否地址, 网络)
    "ipv4_public": [bool, str],       # 生成公有IPv4地址 (是否地址, 网络)
    "ipv6": [bool],                   # 生成IPv6地址 (是否网络)
    "uri_path": [int],                # 生成URI路径 (深度)
    
    # === 图书标识函数 ===
    "isbn10": [str],                  # 生成ISBN-10 (分隔符)
    "isbn13": [str],                  # 生成ISBN-13 (分隔符)
    
    # === 文本生成函数 ===
    "paragraph": [int, bool],         # 生成段落 (句子数, 是否可变)
    "paragraphs": [int],              # 生成多个段落 (段落数)
    "sentence": [int, bool],          # 生成句子 (单词数, 是否可变)
    "sentences": [int],               # 生成多个句子 (句子数)
    "text": [int],                     # 生成文本 (最大字符数)
    "texts": [int, int],              # 生成多个文本 (文本数, 最大字符数)
    "word": [int],                    # 生成单词 (长度)
    "words": [int],                   # 生成多个单词 (单词数)
    
    # === 安全相关函数 ===
    "password": [int, bool, bool, bool, bool],  # 生成密码 (长度, 特殊字符, 数字, 大写, 小写)
    
    # === 浮点数函数 ===
    "pyfloat": [int, int, bool],      # 生成浮点数 (左位数, 右位数, 是否正数)
    
    # === 文件操作函数 ===
    "loadfile": [str],                # 加载文件内容 (文件路径)
    "savefile": [str],                # 保存文件 (文件路径)
    
    # === Base64编解码函数 ===
    "b64encode_str": [str],           # Base64编码字符串 (原始字符串)
    "b64encode_bytes": [bytes],       # Base64编码字节 (原始字节)
    "b64encode_file": [str],          # Base64编码文件 (文件路径)
    "b64decode_toStr": [str],         # Base64解码为字符串 (编码字符串)
    "b64decode_toBytes": [str],       # Base64解码为字节 (编码字符串)
    
    # === 数学运算函数 ===
    "arithmetic": [str],              # 算术运算 (表达式)
    
    # === 时间操作函数 ===
    "current_time": [str],            # 获取当前时间 (格式)
    "year_shift": [float, str],       # 年份偏移 (偏移量, 格式)
    "month_shift": [float, str],      # 月份偏移 (偏移量, 格式)
    "week_shift": [float, str],       # 周偏移 (偏移量, 格式)
    "date_shift": [float, str],       # 日期偏移 (偏移量, 格式)
    "hour_shift": [float, str],       # 小时偏移 (偏移量, 格式)
    "minute_shift": [float, str],     # 分钟偏移 (偏移量, 格式)
    "second_shift": [float, str],     # 秒偏移 (偏移量, 格式)
    
    # === 数据结构操作函数 ===
    "lenof": [list],                  # 获取列表长度 (列表)
    "indexof": [list, int],           # 获取列表指定索引元素 (列表, 索引)
    "keyof": [dict, str],             # 获取字典指定键值 (字典, 键名)
    
    # === 中文处理函数 ===
    "pinyin": [str],                  # 汉字转拼音 (汉字字符串)
    
    # === 字符串处理函数 ===
    "substing": [str, int, int],      # 字符串截取 (原字符串, 开始位置, 长度)
    "extract": [str],                 # 数据提取 (提取表达式)
    "replace": [str, str, str],       # 字符串替换 (原字符串, 查找字符串, 替换字符串)
    
    # === 数据序列化函数 ===
    "map_dumps": [dict],              # 字典序列化 (字典对象)
    "array_dumps": [list],            # 列表序列化 (列表对象)
}
