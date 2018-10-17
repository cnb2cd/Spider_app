# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/17 09:01
@desc
"""


import time
import re
from pyquery import PyQuery as pd
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
    "Host": "www.ezfy.hbfy.gov.cn",
    "Pragma": "no-cache",
    "Referer": "http://www.ezfy.hbfy.gov.cn/DocManage/getDocsByFolder?folderNo=0401",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
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
        log.info("开始抓取==============湖北省高级人民法院,第{}页".format(str(form['pageIndex'])))
        self.http.http_requst(url, "post", data=form, headers=self.headers)
        if self.http.res_code() == 200:
            html_data = self.http.parse_html()
            object_list, total_page = self.parse_html(html_data)
            log.info("开始存储==============湖北省高级人民法院,第{}页".format(str(form['pageIndex'])))
            # 将对象列表插入数据库
            self.mysql_client.session_insert_list(object_list)
            # 提交
            self.mysql_client.session_commit()
            for i in range(2, int(total_page)+1):
                try:
                    form["pageIndex"] = i
                    log.info("开始抓取==============湖北省高级人民法院,第{}页".format(i))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        html_data = self.http.parse_html()
                        object_list, total_page = self.parse_html(html_data)
                        log.info("开始存储==============湖北省高级人民法院,第{}页".format(str(form['pageIndex'])))
                        # 将对象列表插入数据库
                        self.mysql_client.session_insert_list(object_list)
                        # 提交
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取湖北省高级人民法院,第{}页异常".format(i), self.task_id, url, self.site_name)

                except Exception:
                    # 捕获异常
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取湖北省高级人民法院,第{}页异常".format(str(form['pageIndex'])), self.task_id, url, self.site_name)
        # 关闭数据库链接
        self.mysql_client.session_close()
        log.info("抓取湖北省高级人民法院结束")


    def added_parse(self):
        pass

    def parse_html(self, html):
        # 解析html

        t_way = self.task_id + str(time.time()) + '.txt'
        file_out(t_way, str(html))
        doc = pd(html)
        total_page = "".join(re.findall("共.*页\s上", doc('span').text().replace("\n", "")))[1:3]
        lis = doc('table.newlisttable tr').items()
        object_list = list()
        for content in lis:
            item = dict()
            item["taskid"] = self.task_id
            item["release_date"] = "".join(re.findall("(\(.*\))", content('td').text()))[1:-1]
            item["title"] = content('a').text()
            item["bulletin_way"] = t_way
            item["court_y"] = "湖北省高级人民法院" if content('p').text()[:4] == "本院定于" else content('p').text()[:4]
            item["court_t"] = "".join(re.findall("(在.*判庭)", content('p').text())).replace("在", "")
            item["start_court_t"] = "".join(re.findall("(\d{4}年\d{2}月\d{2}日\s\d{2}:\d{2})", content('p').text())).replace(
                "年", "-").replace("月", "-").replace("日", "")
            item["plaintiff"] = "".join(re.findall("(原告:.*;)", content('p').text())).replace("原告:", "")
            item["defendant"] = "".join(re.findall("(被告:.*的)", content('p').text())).replace("被告:", "").replace("的", "")
            item["site_name"] = "湖北省高级人民法院"
            # 将item字典映射成对象
            b = BulletinCourt(**item)
            object_list.append(b)
        # 返回对象列表和总页数
        return object_list, total_page



if __name__ == "__main__":

    hubei_spider = Spider()
    hubei_spider.parse()
