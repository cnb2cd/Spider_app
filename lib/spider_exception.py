# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/11 19:10
@desc email send
"""
import logging

log = logging.getLogger()


class SpiderException(Exception):
    def __init__(self, m, *args):
        self.args = args
        sr = 'exception messgae is :'
        for my_info in args:
            sr = sr + str(my_info) + ","
        sr = sr + "Trace message is{}:" + m
        log.error(sr)
