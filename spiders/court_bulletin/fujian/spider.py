# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/18 16:19
@desc
"""


import logging
import time
import re
import requests
from pyquery import PyQuery as pq
from spiders import MainSpider
from lib.http_request import HttpRequest
from spiders.court_bulletin.model import BulletinCourt
from lib.spider_exception import SpiderException
import traceback
from util.date_parse import get_today_date
from util.file import file_out

requests.packages.urllib3.disable_warnings()


log = logging.getLogger()


headers = {
    "Host": "www.fjcourt.gov.cn",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
    # "Cookie": "ASP.NET_SessionId=00cjljiyfdjgxlmyvbdkm0ab; Hm_lvt_5b3a903dfec5ceeedc657e93ebc7c5f4=1539836124,1539850436; Hm_lpvt_5b3a903dfec5ceeedc657e93ebc7c5f4=1539851321",
    }


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "fujian"
        self.site_name = "福建省高级人民法院法院公告"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        url = "https://www.fjcourt.gov.cn/page/public/courtreport.html"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, 1))
        self.http.http_requst(url, "get", headers=self.headers, verify=False)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page, VIEWSTATE = self.parse_html(html_data)
            log.info("开始存储=============={},第{}页".format(self.site_name, 1))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()

            for i in range(2, int(total_page)+1):
                form = {
                    "__VIEWSTATE": VIEWSTATE,
                    "__VIEWSTATEGENERATOR": "54969BDC",
                    "__EVENTTARGET": "ctl00$cplContent$AspNetPager1",
                }
                try:
                    form["__EVENTARGUMENT"] = i
                    log.info("开始抓取=============={},第{}页".format(self.site_name, (form['__EVENTARGUMENT'])))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page, VIEWSTATE = self.parse_html(html_data)
                        log.info("开始存储=============={},第{}页".format(self.site_name, (form['__EVENTARGUMENT'])))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取{},第{}页异常".format(self.site_name, (form['__EVENTARGUMENT'])
                                                             ), self.task_id, url, self.site_name)
            #
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取{},第{}页异常".format(self.site_name, 1), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_html(self, html):

        doc = pq(html)
        total_page = 10
        for page in doc('a.pagination').items():
            if page.text() == ">>":
                total_page = int("".join(re.findall("\d{2,3}", page.attr.href)))
        VIEWSTATE = doc("div.aspNetHidden input").attr.value
        lis = doc('ul.module-case-items li').items()
        object_list = list()
        for x in lis:
            self.http.http_session("https://www.fjcourt.gov.cn" +
                                   x('a').attr.href, "get", headers=self.headers, verify=False)
            htm = self.http.parse_html()
            doc = pq(htm)
            # 生成文件路径
            t_way = self.task_id + str(time.time()) + '.txt'
            # 生成文件路径
            file_out(t_way, str(htm))
            content = doc('div.article-wrap')
            item = dict()
            item["taskid"] = self.task_id
            item["title"] = content('p.article-hd-title').text()
            item["bulletin_way"] = t_way
            item["court_y"] = content('span.article-author').text()
            item["court_t"] = "".join(re.findall("(在.*公开)", content('div.article-content').text())
                                      ).replace("在", "").replace("公开", "")
            item["start_court_t"] = x('span.cir-time').text().replace("[", "").replace("]", "")
            item["court_part"] = "".join(re.findall("(在.*公开)", content('div.article-content').text())
                                      ).replace("在", "").replace("公开", "")
            item["site_name"] = self.site_name
            pub_time = (item["start_court_t"].replace("-", ""))
            date = get_today_date()
            if eval(pub_time) > eval(date):
                # 将item字典映射成对象
                b = BulletinCourt(**item)
                object_list.append(b)
        # 返回对象列表和总页数
        return object_list, total_page, VIEWSTATE



if __name__ == "__main__":

    fujian_spider = Spider()
    fujian_spider.parse()
