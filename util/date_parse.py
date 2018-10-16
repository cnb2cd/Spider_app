# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/15 19:03
@desc
"""

import time
import datetime

def get_today_date(format_str='%Y-%m-%d'):
    """
    按格式获取当天日期
    :param format_str:
    :return:
    """
    today_str = time.strftime(format_str, time.localtime())
    return today_str


# 1.把datetime转成字符串
def date_str(dt, format_type):
    return dt.strftime(format_type)


# 2.把字符串转成datetime
def str_datetime(st, format_type):
    return datetime.datetime.strptime(st, format_type)


# 3.把字符串转成时间戳形式
def str_timestamp(st, format_type):
    return time.mktime(time.strptime(st, format_type))


# 4.把时间戳转成字符串形式
def timestamp_str(sp, format_type):
    return time.strftime(format_type, time.localtime(sp))


# 5.把datetime类型转外时间戳形式
def datetime_timestamp(dt):
    return time.mktime(dt.timetuple())
