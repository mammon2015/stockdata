#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
""" Used to test WebExtractor """

#
# SECTION: MODULE IMPORTS
#
import logging

from data.extended import CaptitalStructureData
from etl.extractor import SinaSSE

#
# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
if __name__ == "__main__":
    #
    # 创建调试用 logging 机制, 仅输出日志到标准错误输出。
    #
    _fmt = logging.Formatter(
        fmt='%(asctime)s %(levelname)8s %(name)s : %(message)s',
        datefmt='%m-%d %H:%M:%S |')
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.DEBUG)  # 在此处设置输出日志的级别
    _ch.setFormatter(_fmt)
    LOG = logging.getLogger("DEBUG")
    LOG.setLevel(logging.DEBUG)  # 在此处设置生成日志的级别
    LOG.addHandler(_ch)

    code = "600036"
    data60036 = CaptitalStructureData(code)

    url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600036.phtml"
    sh600036 = SinaSSE(code, url)
    sh600036.fetch()
    # sh600036.clean()
    sh600036.upload(data60036)
    data60036.update_database()
    # data60036.dump_all()
