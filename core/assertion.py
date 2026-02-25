# -*- coding: utf-8 -*-
import re  # 正则表达式模块，用于字符串模式匹配
import ast  # 抽象语法树模块，用于安全解析字符串为Python对象

from assertpy import assertpy  # 第三方断言库，提供丰富的断言方法


class LMAssert:
    """
        LiuMa测试引擎断言类
        
        提供多种类型的断言验证功能，支持字符串、数字、列表、字典等数据类型的比较和验证。
        该类封装了assertpy库的功能，并提供了中文化的断言类型支持。
        
        Attributes:
            comparator (str): 断言比较器类型，支持中英文断言类型
            actual_result: 实际结果值
            expected_result: 期望结果值
        
        Example:
            >>> assert_obj = LMAssert("equal", "hello", "hello")
            >>> result, message = assert_obj.compare()
            >>> print(result)  # True
    """

    def __init__(self, position, actual_result, expected_result):
        """
        初始化断言对象
        
        Args:
            position (str): 断言比较器类型，如"equal"、"contains"等
            actual_result: 实际结果值，可以是任意类型
            expected_result: 期望结果值，可以是任意类型
        """
        self.comparator = position  # 断言比较器类型
        self.actual_result = actual_result  # 实际结果值
        self.expected_result = expected_result  # 期望结果值

    def compare(self):
        """
            执行断言比较操作
            
            根据初始化时设置的比较器类型，对实际结果和期望结果进行相应的断言验证。
            支持多种断言类型，包括相等性比较、包含关系、数值比较、类型检查等。
            
            Returns:
                tuple: 包含两个元素的元组
                    - bool: 断言结果，True表示断言通过，False表示断言失败
                    - str: 断言消息，成功时返回'success'，失败时返回详细错误信息
            
            Raises:
                AssertionTypeNotExist: 当使用了不支持的断言类型时抛出
            
            Example:
                >>> assert_obj = LMAssert("equal", "test", "test")
                >>> result, message = assert_obj.compare()
                >>> print(f"结果: {result}, 消息: {message}")
        """
        try:
            if self.comparator in ["equal", "equals", "相等", "字符相等"]:  # 等于
                assFailMsg = '实际值({})与预期值({}) 字符相等，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(str(self.actual_result)).is_equal_to(self.expected_result)
            elif self.comparator in ["equalsList", "数组相等"]:  # 列表相同，包括列表顺序也相同
                assFailMsg = '实际值({})与预期值({}) 数组相等，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2list(self.actual_result)).is_equal_to(LMAssert.str2list(self.expected_result))
            elif self.comparator in ["equalsDict", "对象相等"]:  # 字典相同
                assFailMsg = '实际值({})与预期值({}) 对象相等，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2dict(self.actual_result)).is_equal_to(LMAssert.str2dict(self.expected_result))
            elif self.comparator in ["equalsNumber", "数字相等", "数值相等"]:  # 数字等于
                assFailMsg = '实际值({})与预期值({}) 数值相等，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_equal_to(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["equalIgnoreCase", "相等(忽略大小写)"]:  # 忽略大小写等于
                assFailMsg = '实际值({})与预期值({}) 相等(忽略大小写)，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(str(self.actual_result)).is_equal_to_ignoring_case(self.expected_result)
            elif self.comparator in ["notEqual", "does not equal", "不等于"]:  # 不等于
                assFailMsg = '实际值({}) 不等于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_not_equal_to(self.expected_result)
            elif self.comparator in ["contains", "包含"]:  # 字符串包含该字符
                assFailMsg = '实际值({}) 包含 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.to_str(self.actual_result)).contains((self.expected_result))
            elif self.comparator in ["notContains", "does no contains", "不包含"]:  # 字符串不包含该字符
                assFailMsg = '实际值({}) 不包含 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).does_not_contain(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["containsOnly", "仅包含"]:  # 字符串仅包含该字符
                assFailMsg = '实际值({}) 仅包含 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).contains_only(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["isNone", "none/null"]:  # 为none或null
                assFailMsg = '实际值({}) 为none或null，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2none(self.actual_result)).is_none()
            elif self.comparator in ["notEmpty", "is not empty", "不为空"]:  # 不为空
                assFailMsg = '实际值({}) 不为空，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_not_empty()
            elif self.comparator in ["empty", "is empty", "为空"]:  # 为空
                assFailMsg = '实际值({}) 为空，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_empty()
            elif self.comparator in ["isTrue", "true"]:  # 是true
                assFailMsg = '实际值({}) 是true，条件为否：'.format(self.actual_result, self.expected_result)
                res = False if LMAssert.str2bool(self.actual_result) is None else LMAssert.str2bool(self.actual_result)
                assertpy.assert_that(res).is_true()
            elif self.comparator in ["isFalse", "false"]:  # 是false
                assFailMsg = '实际值({}) 是false，条件为否：'.format(self.actual_result, self.expected_result)
                res = True if LMAssert.str2bool(self.actual_result) is None else LMAssert.str2bool(self.actual_result)
                assertpy.assert_that(res).is_false()
            elif self.comparator in ["isStrType", "字符串"]:  # 是str的类型
                assFailMsg = '实际值({}) 是字符串，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_type_of(str)
            elif self.comparator in ["isIntType", "整数"]:  # 是int的类型
                assFailMsg = '实际值({}) 是整数，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_type_of(int)
            elif self.comparator in ["isFloatType", "浮点数"]:  # 是浮点的类型
                assFailMsg = '实际值({}) 是浮点数，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_type_of(float)
            elif self.comparator in ["isInt", "is a number", "仅含数字"]:  # 字符串中仅含有数字
                assFailMsg = '实际值({}) 仅含数字，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_digit()
            elif self.comparator in ["isLetter", "仅含字母"]:  # 字符串中仅含有字母
                assFailMsg = '实际值({}) 仅含字母，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_alpha()
            elif self.comparator in ["isLower", "小写"]:  # 是小写的
                assFailMsg = '实际值({}) 是小写的，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_lower()
            elif self.comparator in ["isUpper", "大写"]:  # 是大写的
                assFailMsg = '实际值({}) 是大写的，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_upper()
            elif self.comparator in ["startWith", "开头是"]:  # 字符串以该字符开始
                assFailMsg = '实际值({}) 开头是 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).starts_with(self.expected_result)
            elif self.comparator in ["endWith", "结尾是"]:  # 字符串以该字符结束
                assFailMsg = '实际值({}) 结尾是 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).ends_with(self.expected_result)
            elif self.comparator in ["isIn", "has item", "包含对象", "被包含"]:  # 在这几个字符串中
                assFailMsg = '实际值({}) 被包含在 预期值({}) 列表中，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_in(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["isNotIn", "不被包含"]:  # 不在这几个字符串中
                assFailMsg = '实际值({}) 不被包含在 预期值({}) 列表中，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_not_in(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["isNotZero", "非0"]:  # 不是0
                assFailMsg = '实际值({}) 不是0，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_not_zero()
            elif self.comparator in ["isZero", "为0"]:  # 是0
                assFailMsg = '实际值({}) 是0，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_zero()
            elif self.comparator in ["isPositive", "正数"]:  # 是正数
                assFailMsg = '实际值({}) 是正数，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_positive()
            elif self.comparator in ["isNegative", "负数"]:  # 是负数
                assFailMsg = '实际值({}) 是负数，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(self.actual_result).is_negative()
            elif self.comparator in ["isGreaterThan", " 大于"]:  # 大于
                assFailMsg = '实际值({}) 大于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_greater_than(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["isGreaterThanOrEqualTo", "greater than or equal", ">=", " 大于等于"]:  # 大于等于
                assFailMsg = '实际值({}) 大于等于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_greater_than_or_equal_to(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["isLessThan", " 小于"]:  # 小于
                assFailMsg = '实际值({}) 小于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_less_than(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["isLessThanOrEqualTo", "less than or equal", "<=", " 小于等于"]:  # 小于等于
                assFailMsg = '实际值({}) 小于等于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_less_than_or_equal_to(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["isBetween", " 在...之间"]:  # 在...之间
                assFailMsg = '实际值({}) 在 预期值({}) 之间，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_between(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["isCloseTo", " 接近于"]:  # 接近于
                assFailMsg = '实际值({}) 接近于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.str2num(self.actual_result)).is_close_to(*LMAssert.str2list(self.expected_result))
            elif self.comparator in ["listLenEqual","列表长度相等"]:  # 列表长度相等
                assFailMsg = '实际值({}) 列表长度相等 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.list_len(self.actual_result)).is_equal_to(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["listLenGreaterThan","列表长度大于"]:  # 列表长度大于
                assFailMsg = '实际值({}) 列表长度大于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.list_len(self.actual_result)).is_greater_than(LMAssert.str2num(self.expected_result))
            elif self.comparator in ["listLenLessThan","列表长度小于"]:  # 列表长度小于
                assFailMsg = '实际值({}) 列表长度小于 预期值({})，条件为否：'.format(self.actual_result, self.expected_result)
                assertpy.assert_that(LMAssert.list_len(self.actual_result)).is_less_than_or_equal_to(LMAssert.str2num(self.expected_result))
            else:
                raise AssertionTypeNotExist('没有{}该断言类型'.format(self.comparator))
            return True, 'success'
        except AssertionError as e:
            ex = str(e).replace("Expected <", "Expected (").replace(">, ", "), ").replace(" <", " (").replace("> ", ") ")
            return False, assFailMsg + ex

    @staticmethod
    def str2none(value):
        """
            将字符串转换为None值
            
            检查输入值是否为"none"或"null"字符串（忽略大小写），如果是则返回None，否则返回原值。
            
            Args:
                value: 待转换的值，可以是任意类型
            
            Returns:
                None或原值: 如果输入为"none"或"null"字符串则返回None，否则返回原值
            
            Example:
                >>> LMAssert.str2none("none")  # None
                >>> LMAssert.str2none("test")  # "test"
        """
        if str(value).lower() == "none" or str(value).lower() == "null":
            return None
        else:
            return value

    @staticmethod
    def str2bool(value):
        """
            将字符串转换为布尔值
            
            检查输入值是否为"true"或"false"字符串（忽略大小写），进行相应的布尔值转换。
            
            Args:
                value: 待转换的值，可以是任意类型
            
            Returns:
                bool或None: "true"返回True，"false"返回False，其他情况返回None
            
            Example:
                >>> LMAssert.str2bool("true")   # True
                >>> LMAssert.str2bool("false")  # False
                >>> LMAssert.str2bool("other")  # None
        """
        if str(value).lower() == "true":
            return True
        elif str(value).lower() == "false":
            return False
        else:
            return None

    @staticmethod
    def str2num(value):
        """
            将字符串转换为数字类型
            
            尝试将输入值转换为整数或浮点数。如果输入已经是数字类型则直接返回，
            如果是符合数字格式的字符串则转换为相应的数字类型。
            
            Args:
                value: 待转换的值，可以是字符串、数字或其他类型
            
            Returns:
                int/float/原值: 成功转换则返回数字，否则返回原值
            
            Example:
                >>> LMAssert.str2num("123")    # 123
                >>> LMAssert.str2num("12.5")   # 12.5
                >>> LMAssert.str2num("abc")    # "abc"
        """
        if type(value) == int or type(value) == float:
            return value
        if value is None or len(value) == 0:
            return None
        elif re.fullmatch(r'-?[0-9]*\.?[0-9]*', value) is not None:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        else:
            return value

    @staticmethod
    def str2list(value):
        """
            将字符串转换为列表类型
            
            尝试将字符串格式的列表（如"[1,2,3]"）转换为Python列表对象。
            支持数字和字符串元素的混合列表转换。
            
            Args:
                value: 待转换的值，可以是字符串、列表或其他类型
            
            Returns:
                list/原值: 成功转换则返回列表，否则返回原值
            
            Example:
                >>> LMAssert.str2list("[1,2,3]")        # [1, 2, 3]
                >>> LMAssert.str2list("['a','b']")     # ['a', 'b']
                >>> LMAssert.str2list([1,2,3])         # [1, 2, 3]
        """
        if type(value) == list or type(value) == int or type(value) == float:
            return value
        if value is None or len(value) == 0:
            return None
        value_list = []  # 初始化结果列表
        if value.startswith('[') and value.endswith(']'):  # 检查是否为列表格式
            for item in value[1:-1].split(','):  # 分割列表元素
                item_strip = item.strip()  # 去除空格
                if re.fullmatch(r'-?[0-9]*\.?[0-9]*', item_strip) is not None:  # 检查是否为数字
                    if '.' in item_strip:
                        value_list.append(float(item_strip))  # 转换为浮点数
                    else:
                        value_list.append(int(item_strip))  # 转换为整数
                else:  # 字符串元素
                    value_list.append(item_strip[1:-1])  # 去除引号
            return value_list
        else:
            return value

    @staticmethod
    def str2dict(value):
        """
            将字符串转换为字典类型
            
            尝试将字符串格式的字典（如"{\"key\": \"value\"}"）转换为Python字典对象。
            使用ast.literal_eval进行安全的字符串解析。
            
            Args:
                value: 待转换的值，可以是字符串、字典或其他类型
            
            Returns:
                dict/原值: 成功转换则返回字典，否则返回原值
            
            Example:
                >>> LMAssert.str2dict('{"a": 1}')     # {'a': 1}
                >>> LMAssert.str2dict({'a': 1})       # {'a': 1}
        """
        if type(value) == dict or type(value) == int or type(value) == float:
            return value
        if value is None or len(value) == 0:
            return None
        value_dict={}  # 初始化结果字典
        if value.startswith('{') and value.endswith('}'):  # 检查是否为字典格式
            for item in value[1:-1].split(','):  # 遍历字典项
                value_dict = ast.literal_eval(value)  # 使用ast安全解析
            return value_dict
        else:
            return value

    @staticmethod
    def to_str(value):
        """
            将值转换为字符串类型
            
            将输入值转换为字符串格式，处理各种数据类型的转换。
            
            Args:
                value: 待转换的值，可以是任意类型
            
            Returns:
                str: 转换后的字符串，空值返回空字符串
            
            Example:
                >>> LMAssert.to_str(123)      # "123"
                >>> LMAssert.to_str(None)     # ""
                >>> LMAssert.to_str("test")   # "test"
        """
        if type(value) == int or type(value) == float:
            return value
        if value is None or len(value) == 0:
            return ""  # 空值返回空字符串
        if type(value) == str:
            return value
        else:
            return str(value)  # 其他类型转换为字符串

    @staticmethod
    def list_len(value):
        """
            获取列表的长度
            
            将输入值转换为列表后返回其长度，用于列表长度相关的断言。
            
            Args:
                value: 待检查长度的值，应该是列表格式或可转换为列表的字符串
            
            Returns:
                int: 列表的长度
            
            Raises:
                AssertionTypeNotExist: 当输入值无法转换为列表时抛出
            
            Example:
                >>> LMAssert.list_len("[1,2,3]")  # 3
                >>> LMAssert.list_len([1,2,3])    # 3
        """
        value2list=LMAssert.str2list(value)  # 转换为列表
        if type(value2list) != list:
            raise AssertionTypeNotExist('传入实际值({}) 不是列表格式'.format(value))
        else:
            return len(value2list)  # 返回列表长度


class AssertionTypeNotExist(Exception):
    """
        断言类型不存在异常
        
        当使用了不支持的断言类型或数据格式转换失败时抛出此异常。
        继承自Python内置的Exception类。
        
        Example:
            >>> raise AssertionTypeNotExist("不支持的断言类型: unknown_type")
    """
