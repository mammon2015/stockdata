#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件包含在 FileExtractor 的基础上, 定义包含特定数据和逻辑的子类:
#       TdxCodeFile
#
""" Module contains the superclasses of 'Extractor'. """

#
# SECTION: MODULE IMPORTS
#
from etl.extractor import FileExtractor

import datetime

from struct import unpack

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['TdxCodeFile']


#
#   TdxCodeFile
#
#       属性:
#           path(str)   文件数据的 PATH
#       方法:
#           fetch()     重载方法, 实现抓取数据。
#
class TdxCodeFile(FileExtractor):
    """ Superclass of all web data extractors """

    def __init__(self, market, path):
        super().__init__(path)
        # 类属性定义部分
        self.market = market
        self.path = path
        self.keys = []
        self.vals = []

    def fetch(self):
        """"""
        f = open(self.path, "rb")
        # 处理文件头
        head_size = 50  # 此处定义了文件头部的大小
        conv_date = lambda x: datetime.date(x // 10000, x // 100 % 100, x % 100)
        buffer = f.read(head_size)
        date = conv_date(unpack("<40shii", buffer)[2])
        # DEBUG
        print("Get date from head of data file =", date)

        # 处理正文部分的数据记录
        recd_size = 314  # 此处定义了记录的直接长度
        conv_cstr = lambda s: s.strip(b"\x00")
        while True:
            buffer = f.read(recd_size)
            if len(buffer) < recd_size:  # 如果读到的记录长度不对, 意味 EOF
                break
            else:
                v1, v2, v3, v4 = [conv_cstr(s) for s in
                                  unpack("<23s49s213s29s", buffer)]
                # print(v1.decode("gbk"),v2.decode("gbk"),v4.decode("gbk"))
                self.keys.append([v1.decode("gbk"),])
                self.vals.append([v2.decode("gbk"),v4.decode("gbk")])
        f.close()
        print(self.keys,self.vals)



# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
if __name__ == "__main__":
    # 构造变量, 或调用函数以对本模块进行自我测试
    # s600029 = WebExtractor(
    #     "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600029.phtml")
    # s600029.fetch()

    codesSH = TdxCodeFile("上海", "/Users/mammon/Programming/szm.tnf")
    codesSH.fetch()
