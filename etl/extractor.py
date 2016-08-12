#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件包含 Extractor 系列中通用超类的定义, 包含:
#       Extractor
#           WebExtractor
#               SinaSSE
#           FileExtractor
#               TdxCodeFile
#
""" Module contains the classes of used to extrac data from source.  """

#
# SECTION: MODULE IMPORTS
#
import logging
from struct import unpack
from urllib import request

from lxml import html
from lxml.html.clean import Cleaner

from config import *
from etl.connector import MysqlConn
from etl.nomalizer import Normalizer

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['SinaSSE', 'TdxCodeFile']

#
# SECTION: DEFINE GLOBAL VARIABLES
#
word_pair = Normalizer(**confs.DB_STR)  # 用来纠正非规范词的对象


#
# SECTION: CLASS DEFINATION
#
#   所有数据抓取器的基类.
#       属性:
#           state(str)  用于记录状态, 例如 "抓取成功", "转换结束"。
#       方法:
#
class Extractor:
    """ Root class of all data extractors """

    def __init__(self):
        super().__init__()
        # 类属性定义部分
        self._state = "已初始化"
        # 添加类调试使用 Logger
        self.log = logging.getLogger("DEBUG")
        self.log.info("'Extractor' instance is initialized.")


#
#   WebExtractor 网络数据抓取器的超类, Extractor 的子类
#
#       属性:
#           url(str)    Web 数据的 URL
#           parser      lxml.etree.HTMLParser hmtl 解析器
#           tree        lxml.etree.Element 对象, 存放解析后 html 树的根节点。
#       方法:
#           fetch()     重载方法, 实现抓取数据。
#           _purge()    用于抓取后数据的简单清洗, 被 fetch 直接调用。
#           _trans2DHtmlTab
#                       tree 中的数据是若干个 2 标准二维数据表时转换数据用。
#
class WebExtractor(Extractor):
    """ Superclass of all web data extractors """

    def __init__(self, url):
        super().__init__()
        # 类属性定义部分
        self.url = url
        self.data = []

    def _purge(self):
        """ Purges some garbage from fetched data, returns bool. """

    def _add2DHtmlTab(self, table):
        """ Add data in a 2D table to 'tree', returns list of data. """

        # 本方法用来将标准的二维数据表装换成列表 [行标题, 列标题, 单元数据]。
        # 二维数据表格式必须标准, 即第一行为列标题, 第一列为行标题，每行数据单
        # 元数量与列标题数相等。
        #
        rows = table.xpath(".//tr")
        # 先抽取列标题, 否则无法构成后面的数据
        get_text = lambda tag: "" if tag.text is None else tag.text.strip()
        colheads = [get_text(td) for td in rows[0].xpath(".//td")]
        # 处理包含的数据
        data = []
        for row in rows[1:]:
            cells = [get_text(cell) for cell in row.xpath(".//td")]
            for i in range(1, len(cells)):
                self.data.append([cells[0], colheads[i], cells[i]])
        # DEBUG
        self.log.info("One table found, %d rows found." % len(rows))

    def fetch(self):
        """ Fetches html from web, returns None. """

        # 抓取 html 网页
        self.log.info("Start to fetch page : %s" % self.url)
        parser = html.HTMLParser(encoding="gbk",
                                 remove_blank_text=True,
                                 remove_comments=True)
        # try:
        f = request.urlopen(self.url)
        self.tree = html.parse(f, parser).getroot()
        self.log.info("HTML page fetched.")

        # 数据的初步清洗, 以节约部分内存。
        html_cleaner = Cleaner(style=True,
                               page_structure=False,
                               kill_tags=('a',))
        self.tree = html_cleaner.clean_html(self.tree)
        # 完成裸数据清洗后, 将实例状态改为 "抓取成功"
        self._state = "抓取成功"
        # DEBUG
        self.log.info("HTML tree purged.")
        # print(html.tostring(self.tree,encoding=str))


#
#   FileExtractor 文件数据抓取器的超类, Extractor 的子类
#
#       属性:
#           path(str)   文件数据的 PATH
#       方法:
#           fetch()     重载方法, 实现抓取数据。
#
class FileExtractor(Extractor):
    """ Superclass of all web data extractors """

    def __init__(self, path):
        super().__init__()
        # 类属性定义部分
        self.path = path


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
        super().__init__(url)
        self.code = code

    def fetch(self):
        """ Re-define 'fetch()' method to add data transfrom. """

        # 调用其父类的 fetch 完成网页抓取和基本数据清洗
        super().fetch()

        # 数组转换，将 fetch 得到的 html 树转换为记录的列表。
        #   新浪 "股本结构" 网页的数据包含在多个带 id 的表格中。
        tables = self.tree.xpath("//table[@id]")
        for table in tables:
            # 每个数据都有一个无用的表头，直接删除。
            table.xpath(".//thead")[0].drop_tree()
            self._add2DHtmlTab(table)
        self._state = ("转换成功" if len(self.data) > 0 else "转换失败")
        # DEBUG
        self.log.info("Total %d data records found in page." % len(self.data))
        # for i in self.data: print(i)

    def clean(self):
        """ Clean data with advanced logic. """
        del_list = []
        for i, rec in enumerate(self.data):
            rec[0] = word_pair.get_fix(rec[0])
            # 如果第一个字段规范化结果是空的话，删除整个记录。
            if rec[0] == "":
                del_list.append(i)
                continue
            # 第三个字段主要解决数字中的 "万股" 的问题
            if rec[2].find("万股") != -1:
                s = rec[2].split("万股")[0]
                f = float(s) * 10000 + 0.005
                rec[2] = int(f)
        del_list.sort(reverse=True)
        for i in del_list:
            self.data.pop(i)
        for rec in self.data: print(rec)


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

    def __init__(self, market, path, **kw):
        super().__init__(path)
        # 类属性定义部分
        self.market = market
        self.data = []
        self.mysql = MysqlConn(**kw)
        self.log.info("Code file extractor initialized for %s." % market)

    def fetch(self):
        """"""
        f = open(self.path, "rb")
        # 处理文件头
        head_size = 50  # 此处定义了文件头部的大小
        conv_date = lambda x: date(x // 10000, x // 100 % 100, x % 100)
        buffer = f.read(head_size)
        date = conv_date(unpack("<40shii", buffer)[2])
        # DEBUG
        self.log.info("Get date from head of data file = %s" % date)

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
                self.data.append(
                    [v1.decode("gbk"), self.market, v2.decode("gbk"),
                     v4.decode("gbk")])
        f.close()
        # DEBUG
        self.log.info(
            "Data fetched from file, total %d records." % len(self.data))
        # for i in range(0,len(self.keys)):
        #     print(self.keys[i], self.vals[i])

    def upload(self):
        """ Update data to database. """
        # 将数据表读入内存
        self.log.info("Start to update database.")
        records = self.mysql.select(
            "SELECT code, market, name, abbreviation, timestamp FROM codes;")

        # DEBUG
        for r in records:
            print(r)  # SECTION: SELFTESTING


class Normalizer():
    """ A class which method used to nomalizer """

#
#   Selftesing syntax: python <filename>
#
# if __name__ == "__main__":
