# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/17 09:01
@desc
"""


import re
from pyquery import PyQuery as pd
from spiders import MainSpider
from lib.http_request import HttpRequest
from spiders.court_bulletin.model import BulletinCourt
from lib.spider_exception import SpiderException
import traceback
import logging


log = logging.getLogger()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.ezfy.hbfy.gov.cn",
    "Pragma": "no-cache",
    "Referer": "http://www.ezfy.hbfy.gov.cn/DocManage/getDocsByFolder?folderNo=0401",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
}


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "hubei"
        self.site_name = "湖北省高级人民法院"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        form = {
            "folderNo": "0401",
            "pageIndex": "1"
        }

        url = "http://www.ezfy.hbfy.gov.cn/DocManage/getDocsByFolder"
        log.info("开始抓取==============湖北省高级人民法院")

        self.http.http_requst(url, "post", data=form, headers=self.headers)

        if self.http.res_code() == 200:

            html_data = self.http.parse_html()
            self.parse_html(html_data)


            # object_list = self.parse_list(parse_data)
            # self.mysql_client.session_insert_list(object_list)
            # self.mysql_client.session_commit()
            # total_page = self.get_total_page(json_data)
            # for i in range(2, total_page + 1):
            #     try:
            #         form["page.pageNo"] = i
            #         log.info("开始抓取==============江西庭审公开网,第{}页".format(i))
            #         self.http.http_session(url, "post", data=form, headers=self.headers)
            #         if self.http.res_code() == 200:
            #             json_data = self.http.parse_json()
            #             object_list = self.parse_list(json_data)
            #             self.mysql_client.session_insert_list(object_list)
            #             self.mysql_client.session_commit()
            #         else:
            #             SpiderException("抓取json异常", self.task_id, url, self.site_name)
            #
            #     except Exception:
            #         m = traceback.format_exc()
            #         SpiderException(m, self.task_id, url, self.site_name)
            #     # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
            #     break
        else:
            SpiderException("抓取异常", self.task_id, url, self.site_name)


    def added_parse(self):
        pass

    def parse_html(self, html):
        doc = pd(html)
        total_page = "".join(re.findall("共.*页\s上", doc('span').text().replace("\n", "")))[1:3]
        print(total_page)


if __name__ == "__main__":

    jiangxi_spider = Spider()
    jiangxi_spider.parse()
