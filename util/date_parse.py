# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/15 19:03
@desc
"""

import time


def get_today_date(format_str='%Y-%m-%d'):
    """
    按格式获取当天日期
    :param format_str:
    :return:
    """
    today_str = time.strftime(format_str, time.localtime())
    return today_str


