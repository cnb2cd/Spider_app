# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/18 16:22
@desc
"""


class NotSearchConditionException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
