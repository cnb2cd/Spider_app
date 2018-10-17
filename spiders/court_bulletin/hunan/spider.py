# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/17 15:09
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
    "Host": "hunanfy.chinacourt.org",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

class Spider(MainSpider):

    def __init__(self):
        self.task_id = "hunan"
        self.site_name = "湖南法院网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        page = 1
        url = "http://hunanfy.chinacourt.org/article/index/id/M0jONTAwNzAwNCACAAA/page/{}.shtml".format(page)
        log.info("开始抓取==============湖南法院网")
        log.info("开始抓取==============湖南法院网,第{}页".format(page))
        self.http.http_session(url, "get", headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储==============山西法院诉讼服务网,第{}页".format(page))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            for i in range(2, int(total_page)+1):
                page = i
                try:
                    log.info("开始抓取==============湖南法院网,第{}页".format(page))
                    url = url = "http://hunanfy.chinacourt.org/article/index/id/M0jONTAwNzAwNCACAAA/page/{}.shtml".format(page)
                    self.http.http_session(url, "get", headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储==============山西法院诉讼服务网,第{}页".format(page))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("湖南法院网,第{}页异常".format(page), self.task_id, url, self.site_name)
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break

        else:
            SpiderException("湖南法院网,第{}页异常".format(page), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取湖南法院网结束")


    def parse_html(self, html):
        # 解析html

        # 生成文件路径
        t_way = self.task_id + str(time.time()) + '.txt'
        # 将获取的html写入文件
        file_out(t_way, str(html))
        doc = pq(html)
        page_lis = doc('a').items()
        for pag in page_lis:
            if pag.text() == "尾页":
                total_page = "".join(re.findall("(\d*.shtml)", pag.attr.href)).replace(".shtml", "")
        lis = doc('div.font14 li').items()
        # 创建对象列表
        object_list = list()
        for x in lis:
            # 创建item字典
            item = dict()
            item["release_date"] = x('span.right').text()
            self.http.http_session("http://hunanfy.chinacourt.org" + x('a').attr.href, "get", headers=self.headers)
            html = self.http.parse_html()
            doc = pq(html)
            content = doc('div.detail')
            item["taskid"] = self.task_id
            item["title"] = content('div.detail_bigtitle').text()
            item["court_y"] = "".join(re.findall("在.*法院", content('div.detail_txt').text())).replace("在", "")
            item["court_t"] = "".join(re.findall("刑.*庭", content('div.detail_txt').text()))
            item["start_court_t"] = "".join(re.findall("本院定于\d{4}年.{1,5}日", content('div.detail_txt').text())).replace(
                "年", "-").replace("月", "-").replace("日", "").replace("本院定于", "")
            item["court_num"] = "".join(re.findall("审理.*号", content('div.detail_txt').text())).replace("审理", "")
            item["trial_cause"] = "".join(re.findall("合议庭成员.*\s", content('div.detail_txt').text())).replace(
                "合议庭成员：", "").replace("\n", "")
            item["court_part"] = "".join(re.findall("在.*法院", content('div.detail_txt').text())).replace("在", "")
            item['site_name'] = self.site_name

            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
        # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    hubei_spider = Spider()
    hubei_spider.parse()


