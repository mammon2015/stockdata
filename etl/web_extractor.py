#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件包含在 WebExtractor 的基础上, 定义包含特定补票数据的和定位逻辑的子类:
#       SinaSSE
#
""" Module contains the web extrators based on WebExtractor """

#
# SECTION: MODULE IMPORTS
#
from etl.extractor import WebExtractor

import logging

from lxml import html

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['SinaSSE']


#
# SECTION: CLASS DEFINATION
#
#   新浪股本数据抓取器, WebExtractor 的子类
#
#   通过重载方法 transfrom(), 实现对不同数据种类和不同数据来源的 html 数据抽取
#   的转换。由于股票基本面数据大多以数据表格的方式提供, 因此抽取相关 html 的工
#   作大体为, 首先定位包含数据的容器标签; 其次删除容器中不包含数据的表格; 最后
#   将表格格式标准化。
#
#       属性:
#           code(str)   数据所属的股票代码
#       方法:
#           transform() 重载方法, 实现抓取数据。
#
class SinaSSE(WebExtractor):
    """Class for 'capital structure of a Share from Sina'"""

    def __init__(self, code, url):
        # 添加 Logger, 需要放在 super().__init__() 前面以节约资源
        if not hasattr(self, "log"): self.log = logging.getLogger(code)
        self.log.setLevel(logging.DEBUG)
        super().__init__(url)
        self.code = code

    def transfrom(self):
        """ Transforms html data, return None. """

        # 定义一个面向整个文档的 xpath, 并使用其定位 html 中的数据部分
        strXPath = "//table[@id]"
        tables = self.tree.xpath(strXPath)
        # 处理未找到数据的情况
        if tables == []:
            self.log.warn("No data found for %s, source url is " % self.code,
                          self.url)
            self._state = "转换失败"
            return
        self.log.info("Found total %d tables containing data." % len(tables))
        # 找到数据后, 由于新浪的网页中有一个无用的表头, 因此要删去
        for table in tables:
            theads = table.xpath(".//thead")
            if len(theads) == 1:
                theads[0].drop_tree()
            else:
                # 没有或超过 1 个 thead 都表示本数据表有问题, 因此跳过。
                continue
            self._trans2DHtmlTab(table)


# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
if __name__ == "__main__":
    # 自我测试用的 logging 机制, 仅输出错误到标出错误输出。
    log = logging.getLogger("MAIN")
    log.setLevel(logging.DEBUG)  # 在此处设置生成日志的级别
    ch1 = logging.StreamHandler()
    ch1.setLevel(logging.DEBUG)  # 在此处设置输出日志的级别
    fmt = logging.Formatter(
        fmt='%(asctime)s %(levelname)8s %(name)s : %(message)s',
        datefmt='%m-%d %H:%M:%S |')
    ch1.setFormatter(fmt)
    log.addHandler(ch1)

    # 构造变量, 或调用函数以对本模块进行自我测试
    s600029 = SinaSSE(
        "600029",
        "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600029.phtml")
    s600029.fetch()
    s600029.transfrom()
