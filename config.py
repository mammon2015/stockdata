#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   包含软件全局变量的包，使用 "import *" 载入
#
""" Containing global variables. """

#
# SECTION: MODULE IMPORTS
#
import confs

import logging
import platform

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ["LOG", "CONFIG_FILE", "confs"]

#
# 创建调试用 logging 机制, 仅输出日志到标准错误输出。
#
_fmt = logging.Formatter(fmt='%(asctime)s %(levelname)8s %(name)s : %(message)s',
                         datefmt='%m-%d %H:%M:%S |')
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)  # 在此处设置输出日志的级别
_ch.setFormatter(_fmt)
LOG = logging.getLogger("DEBUG")
LOG.setLevel(logging.DEBUG)  # 在此处设置生成日志的级别
LOG.addHandler(_ch)

# 配置文件所在路径
if platform.system() == "Windows":
    CONFIG_FILE = "D:\\Coding\\stockdata\\config.ini"
else:
    CONFIG_FILE = "~\\Coding\\stockdata\\config.ini"
