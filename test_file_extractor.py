#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
""" Used to test FileExtractor """

#
# SECTION: MODULE IMPORTS
#
from config import *
from etl.connector import MysqlConn
from etl.extractor import TdxCodeFile

import platform

#
# from etl.connector import DBConn
# from etl.extractor import TdxCodeFile

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

    # Define data file path based on Windows or Mac
    system_name = platform.system()
    if system_name == "Windows":
        file_path = "E:\Stock\TDX\T0002\hq_cache\shm.tnf"
    else:
        file_path = "/home/mammon/Programming/shm.tnz"
    sh_code_e = TdxCodeFile("上海", file_path, **confs.DB_STR)
    sh_code_e.fetch()
    sh_code_e.upload()
