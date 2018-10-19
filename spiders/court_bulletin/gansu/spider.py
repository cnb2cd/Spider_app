# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/19 11:31
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
    "Host": "gsgf.gssfgk.com",
    "Pragma": "no-cache",
    "Referer": "http://gsgf.gssfgk.com/ktgg/index.jhtml",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "gansu"
        self.site_name = "甘肃省高级人民法院司法公开网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        form = {
            "channelId": "307",
            "listsize": "100",
            "pagecur": "0",
            "pagego": "add"
        }

        url = "http://gsgf.gssfgk.com/ktggPage.jspx"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, (form['pagecur'])))
        self.http.http_session(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储=============={},第{}页".format(self.site_name, (form['pagecur'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            form["listsize"] = total_page
            for i in range(1, int(total_page)+1):
                try:
                    form["pagecur"] = i
                    log.info("开始抓取=============={},第{}页".format(self.site_name, (form['pagecur'])))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储=============={},第{}页".format(self.site_name, (form['pagecur'])))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取{},第{}页异常".format(self.site_name, (form['pagecur'])
                                                             ), self.task_id, url, self.site_name)
            #
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取{},第{}页异常".format(self.site_name, (form['pagecur'])), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_html(self, html):
        # 解析html

        doc = pq(html)
        page_list = doc('a.zt_02').items()
        total_page = 10
        for page in page_list:
            if int(page.text()) > total_page:
                total_page = int(page.text())
        lis = doc('div.text ul li a').items()
        object_list = list()
        for x in lis:
            item = dict()
            self.http.http_session(x.attr.href, "get", headers=self.headers)
            htm = self.http.parse_html()
            # # 生成文件路径
            t_way = self.task_id + str(time.time()) + '.txt'
            # # 生成文件路径
            file_out(t_way, str(htm))
            doc = pq(htm)
            content = doc('div.text')
            item["taskid"] = self.task_id
            item["release_date"] = content('h2').text()[3:13]
            item["title"] = content('h1').text()
            item["bulletin_way"] = t_way
            item["court_y"] = "".join(re.findall("(在.*法院)", content('h1').text())).replace("在", "")
            item["court_t"] = "".join(re.findall("(院.*庭)", content('h1').text())).replace("院", "").replace("开庭", "")
            item["start_court_t"] = "".join(re.findall("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}", x.text()))
            item["plaintiff"] = "".join(re.findall("(审理.*诉)", content("p").text())).replace("审理", "").replace("诉", "")
            item["site_name"] = self.site_name
            date = get_today_date()
            if eval("".join(re.findall("\d{4}-\d{2}-\d{2}", x.text())).replace("-", "")) > eval(date):

                # 将item字典映射成对象
                b = BulletinCourt(**item)
                object_list.append(b)
        # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    gansu_spider = Spider()
    gansu_spider.parse()