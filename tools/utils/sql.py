# -*- coding: utf-8 -*-
import decimal  # 用于处理高精度小数类型
import pymssql as mssql  # SQL Server数据库连接驱动
import pymysql as mysql  # MySQL数据库连接驱动
import psycopg2 as pgsql  # PostgreSQL数据库连接驱动
import cx_Oracle as oracle  # Oracle数据库连接驱动


class SQLConnect:
    """
        数据库连接工具类
        
        支持多种数据库类型的连接和操作，包括MySQL、SQL Server、PostgreSQL和Oracle。
        提供统一的接口进行数据库连接、查询和执行非查询操作。
        
        Attributes:
            tpz (str): 数据库类型，支持'mysql'、'mssql'、'pgsql'、'oracle'
            host (str): 数据库服务器地址
            port (int): 数据库端口号
            db (str): 数据库名称
            user (str): 数据库用户名
            pwd (str): 数据库密码
            conn: 数据库连接对象
        
        Example:
            >>> sql_conn = SQLConnect('mysql', 'localhost', 3306, 'test_db', 'user', 'password')
            >>> results = sql_conn.query('SELECT * FROM users')
            >>> sql_conn.exec('INSERT INTO users (name) VALUES ("test")')
    """

    def __init__(self, tpz, host, port, db, user, password):
        """
            初始化数据库连接参数
            
            Args:
                tpz (str): 数据库类型，支持'mysql'、'mssql'、'pgsql'、'oracle'
                host (str): 数据库服务器地址
                port (int/str): 数据库端口号
                db (str): 数据库名称
                user (str): 数据库用户名
                password (str): 数据库密码
        """
        self.tpz = tpz  # 数据库类型
        self.host = host  # 服务器地址
        self.port = int(port)  # 端口号，确保为整数类型
        self.db = db  # 数据库名称
        self.user = user  # 用户名
        self.pwd = password  # 密码
        self.conn = None  # 数据库连接对象，初始为None

    def connect(self):
        """
            建立数据库连接并返回游标对象
            
            根据初始化时指定的数据库类型，使用相应的驱动程序建立数据库连接。
            支持MySQL、SQL Server、PostgreSQL和Oracle四种数据库类型。
            
            Returns:
                cursor: 数据库游标对象，用于执行SQL语句
            
            Raises:
                TypeError: 当数据库类型不受支持时抛出
                RuntimeError: 当数据库连接失败时抛出
            
            Example:
                >>> cursor = sql_conn.connect()
                >>> cursor.execute('SELECT 1')
        """
        # 根据数据库类型选择相应的连接方式
        if self.tpz == "mysql":
            # MySQL数据库连接，使用UTF-8字符集
            self.conn = mysql.connect(host=self.host, user=self.user,
                                      password=self.pwd, database=self.db, port=self.port, charset='utf8')
        elif self.tpz == "mssql":
            # SQL Server数据库连接，使用UTF-8字符集
            self.conn = mssql.connect(server=self.host, user=self.user,
                                      password=self.pwd, database=self.db, port=self.port, charset='utf8')
        elif self.tpz == "pgsql":
            # PostgreSQL数据库连接
            self.conn = pgsql.connect(host=self.host, user=self.user,
                                      password=self.pwd, database=self.db, port=self.port)
        elif self.tpz == "oracle":
            # Oracle数据库连接，支持两种连接方式
            try:
                # 尝试使用服务名连接
                self.conn = oracle.connect(self.user, self.pwd, f"{self.host}:{self.port}/{self.db}")
            except:
                # 如果服务名连接失败，尝试使用SID连接
                sn = oracle.makedsn(self.host, self.port, sid=self.db)
                self.conn = oracle.connect(self.user, self.pwd, sn)
        else:
            raise TypeError("不支持的数据库类型")
        
        # 创建游标对象
        cur = self.conn.cursor()
        if not cur:
            raise RuntimeError("连接数据库失败")
        else:
            return cur

    def query(self, sql):
        """
            执行查询SQL语句并返回结果
            
            连接数据库，执行查询语句，并将结果按列进行组织。
            自动处理Decimal类型数据，根据精度决定转换为float还是保持字符串格式。
            
            Args:
                sql (str): 要执行的SQL查询语句
            
            Returns:
                list: 查询结果列表，按列组织数据
                    每个子列表包含该列的所有行数据
            
            Example:
                >>> results = sql_conn.query('SELECT id, name FROM users')
                >>> # 返回: [[1, 2, 3], ['Alice', 'Bob', 'Charlie']]
                >>> # 第一个列表是id列，第二个列表是name列
        """
        # 建立数据库连接并获取游标
        cur = self.connect()
        # 执行SQL查询语句
        cur.execute(sql)
        # 获取所有查询结果:[(),(),()]
        resList = cur.fetchall()
        # 关闭数据库连接
        self.conn.close()
        
        # 初始化结果列表，用于按列存储数据
        results = []
        # 遍历每一行数据(xx,xx,xx)
        for res in resList:
            # 遍历行中的每个字段值
            for index, value in enumerate(res):
                # 确保results列表有足够的子列表来存储当前列的数据
                if len(results) < index + 1:
                    results.append([])
                
                # 处理Decimal类型数据
                if isinstance(value, decimal.Decimal):
                    # 检查小数位数，如果超过16位则保持字符串格式以避免精度丢失
                    if len(str(value).split(".")[1]) > 16:
                        results[index].append(str(value))
                    else:
                        # 小数位数不超过16位，转换为float类型
                        results[index].append(float(value))
                else:
                    # 非Decimal类型直接添加
                    results[index].append(value)
        
        return results

    def exec(self, sql):
        """
            执行非查询SQL语句（INSERT、UPDATE、DELETE等）
            
            连接数据库，执行非查询语句，并提交事务。
            适用于数据修改操作，如插入、更新、删除等。
            
            Args:
                sql (str): 要执行的SQL语句（INSERT、UPDATE、DELETE等）
            
            Returns:
                None
            
            Example:
                >>> sql_conn.exec('INSERT INTO users (name, age) VALUES ("Alice", 25)')
                >>> sql_conn.exec('UPDATE users SET age = 26 WHERE name = "Alice"')
                >>> sql_conn.exec('DELETE FROM users WHERE name = "Alice"')
            
            Note:
                此方法会自动提交事务，确保数据修改生效。
                如果执行过程中出现异常，事务会自动回滚。
        """
        # 建立数据库连接并获取游标
        cur = self.connect()
        # 执行SQL语句
        cur.execute(sql)
        # 提交事务，确保数据修改生效
        self.conn.commit()
        # 关闭游标和连接
        cur.close()
        self.conn.close()