#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件包含 DBConn 系列中通用超类的定义, 包含:
#       DBConn
#           MySQLConn
#
""" Module contains the superclasses of 'Extractor'. """

#
# SECTION: MODULE IMPORTS
#
import logging
import mysql.connector
import mysql.connector.errorcode

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['DBConn']


#
# SECTION: CLASS DEFINATION
#
#   数据库连接类的基类
#       属性:
#           _state          数据路连接的状态
#       方法:
#           update          写数据到数据库的接口
#           select          从数据库读数据的借口
#
class DBConn():
    """ SuperClass of database connect classes. """

    def __init__(self):
        super().__init__()
        # 添加类调试使用 Logger
        self.log = logging.getLogger("DEBUG")

    def update(self, sql_str, keys, vals):
        pass

    def select(self, sql_str):
        pass


#
#   MySQL 数据库连接类
#       属性:
#           _state          数据路连接的状态
#       方法:
#           __init__        重载构造函数，主要实现数据链接的建立
#           update          重载，具体实现数据写入逻辑
#           select          重载，具体实现数据读取逻辑
#
class MysqlConn(DBConn):
    """ DBConn's subclass used to connect MySQL databse. """
    username = None
    password = None
    hostname = None
    database = None

    def __init__(self, **kw):
        super().__init__()
        # 使用可变数量参数的例子, 只有和已定义属性同名的参数才能被接受。
        for name, value in kw.items():
            if not hasattr(self, name):
                raise TypeError("Unknown parameter: %s=%r" % (name, value))
            setattr(self, name, value)
        # 判断是否所有的链接串变量都已经设置。
        if not all((self.username, self.password, self.hostname, self.database)):
            raise ValueError("Database connection string lack of parameters")
        # 创建数据库链接字符串
        self.log.info("Try to connect MySQL database.")
        try:
            self.conn = mysql.connector.connect(user=self.username,
                                                password=self.password,
                                                host=self.hostname,
                                                database=self.database)
            self._state = "数据库已连接"
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.log.error("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.log.error("Database does not exist")
            else:
                print(err)
            raise (err)
        # DEBUG
        self.log.info("Database connected.")

    def update(self, sql_str, keys, vals):
        super().update()

    def select(self, sql_str):
        """ Get and return result set of giving SQL."""
        cursor = self.conn.cursor()
        cursor.execute(sql_str)
        return list(cursor)

    def get_conn(self):
        if self._state in ["数据库已连接", ]:
            return self.conn
        else:
            return None

    def __del__(self):
        if self._state in ["数据库已连接。", ]:
            self.conn.close()
            self.log.info("数据库链接已关闭。")

#
# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
# if __name__ == "__main__":
