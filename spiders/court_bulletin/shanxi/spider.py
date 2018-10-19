# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/17 10:50
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
    "Host": "www.shanxify.gov.cn",
    "Pragma": "no-cache",
    "Referer": "http://www.shanxify.gov.cn/ktggPage.jspx?channelId=307&listsize=238&pagego=234",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

class Spider(MainSpider):

    def __init__(self):
        self.task_id = "shanxi"
        self.site_name = "山西法院诉讼服务网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        form = {
            "channelId": "307",
            "listsize": "238",
            "pagego": "1"
        }

        url = "http://www.shanxify.gov.cn/ktggPage.jspx"
        log.info("开始抓取==============山西法院诉讼服务网")
        log.info("开始抓取==============山西法院诉讼服务网,第{}页".format(str(form['pagego'])))
        self.http.http_session(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储==============山西法院诉讼服务网,第{}页".format(str(form['pagego'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            for i in range(2, int(total_page)+1):
                try:
                    form["pagego"] = i
                    log.info("开始抓取==============山西法院诉讼服务网,第{}页".format(i))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储==============抓取山西法院诉讼服务网,第{}页".format(i))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取山西法院诉讼服务网,第{}页异常".format(i), self.task_id, url, self.site_name)
                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break


        else:
            SpiderException("抓取山西法院诉讼服务网,第{}页异常".format(str(form['pagego'])), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取山西法院诉讼服务网结束")


    def parse_html(self, html):
        # 解析html

        doc = pq(html)
        total_page = int(doc('a.zt_02').text()[-3:])
        lis = doc('div.text ul li a').items()
        # 创建对象列表
        object_list = list()
        for x in lis:
            # 创建item字典
            item = dict()
            self.http.http_session(x.attr.href, "post", headers=self.headers)
            htm = self.http.parse_html()
            doc = pq(htm)
            # 生成文件路径
            t_way = self.task_id + str(time.time()) + '.txt'
            # 将获取的html写入文件
            file_out(t_way, str(htm))
            content = doc('div.text')
            item["taskid"] = self.task_id
            item["release_date"] = content('h2').text()[3:13]
            item["title"] = content('h1').text()
            item["bulletin_way"] = t_way
            item["court_y"] = "".join(re.findall("(在.*院)", content('h1').text())).replace("在", "")
            item["court_t"] = "".join(re.findall("(院.*庭)", content('h1').text())).replace("院", "").replace("开庭", "")
            item["start_court_t"] = x.text()[:16]
            if u"刑事" in item["title"]:
                item["defendant"] = "".join(re.findall("(审理.*)", content('p').text().replace(
                    "\xa0\xa0", ""))).replace("审理", "")
            else:
                item["plaintiff"] = "".join(re.findall("(审理.*诉)", content('p').text().replace(
                    "\xa0\xa0", ""))).replace("审理", "").replace("诉", "")
                item["defendant"] = "".join(re.findall("(诉.*等)", content('p').text().replace(
                    "\xa0\xa0", ""))).replace("诉", "").replace("等", "")
            item['site_name'] = self.site_name
            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
            # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    shanxi_spider = Spider()
    shanxi_spider.parse()
