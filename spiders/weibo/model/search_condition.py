# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/18 12:01
@desc
"""

from urllib.parse import quote
import logging

logger = logging.getLogger()


class SearchCondition:

    # 搜索的链接前缀
    prefix_url = "https://s.weibo.com/weibo/"
    ser_type_values = {
                        "typeall": "typeall=1",  # 全部
                        "hot": "xsort=hot",  #  热门
                        "ori": "scope=ori",  # 原创
                        "atten": "atten=1",  # 关注的人
                        "vip": " vip=1",  # 认证的用户
                        "category": "category=4",  # 媒体
                        "viewpoint": "viewpoint=1"  # 观点
                      }

    ser_sub_values = {
                        "suball": "suball=1",  # 包含全部
                        "haspic": "haspic=1",  # 有图
                        "hasvideo": "hasvideo=1",  # 有视频
                        "hasmusic": "hasmusic=1",  # 有音乐
                        "haslink": "haslink=1"  # 有链接
                     }

    def __init__(self, ser_word=None, ser_type="typeall", ser_sub="suball", ser_time_start=None, ser_time_end=None,
                 ser_localtion=None):
        """
        搜索类型
        :param ser_type:
        :param ser_sub:
        :param ser_time_start:
        :param ser_time_end:
        :param ser_localtion:
        """
        self.ser_type = ser_type
        self.ser_sub = ser_sub
        self.ser_time_start = ser_time_start
        self.ser_time_end = ser_time_end
        self.ser_localtion = ser_localtion
        self.ser_word = ser_word
        self.ser_word_quote = quote(quote(self.ser_word, encoding="utf-8"), encoding="utf-8")
        self.page = 1

    def get_ser_condition_url(self):
        return self.prefix_url + self.ser_word_quote + "&" + self.get_ser_condition_time() + "&" + \
               self.ser_type_values.get(self.ser_type) + "&" + self.ser_sub_values.get(self.ser_sub) \
               + "&nodup=1&page=" + str(self.page)

    def get_ser_condition_time(self):
        if not self.ser_time_start:
            return
        ser_time_start = "timescope=custom:" + self.ser_time_start
        ser_time_end = ":" + self.ser_time_end if self.ser_time_end else ""
        return ser_time_start + ser_time_end
