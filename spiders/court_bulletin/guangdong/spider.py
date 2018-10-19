# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/19 14:28
@desc
"""


import time
import re
from pyquery import PyQuery as pq
from spiders import MainSpider
from lib.http_request import HttpRequest
from spiders.court_bulletin.model import BulletinCourt
from lib.spider_exception import SpiderException
import traceback
import logging
from util.file import file_out
from util.date_parse import get_today_date


log = logging.getLogger()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.gdcourts.gov.cn",
    "Pragma": "no-cache",
    # "Referer": "http://gsgf.gssfgk.com/ktgg/index.jhtml",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "guangdong"
        self.site_name = "广东法院网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        form = {
            "action": "gotoggxxcx",
            "gglx": "ktgg",
            "flag": "first"
        }

        url = "http://www.gdcourts.gov.cn/web/search"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, (form['flag'])))
        self.http.http_session(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list = self.parse_html(html_data)
            log.info("开始存储=============={},第{}页".format(self.site_name, (form['flag'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
        else:
            SpiderException("抓取{},第{}页异常".format(self.site_name, (form['pagecur'])), self.task_id, url, self.site_name)

        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_html(self, html):
        # 解析html

        # 生成文件路径
        t_way = self.task_id + str(time.time()) + '.txt'
        # 生成文件路径
        file_out(t_way, str(html.encode("utf8")))

        doc = pq(html)
        lis = doc('div.doclist tr').items()
        object_list = list()
        x_lis = list()
        for x in lis:
            x_lis.append(x)
        text_lis = list()
        for i in x_lis[1:]:
            text_lis = list()
            for text in i('td').items():
                text_lis.append(text.text())
            item = dict()
            item["taskid"] = self.task_id
            item["bulletin_way"] = t_way
            item["court_num"] = text_lis[0]
            item["court_pur"] = text_lis[1]
            item["court_part"] = text_lis[2]
            item["start_court_t"] = text_lis[3]
            item["court_end_t"] = text_lis[4]
            item["court_status"] = text_lis[5]
            item["site_name"] = self.site_name
            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
        # # 返回对象列表和总页数
        return object_list



if __name__ == "__main__":

    guangdong_spider = Spider()
    guangdong_spider.parse()
