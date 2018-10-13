# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/11 19:10
@desc email send
"""
import requests
import traceback
import logging


from .spider_exception import SpiderException

log = logging.getLogger()

header = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate',
          'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
          'Connection': 'Keep-Alive',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
        }


class HttpRequest:

    def __init__(self, taskid):
        self.session = requests.session()
        self.taskid = taskid
        self.r = None
        self.charset = "utf-8"

    def setcharset(self, char):
        self.charset = char

    def http_session(self, url, method, **kwargs):
        try:
            r = self.session.request(method, url, **kwargs)
            self.r = r
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, url)

    def http_requst(self, url, method, **kwargs):
        try:
            r = requests.request(method, url, **kwargs)
            self.r = r
        except Exception :
            m = traceback.format_exc()
            SpiderException(m, self.taskid, url)

    def parse_html(self):
        print(self.charset)
        return self.r.content.decode(self.charset, 'ignore').replace(u'\xa9', u'')

    def parse_json(self):
        return self.r.json()

    def parse_text(self):
        self.r.encoding = self.charset
        return self.r.text

    def res_code(self):
        return self.r.status_code

    def res_cookie(self):
        return self.r.cookies

    def add_cookie(self, cookies):
        self.session.cookies.set_cookie(cookies)

    def clear_cookie(self):
        self.session.cookies.clear_session_cookies()

    def set_proxies(self, proxies):
        self.session.proxies = proxies

















