# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/15 11:11
@desc
"""

from spiders import MainSpider
from lib.http_request import HttpRequest
from lib.spider_exception import SpiderException
import traceback
import logging

log = logging.getLogger()


class Spider(MainSpider):

    site_name = '天津法院网'

    def __init__(self, taskid, url):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = url

    def parse(self):
        log.info('开始抓取==================天津法院网')
        self.http.http_session(self.url, 'get', headers=self.http.headers)
        try:
            r = self.http.parse_html()
            print(r)
        except Exception :
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name)
        pass

    def added_parse(self):
        pass

    def parse_list(self, doc):
        pass

s=Spider("111111111", "http://tjfy.chinacourt.org/article/index/id/MzDIMTCwMDAwNCACAAA=.shtml")
s.parse()