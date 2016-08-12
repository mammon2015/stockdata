#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
#
#   本文件中的 Normalizer 类用将名字标准化，转化带单位的数字等。
#       Extractor
#           WebExtractor
#               SinaSSE
#           FileExtractor
#               TdxCodeFile
#
""" A class containing method used to normalize words. """

#
# SECTION: MODULE IMPORTS
#
from mysql import connector

#
# SECTION: DEFINE EXTERNAL INTERFACE
#
__all__ = ['NormalizerClass']


#
#   Normalizer 类
#       属性:
#
#       方法:
#
#       TODO: 将其转化为一个单例类，以节约内存占用。
#
class Normalizer():
    """ A class which method used to nomalizer """

    def __init__(self, **kw):
        super().__init__()
        # 类属性初始化
        self.pairs = {}
        # 从数据库中读取非规范词表
        mysql = connector.connect(**kw)
        cursor = mysql.cursor()
        cursor.execute("SELECT nonstd_word, std_word FROM nonstd_words;")
        self.pairs = {r[0]: r[1] for r in cursor}
        # DEBUG
        print(self.pairs)

    def get_fix(self, word):
        """ Try to fix the word. """
        return self.pairs[word] if word in self.pairs.keys() else word
