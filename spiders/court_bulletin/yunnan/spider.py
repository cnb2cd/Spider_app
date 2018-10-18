# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/18 09:52
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


log = logging.getLogger()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.ynfy.gov.cn",
    "Pragma": "no-cache",
    # "Referer": "http://www.ynfy.gov.cn/ktgg/index.jhtml",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
}


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "yunan"
        self.site_name = "云南法院司法信息网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        form = {
            "channelId": "858",
            "listsize": "673",
            "pagego": "1"
        }

        url = "http://www.ynfy.gov.cn/ktggPage.jspx"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, (form['pagego'])))
        self.http.http_requst(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储=============={},第{}页".format(self.site_name, (form['pagego'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            form["listsize"] = total_page
            for i in range(2, int(total_page)+1):
                try:
                    form["pagego"] = i
                    log.info("开始抓取=============={},第{}页".format(self.site_name, (form['pagego'])))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储=============={},第{}页".format(self.site_name, (form['pagego'])))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取{},第{}页异常".format(self.site_name, (form['pagego'])), self.task_id, url, self.site_name)
            #
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取{},第{}页异常".format(self.site_name, (form['pagego'])), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_html(self, html):
        # 解析html

        # # 生成文件路径
        t_way = self.task_id + str(time.time()) + '.txt'
        # 生成文件路径
        file_out(t_way, str(html))
        doc = pq(html)
        total_page = 10
        for page in doc('div.turn_page a.zt_02').items():
            if int(page.text()) > total_page:
                total_page = int(page.text())
        lis = doc('ul.sswy_news li').items()
        object_list = list()
        for x in lis:
            self.http.http_session(x('a').attr.href, "get", headers=self.headers)
            html = self.http.parse_html()
            doc = pq(html)
            content = doc('div.ywzw_con_inner')
            item = dict()
            item["taskid"] = self.task_id
            item["release_date"] = "".join(re.findall("\d{4}-\d{2}-\d{2}", content('p.p_source ').text()))
            item["title"] = x('a').attr.title
            item["bulletin_way"] = t_way
            item["court_y"] = content('h3.h3_title').text()
            item["court_t"] = "".join(re.findall("(在.*依法)", content('p').text())).replace("在", ""
                                                                                          ).replace("依法", "")
            item["start_court_t"] = "".join(re.findall("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}", x('a').attr.title))
            item["court_part"] = "".join(re.findall("(在.*依法)", content('p').text())
                                         ).replace("在", "").replace("依法", "")
            item["site_name"] = self.site_name
            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
        # 返回对象列表和总页数
        #     break
        return object_list, total_page



if __name__ == "__main__":

    yunnan_spider = Spider()
    yunnan_spider.parse()
