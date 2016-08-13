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
# Normalizer 类
#
#   属性:
#       word_pairs
#   方法:
#
# TODO: 将其转化为一个单例类，以节约内存占用。
#
class WordNormalizer():
    """ A class which method used to nomalizer """

    def __init__(self, **kw):
        super().__init__()
        # 类属性初始化
        self.word_pairs = {}
        # 从数据库中读取非规范词表
        mysql = connector.connect(**kw)
        cursor = mysql.cursor()
        cursor.execute("SELECT nonstd_word, std_word FROM nonstd_words;")
        self.word_pairs = {r[0]: r[1] for r in cursor}
        mysql.close()

    def fix_word(self, word):
        """ Try to fix the word. """
        if word in self.word_pairs.keys():
            return self.word_pairs[word]
        else:
            return word

    def rm_quant(self, word):
        """ Remove quantifier from string and return the corrent number. """
        # 通过查找字符串中是否存在 '万' 来判断是否存在量词。
        if word.find("万") >= 0:
            num_str = word.split("万")[0]   # 拆出 "万" 前的数字字符串
            num_f = float(num_str) * 10000
            num_n = int(num_f + 0.05)       # 浮点数乘 10000 后可能出现小数
            return num_n
        # 如果执行到这里说明没有找到任何量词，直接返回原值
        return word