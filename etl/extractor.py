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
import urllib.request

from lxml import html
from lxml.html.clean import Cleaner
from struct import unpack


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
#           keys(list)  数据的 key 列表, key 可以是一个列表
#           vals(list)  数据的字段列表, 同样可以存放列表
#       方法:
#           fetch()     用于抓取数据
#           upload()    用于上传数据到数据库
#
class Extractor:
    """ Root class of all data extractors """

    def __init__(self):
        super().__init__()
        # 类属性定义部分
        self._state = "已初始化"
        self.keys = []
        self.vals = []

    def fetch(self):
        """ Fetches data from source, returns None. """
        pass

    def upload(self):
        """ Uploads data to right place, returns None. """
        pass


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
        self.parser = html.HTMLParser(encoding="gbk",
                                      remove_blank_text=True,
                                      remove_comments=True)
        self.tree = None

    def _purge(self):
        """ Purges some garbage from fetched data, returns bool. """

        cleaner = html.clean.Cleaner(style=True,
                                     page_structure=False,
                                     kill_tags=('a',))
        self.tree = cleaner.clean_html(self.tree)
        # print(html.tostring(self.tree,pretty_print=True,encoding=str))

    def _trans2DHtmlTab(self, table):
        """ Transforms 2D table in 'tree'; returns None. """

        #   本方法用来将标准的二维数据表装换成 key:value 对。
        #   标准的二维数据表, 是指第一行为列标题, 第一列为行标题, 其余为数据
        #   单元。每行数据单元数量应与列标题数相等。
        #
        rows = table.xpath(".//tr")
        if len(rows) <= 1:  # 小于等于 1 行的显然不是合法表格
            return
        # 先抽取列标题, 否则无法构成后面的数据
        get_text = lambda cell: "" if cell.text is None else cell.text.strip()
        colheads = [get_text(cell) for cell in rows[0].xpath(".//td")]
        # 顺序处理其他行包含的数据
        for row in rows[1:]:
            cells = [get_text(cell) for cell in row.xpath(".//td")]
            if len(cells) != len(colheads):
                continue
            for i in range(1, len(cells)):
                self.keys.append([cells[0], colheads[i]])
                self.vals.append([cells[i], ])

        # DEBUG
        for i in range(0, len(self.keys)):
            print(self.keys[i], self.vals[i])

    def fetch(self):
        """ Fetches html from web, returns None. """

        # 抓取 html 网页
        try:
            f = urllib.request.urlopen(self.url)
            self.tree = html.parse(f, self.parser).getroot()
        except:
            raise ("Error found while retrieving page.")

        # 使用私有方法 _purge 清洗抓到的数据, 以节约部分内存。
        self._purge()
        # 完成裸数据清洗后, 将实例状态改为 "抓取成功"
        self._state = "抓取成功"


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
        """ Redinfe 'fetch()' method to add data transfrom. """
        super().fetch()
        self.transfrom()

    def transfrom(self):
        """ Transforms html data, return None. """

        # 如果网页结构或数据来源发生修改, 主要修改这个字符串。
        tables = self.tree.xpath("//table[@id]")
        # 找到数据后, 由于新浪的网页中有一个无用的表头, 因此要删去
        for table in tables:
            theads = table.xpath(".//thead")
            if len(theads) == 1:
                theads[0].drop_tree()
            else:  # 没有或超过 1 个 thead 都表示本数据表有问题, 因此跳过。
                continue
            self._trans2DHtmlTab(table)
        if len(self.keys) > 0:
            print("数据转换成功")
        else:
            print("数据转换失败")


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
        conv_date = lambda x: datetime.date(x // 10000,
                                            x // 100 % 100, x % 100)
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
                self.keys.append([v1.decode("gbk"), ])
                self.vals.append(
                    [v2.decode("gbk"), v4.decode("gbk")])
        f.close()
        print(self.keys, self.vals)


# SECTION: SELFTESTING
#
#   Selftesing syntax: python <filename>
#
if __name__ == "__main__":
    # 构造变量, 或调用函数以对本模块进行自我测试
    s600029 = SinaSSE(
        "600029",
        "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/600029.phtml")
    s600029.fetch()

    # codesSH = TdxCodeFile("上海", "/Users/mammon/Programming/szm.tnf")
    # codesSH.fetch()
