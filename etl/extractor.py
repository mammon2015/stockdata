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
import logging
import urllib.request

from lxml import html
from lxml.html.clean import Cleaner

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['Extractor', 'WebExtractor']


#
# SECTION: CLASS DEFINATION
#
#
#   所有数据抓取器的基类.
#       属性:
#           state(str)  用于记录抓取器的状态, 例如 "抓取成功", "转换结束"。
#       方法:
#           fetch()     用于抓取数据
#           upload()    用于上传数据到数据库
#
class Extractor:
    """ Root class of all data extractors """

    def __init__(self):
        # 添加 Logger, 需要放在 super().__init__() 前面以节约资源
        if not hasattr(self, "log"): self.log = logging.getLogger("Extractor")
        # self.log.setLevel(logging.DEBUG)
        super().__init__()
        # 类属性定义部分
        self._state = "已初始化"
        # 初始化本地日志

    def fetch(self):
        """ Fetches data from source, returns None. """
        pass

    def upload(self):
        """ Uploads data to right place, returns None. """
        pass


#
#   网络数据抓取器的超类, Extractor 的子类
#
#   为适应不同的数据库类型, 内部使用 keys 和 data 两个集合变量在存放数据。
#       属性:
#           url(str)    Web 数据的 URL
#           parser      lxml.etree.HTMLParser hmtl 解析器
#           tree        lxml.etree.Element 对象, 存放解析后 html 树的根节点。
#           keys(list)  数据的 key 列表, key 可以是一个列表
#           vals(list)  数据的字段列表, 同样可以存放列表
#       方法:
#           fetch()     重载方法, 实现抓取数据。
#           _purge()    用于抓取后数据的简单清洗, 被 fetch 直接调用。
#           _trans2DHtmlTab
#                       tree 中的数据是若干个 2 标准二维数据表时转换数据用。
#
class WebExtractor(Extractor):
    """ Superclass of all web data extractors """

    def __init__(self, url):
        # 添加 Logger, 需要放在 super().__init__() 前面以节约资源
        if not hasattr(self, "log"): self.log = logging.getLogger("WebExtractor")
        # self.log.setLevel(logging.DEBUG)
        super().__init__()
        # 类属性定义部分
        self.url = url
        self.parser = html.HTMLParser(encoding="gbk",
                                      remove_blank_text=True,
                                      remove_comments=True)
        self.tree = None
        self.keys = []
        self.vals = []
        # DEBUG
        self.log.debug("Instance of 'WebExtractor' initialized.")

    def _purge(self):
        """ Purges some garbage from fetched data, returns bool. """

        cleaner = html.clean.Cleaner(style=True,
                                     page_structure=False,
                                     kill_tags=('a',))
        self.tree = cleaner.clean_html(self.tree)
        # DEBUG:
        self.log.debug("Raw html page was cleaned.")
        # print(html.tostring(self.tree,pretty_print=True,encoding=str))

    def _trans2DHtmlTab(self, table):
        """ Transforms 2D table in 'tree'; returns None. """

        #   本方法用来将标准的二维数据表装换成 key:value 对。
        #   标准的二维数据表, 是指第一行为列标题, 第一列为行标题, 其余为数据
        #   单元。每行数据单元数量应与列标题数相等。
        #
        rows = table.xpath(".//tr")
        if len(rows) <= 1:
            self.log.warn("There is one table has no valid data, skipped.")
            return
        # 先抽取列标题, 否则无法构成后面的数据
        get_text = lambda cell: "" if cell.text is None else cell.text.strip()
        # for head_cell in rows[0].xpath(".//td"):
        #     col_heads.append(head_cell.text.strip())
        col_heads = [get_text(cell) for cell in rows[0].xpath(".//td")]
        # 顺序处理其他行包含的数据
        for row in rows[1:]:
            cells = [get_text(cell) for cell in row.xpath(".//td")]
            if len(cells) != len(col_heads):
                self.log.warn("There is one row has invalid data, skipped.")
                continue
            row_head = cells[0]
            for i in range(1, len(cells)):
                self.keys.append([row_head, col_heads[i]])
                self.vals.append([cells[i], ])

        # DEBUG
        for i in range(0, len(self.keys)):
            print(self.keys[i], self.vals[i])
        self.log.debug("Transform a 2D table, find d records.")

    def fetch(self):
        """ Fetches html from web, returns None. """

        # 抓取 html 网页
        try:
            # DEBUG
            self.log.debug("Try to fetch URL %s" % self.url)
            f = urllib.request.urlopen(self.url)
            self.tree = html.parse(f, self.parser).getroot()
        except:
            self.log.error("Failed to fetch web page from %s" % self.url)
            return

        # DEBUG
        self.log.debug("Page fetched via URL ... OK")

        # 使用私有方法 _purge 清洗抓到的数据, 以节约部分内存。
        self._purge()
        # 完成裸数据清洗后, 将实例状态改为 "抓取成功"
        self._state = "抓取成功"


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
    s600029 = WebExtractor(
        "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600029.phtml")
    s600029.fetch()
