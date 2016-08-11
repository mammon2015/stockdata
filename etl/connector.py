#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件包含 Extractor 系列中通用超类的定义, 包含:
#       Extractor
#           WebExtractor
#           FileExtractor
#
""" Module contains the superclasses of 'Extractor'. """

#
# SECTION: MODULE IMPORTS
#
import mysql.connector
import mysql.connector.errorcode

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['', ]


#
# SECTION: CLASS DEFINATION
#
#   所有数据抓取器的基类.
#       属性:
#       方法:
#
class DBConn():
    """"""
    username = None
    password = None
    hostname = None
    database = None

    std_keys = {}

    def __init__(self, **kw):
        super().__init__()
        # 使用可变数量参数的例子, 只有和已定义属性同名的参数才能被接受。
        for name, value in kw.items():
            if not hasattr(self, name):
                raise TypeError("Unknown parameter: %s=%r" % (name, value))
            setattr(self, name, value)
        if not all((self.username, self.password, self.hostname, self.database)):
            raise ValueError("Database connection string lack of parameters")
        try:
            self.conn = mysql.connector.connect(user=self.username,
                                                password=self.password,
                                                host=self.hostname,
                                                database=self.database)
            self._state = "数据库已连接"
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def _std_key(self, word):
        """ Replace any non-standard word in key to standard one. """
        # 首先检查是否存在本地字典, 如果没有, 从数据库抓一份。
        if not self.std_keys:       # None 或者 {}
            if not self._state in ("数据库已连接",):
                raise ValueError("No valid database connection.")
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM stockdata.typos;")
            self.std_keys = {r[0]:r[1] for r in cursor}
            # DEBUG
            print(self.std_keys)

        # 依次检查输入参数, 如果是非标准名则将其替换
        if word in self.std_keys.keys():
            return self.std_keys[word]
        else:
            return word

    def __del__(self):
        if hasattr(self,"conn") and self.conn is not None:
            self.conn.close()


#
# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
# if __name__ == "__main__":

db_conn_str = {
    'username': 'mammon',
    'password': 'leon',
    'hostname': '192.168.1.11',
    'database': 'stockdata'
}

db_mysql = DBConn(**db_conn_str)
print(db_mysql._std_key("·变动原因"))
