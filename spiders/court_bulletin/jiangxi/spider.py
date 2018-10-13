# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/13 12:01
@desc 江西开庭公告
"""

from spiders import MainSpider
from lib.http_request import HttpRequest


class Spider(MainSpider):

    task_id = ""

    def __init__(self):
        MainSpider.__init__(self)
        self.http = HttpRequest("")

    def parse(self):
        pass

    def added_parse(self):
        pass



