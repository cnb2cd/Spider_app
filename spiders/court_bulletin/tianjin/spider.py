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
headers = {
'Host':'www.jxfy.gov.cn',
'Connection':'keep-alive',
'Content-Length':'173',
'Pragma':'no-cache',
'Cache-Control':'no-cache',
'Accept':'application/json, text/javascript, */*; q=0.01',
'Origin':'http://www.jxfy.gov.cn',
'X-Requested-With':'XMLHttpRequest',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Referer':'http://www.jxfy.gov.cn/tingshen/list.jsp?nid=5348&filterform=true&live=false',
'Accept-Language':'zh-CN,zh;q=0.9'

}


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