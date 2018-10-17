# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/16 20:56
@desc
"""

file_path = 'C:/Users/82677/PycharmProjects/Spider_app/content/'


def file_out(file, content):
    path = file_path + file
    w = open(path, 'w')
    w.write(content)
    w.close()