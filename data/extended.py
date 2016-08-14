#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
# 本文件包含 Extractor 系列中通用超类的定义, 包含:
#
#       ExtDataPiece
#           StructureData
#
""" Classes for storing extended data for a particular share.  """

#
# SECTION: MODULE IMPORTS
#
import logging
from decimal import Decimal

import mysql.connector

import etl.stdzn
from config import *

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['NumExtDataPiece', 'NumExtDataPiece']

#
# SECTION: GLOBAL VAIRABLE DEFINATION
#
_word_stdnz = etl.stdzn.WordSTDZN()


#
# SECTION: GLOBAL FUNCTION DEFINATION
#
# _assorted_max
#
#   用来扫描一个二维列表，找到分类的最大值。分类一定按照二维列表的第一列，
#   找最大值的列在函数第二个参数中指定。
#
def _assorted_max(lst2d, val_idx):
    """ Return a dict with assorted key and max vlue index. """

    # 如果是一个空列表，直接返回空字典
    if len(lst2d) == 0: return dict()
    # 二维表宽度必须大于比较列索引
    if len(lst2d[0]) <= val_idx: raise ValueError("Wrong column index!")
    idx = {}
    for i, rec in enumerate(lst2d):
        key, val = rec[0], rec[val_idx]
        if key in idx.keys():
            if lst2d[idx[key]][val_idx] < val: idx[key] = i
        else:
            idx[key] = i
    return idx


#
# SECTION: CLASS DEFINATION
#
# ExtDataPiece
#
#   所有数据抓取器的基类.
#       属性:
#           log         日志对象
#       方法:
#
class ExtDataPiece:
    """ Base class for Extended Data of a share. """

    def __init__(self, code):
        super().__init__()
        # 类属性定义部分
        # 添加类调试使用 Logger
        self.log = logging.getLogger("DEBUG")
        self.log.info("'ExtDataPiece' instance is initialized.")


#
# ExtDataPiece
#
#   所有数据抓取器的基类.
#       属性:
#           code            股票代码
#           type            数据类型，比如："股本数据"
#           data            存放数据的列表，保持数据原始数据类型。
#           new             指向最新值的索引，键值为不同的项目。
#           insert_idx      指向非本地数据的索引，即需要上传到数据库的。
#           update_idx      指向已变更数据的索引，需要在数据库中更新。
#       方法:
#           _read_from_db   从数据库中读取数据
#           dump_all        输出全部数据，调试用
#           dump_now        输出最新数据，调试用
#
class NumExtDataPiece(ExtDataPiece):
    """ Extend ExtDataPiece to store numberic data. """

    def __init__(self, code):
        super().__init__(code)
        # 类属性定义部分
        self.code = code
        self.type = ""
        self.table = ""
        self.data = []
        self.index = {}
        self.recent = {}
        self.insert_idx = []
        self.update_idx = []

    def _read_from_db(self):
        """ Read data from data base.

        This is a private method usually used during initialization,
        It will check class attributes for see whether is callable.
        """
        # 检查类属性，确认其是否可以正常工作。
        # 从数据库中读取数据
        db_conn = mysql.connector.connect(**DB_STR)
        cursor = db_conn.cursor()
        cursor.execute("SELECT item, date, value "
                       "FROM num_extend_data "
                       "WHERE code = %s AND type = %s",
                       (self.code, self.type))
        self.data = [list(rec) for rec in cursor]
        self.log.info("Read %d rows from database" % cursor.rowcount)
        cursor.close()
        db_conn.close()
        # 使用公共函数 _assorted_max 创建数据索引
        # self.new = _assorted_max(self.data, 1)

    def add_one(self, data):
        """ Add data via a list. """
        # 将参数给定的数据加入，假定参数是一条记录形式，且数据正确。
        # 数据是否合法应该由其调用者检查，因为在这个类层级，数据含义是未知的。
        #
        # 确认数据类型是数字类型，即 Decimal
        if not isinstance(data[2], Decimal): return False
        # 如果没有索引属性则建立索引属性
        self._chk_index()
        # 检查值是否已经存在, 已存在则更新值
        key = str(data[0]) + str(data[1])
        if key in self.index.keys():
            pt = self.index[key]
            old = self.data[pt]
            if old[2] != data[2]:
                self.data[pt][2] = data[2]
                self.update_idx.append(pt)   # 记录该条数据需要更新到数据库
                self.log.info("%s %s %d changed to %d" %
                              (old[0], old[1], old[2], data[2]))
        # 不存在则加入
        else:
            pt = len(self.data)
            self.data.append(data)
            self.insert_idx.append(pt)
            # 在索引中加入新 key
            self.index[key] = pt
            # 加入的值可能影响最新值索引，因此将其置空。
            self.recent={}
        return True

    def update_database(self):
        """ Update changed data to database. """

        # 首先根据 self.insert_idx 将新数据写入数据库
        db_conn = mysql.connector.connect(**DB_STR)
        cursor = db_conn.cursor()
        # 准备写入数据库的数据列表
        insert_list = [[self.code, self.type] + self.data[n]
                       for n in self.insert_idx]
        cursor.executemany("INSERT INTO num_extend_data "
                           "(code, type, item, date, value) "
                           "VALUES (%s, %s, %s, %s, %s)", insert_list)
        db_conn.commit()
        self.insert_idx=[]
        # 其次根据 self.update_idx 更新数据库中的记录

    def _chk_recent(self):
        """ Check if self.recent existend and have valid value. """
        if self.recent == {}:
            self.recent = _assorted_max(self.data, 1)

    def _chk_index(self):
        """ Check if self.index existed and have valid value. """
        if self.index == {}:
            for idx, rec in enumerate(self.data):
                key = str(rec[0]) + str(rec[1])
                self.index[key] = idx

    def dump_all(self):
        """ Print all data. """
        for r in self.data: print(r)
        print ("Total record number is %d" % len(self.data))

    def dump_now(self):
        """ Print now data """
        self._chk_recent()
        for i in self.recent.values():
            print(self.data[i])


#
# CaptitalStructureData
#
#   所有数据抓取器的基类.
#       属性:
#       方法:
#
class CaptitalStructureData(NumExtDataPiece):
    """ Class used to store Capital Structure data. """

    def __init__(self, code):
        super().__init__(code)
        # 类属性定义部分
        self.type = "股本结构"
        self.table = "num_extend_data"
        # 调用类方法从数据库读取数据
        self._read_from_db()
