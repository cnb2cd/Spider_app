# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/17 16:31
@desc
"""



import re
import time
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
    "Host": "www.hncourt.gov.cn",
    "Pragma": "no-cache",
    "Referer": "http://www.hncourt.gov.cn/public/index.php?LocationID=1000000000",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

class Spider(MainSpider):

    def __init__(self):
        self.task_id = "henan"
        self.site_name = "河南省高级人民法院"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        form = {
            "p": "1",
            "LocationID": "1000000000",
            "sub": ""
        }

        url = "http://www.hncourt.gov.cn/public/index.php?LocationID=1000000000"
        log.info("开始抓取==============河南省高级人民法院")
        log.info("开始抓取==============河南省高级人民法院,第{}页".format(str(form['p'])))
        self.http.http_session(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            self.http.set_charset("gbk")
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储==============河南省高级人民法院,第{}页".format(str(form['p'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            # for i in range(2, int(total_page)+1):
            #     try:
            #         form["pagego"] = i
            #         log.info("开始抓取==============河南省高级人民法院,第{}页".format(i))
            #         self.http.http_session(url, "post", data=form, headers=self.headers)
            #         if self.http.res_code() == 200:
            #             html_data = self.http.parse_html()
            #             object_list, total_page = self.parse_html(html_data)
            #             log.info("开始存储==============河南省高级人民法院,第{}页".format(i))
            #             # 将对象列表插入数据库
            #             self.mysql_client.session_insert_list(object_list)
            #             # 提交
            #             self.mysql_client.session_commit()
            #         else:
            #             SpiderException("抓取河南省高级人民法院,第{}页异常".format(i), self.task_id, url, self.site_name)
            #     except Exception:
            #         # 捕获异常
            #         m = traceback.format_exc()
            #         SpiderException(m, self.task_id, url, self.site_name)
            #     # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
            #     break


        else:
            SpiderException("抓取河南省高级人民法院,第{}页异常".format(str(form['pagego'])), self.task_id, url, self.site_name)
        # 关闭数据库链接
        # self.mysql_client.session_close()
        log.info("抓取河南省高级人民法院结束")


    def parse_html(self, html):
        # 解析html


        # 生成文件路径
        t_way = self.task_id + str(time.time()) + '.txt'
        # 将获取的html写入文件
        file_out(t_way, str(html.encode("utf-8")))
        doc = pq(html)
        total_page = int("".join(re.findall("(共\d{1,2}页)", doc("td.td_pagebar").text())).replace("共", "").replace("页", ""))
        # print(total_page)
        lis = doc('div.box tr.tr_odd').items()
        # 创建对象列表
        object_list = list()
        for x in lis:
            # 创建item字典
            item = dict()

            url = "http://www.hncourt.gov.cn" + x('a').attr.href
            self.http.http_session(url, "get", headers=self.headers)
            htm = self.http.parse_html()
            doc = pq(htm)
            content = doc('table.article_content')
            item["taskid"] = self.task_id
            item["release_date"] = "".join(re.findall("\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}", content(
                'span.article_time').text()))
            item["title"] = content('b').text()
            item["bulletin_way"] = t_way
            try:
                item["court_y"] = "".join(re.findall("(.{2,8}法院)", content.text(),)[0])
            except:
                item["court_y"] = ""
            item["court_t"] = "".join(re.findall("(在本院.*依法公开)", content.text())).replace(
                "在本院", "").replace("依法公开", "")
            item["start_court_t"] = "".join(re.findall("20\d{2}年\d{1,2}月\d{1,2}日\s\d{1,2}时\d{1,2}分", content.text())
                                            ).replace("年", "-").replace("月", "-").replace("日", "").replace("时", ":").replace("分", "")
            if len(item["start_court_t"]) < 10:
                item["start_court_t"] = "".join(re.findall("开庭时间.*:\d{1,2}", content.text())).replace("开庭时间：", "")

            item["plaintiff"] = "".join(re.findall("(审理.{2,20}诉)", content.text())).replace(
                "审理", "").replace("诉", "")
            item["defendant"] = "".join(re.findall("(诉.*等)", content.text())).replace("诉", "").replace("等", "")
            item['site_name'] = self.site_name

            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
            # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    henan_spider = Spider()
    henan_spider.parse()
