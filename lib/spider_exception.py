# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/11 19:10
@desc email send
"""
import logging
log = logging.getLogger()
class spiderexception(Exception):
    def __init__(self, m, *args):
        self.args = args
        s = 'exception messgae is : '
        for my_info in args:
           s = s + my_info + ","
        s = str + "Trace message is{}:" + m
        log.error(str)








