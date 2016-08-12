#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
""" Used to test WebExtractor """

#
# SECTION: MODULE IMPORTS
#
from config import *

from etl.extractor import SinaSSE

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['', ]

#
# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
if __name__ == "__main__":
    url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600036.phtml"
    code = "600036"
    sh600036 = SinaSSE(code, url)
    sh600036.fetch()
    sh600036.clean()
