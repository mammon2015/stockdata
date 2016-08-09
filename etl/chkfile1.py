#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 本程序是一个用来检验对通达信 shm.tnf 和 shz.tnf 的解码是否存在错误的工具。
# 目前使用这两个文件提取上海和深圳的股票代码, 解码模板如下:
#       HEAD: <40shii
#     RECORD: <23s49sIBc8sBBB183sBBBBfBI29s
#
#      简化为: <23s49s204sfBI29s

#
#  Modules import section
#
from struct import unpack

path = "/Users/mammon/Coding/pyStock/szm.tnf"
data = []
head_size = 50
record_size = 314

f = open(path, "rb")

buffer = f.read(head_size)
head = unpack("<40shii", buffer)

while True:
    buffer = f.read(record_size)
    if len(buffer) < record_size:
        break
    else:
        record_data = unpack("<23s49sIBc8sBBB183sBBBBfBI29s", buffer)
        data.append(record_data)
f.close()

for i in data:

    # i[0] 23位长的股票代码, 截去末尾的 0x00 后不超过 6 位
    code = i[0].strip(b"\x00").decode("gbk")
    if len(code) > 6:
        print(code)
        raise ValueError

    # i[1] 49位长的股票代码, 截去末尾的 0x00 后不超过 8 位
    name = i[1].strip(b"\x00").decode("gbk")
    if len(name) > 8:
        print(code, name)
        raise ValueError

    # i[2] 未知 int 类标识, 取值为 2 或 3
    if not i[2] in [2, 3]:
        print("2:", code, i[2])

    # i[3] 未知 unsinged char 类标识, 取值为 32 或 200
    if not i[3] in [32, 200]:
        print("3:", code, i[3])

    # i[4] 未知 unsinged char 类标识, 取值为 32 或 200
    if not i[4].decode() in ['A', 'B']:
        print("4:", code, i[4])

    # print(code, i[2], i[3], i[4].decode())

    # i[5] 全零 长度 8 字节的空白
    if len(i[5].strip(b"\x00")) > 0:
        print("5:", code, i[5])

    # i[6] 到 i[8] 未知的 3 个标识位, 可能用于分类或板块

    # i[9] 全零 长度 183 个字节的空白
    if len(i[9].strip(b"\x00")) > 0:
        print("9:", code, i[9])

    # i[10] 到 i[13] 未知 3 个标识位, 可能用于分类或板块

    # i[14] 最近收盘价格, 这时一个浮点数, 需要对小数点后 2 位取整, 否则计算有误。

    # i[15] 标示是深圳(0)还是上海(1)
    if not i[15] in [0, 1]:
        print("15:", code, i[15])

    # i[16] 未知 unsinged int 类标识, 取值为 1
    if not i[16] in [1]:
        print("16:", code, i[16])

    # i[17] 29位长的股票缩写, 截去末尾的 0x00 后不超过 8 位
    code = i[17].strip(b"\x00").decode("gbk")
    if len(code) > 8:
        print(code)
        raise ValueError

#
# Standard boilerplate to call right function for testing
#
# if __name__ == "__main__":
