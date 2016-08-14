#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   包含软件全局变量的包，使用 "import *" 载入
#
""" Containing global variables. """

#
# SECTION: MODULE IMPORTS
#
import platform

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ["CONFIG_FILE", "DB_STR"]

# 配置文件所在路径
if platform.system() == "Windows":
    CONFIG_FILE = "D:\\Coding\\stockdata\\config.ini"
else:
    CONFIG_FILE = "~\\Coding\\stockdata\\config.ini"

DB_STR = {
    'user': 'mammon',
    'password': 'leon',
    'host': '192.168.1.11',
    'database': 'stockdata'
}