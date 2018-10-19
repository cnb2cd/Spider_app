# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/19 19:05
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
    "Host": "sxfy.chinacourt.org",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
}


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "sanxi"
        self.site_name = "陕西法院网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        page = 1
        url = "http://sxfy.chinacourt.org/article/index/id/M8i2NDBINDAwNCACAAA/page/{}.shtml".format(page)
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, page))
        self.http.http_requst(url, "get", headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储=============={},第{}页".format(self.site_name, page))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            #
            for i in range(2, int(total_page)+1):
                try:
                    page = i
                    url = "http://sxfy.chinacourt.org/article/index/id/M8i2NDBINDAwNCACAAA/page/{}.shtml".format(page)
                    log.info("开始抓取=============={},第{}页".format(self.site_name, page))
                    self.http.http_session(url, "get", headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储=============={},第{}页".format(self.site_name, page))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取{},第{}页异常".format(self.site_name, page),
                                        self.task_id, url, self.site_name)
            #
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取{},第{}页异常".format(self.site_name, page), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_html(self, html):
        # 解析html

        doc = pq(html)
        page = doc('div.paginationControl a').eq(5).attr.href
        total_page = "".join(re.findall("\d{1,3}", page))
        lis = doc('span.left').items()
        object_list = list()
        for x in lis:
            self.http.http_session("http://sxfy.chinacourt.org" + x('a').attr.href, "get", headers=self.headers)
            htm = self.http.parse_html()

            doc = pq(htm)
            content = doc('div.detail')
            # 生成文件路径
            t_way = self.task_id + str(time.time()) + '.txt'
            # 生成文件路径
            file_out(t_way, str(content))
            item = dict()
            item["taskid"] = self.task_id
            item["release_date"] = "".join(re.findall("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}", content('div.sth_a').text()))
            item["title"] = content('div.b_title').text()
            item["bulletin_way"] = t_way
            item["court_y"] = "陕西省高级人民法院"
            item["court_t"] = "".join(re.findall("(在.{1,10}公开)", content('div').text())).replace(
                "在", "").replace("公开", "")
            item["court_part"] = "".join(re.findall("(在.{1,10}公开)", content('div').text())).replace(
                "在", "").replace("公开", "")
            item["site_name"] = self.site_name
            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
        # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    sanxi_spider = Spider()
    sanxi_spider.parse()