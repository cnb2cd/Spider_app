# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/18 10:59
@desc
"""


import time
from spiders import MainSpider
from lib.http_request import HttpRequest
from util.date_parse import get_today_date
from spiders.court_bulletin.model import BulletinCourt
from lib.spider_exception import SpiderException
import traceback
import logging
from util.file import file_out


log = logging.getLogger()

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "146",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.hicourt.gov.cn",
    "Origin": "http://www.hicourt.gov.cn",
    "Pragma": "no-cache",
    "Referer": "http://www.hicourt.gov.cn/preview/channel?columnId=2053fd88-0e35-4374-9832-d0fe07224671&&parentId=dcff733d-6602-44a4-9591-1149d03ef9d8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    }


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "hainan"
        self.site_name = "天涯法律网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        today_date = get_today_date()
        next_year_today_date = str(int(today_date[0:4]) + 1) + today_date[4:]

        form = {
            "currentPageNo": "1",
            "pageSize": "10",
            "startDate": today_date,
            "endDate": next_year_today_date,
            "caseNo": "",
            "litigant": "",
            "judge": "",
            "caseDesc": "",
            "siteId": "f7afc746-8577-4cd4-a410-884027df5bab"
        }

        url = "http://www.hicourt.gov.cn/frontDesk/getNoticeList"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, str(form['currentPageNo'])))
        self.http.http_session(url, "post", data=form, headers=self.headers)
        #
        if self.http.res_code() == 200:
            json_data = self.http.parse_json()
            object_list = self.parse_list(json_data, form)
            log.info("开始存储=============={},第{}页".format(self.site_name, str(form['currentPageNo'])))
            self.mysql_client.session_insert_list(object_list)
            self.mysql_client.session_commit()
            total_page = self.get_total_page(json_data)
            for i in range(2, total_page + 1):
                try:
                    form["currentPageNo"] = i
                    log.info("开始抓取=============={},第{}页".format(self.site_name, i))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        json_data = self.http.parse_json()
                        object_list = self.parse_list(json_data, form)
                        log.info("开始存储=============={},第{}页".format(self.site_name, str(form['currentPageNo'])))
                        self.mysql_client.session_insert_list(object_list)
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取json{},第{}页异常".format(self.site_name, str(form['currentPageNo'])
                                                                      ), self.task_id, url, self.site_name)

                except Exception:
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
            self.mysql_client.session_close()
        else:
            SpiderException("抓取json{},第{}页异常".format(self.site_name, str(form['page.pageNo'])
                                                     ), self.task_id, url, self.site_name)
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_list(self, json_data, form):
        # 解析获取到的json
        log.info("开始解析{}第{}页".format(self.site_name, (form['currentPageNo'])))
        t_way = self.task_id + str(time.time()) + '.txt'
        file_out(t_way, str(json_data))
        object_list = list()
        case_list = json_data["data"]
        for case in case_list:
            item = dict()
            item["taskid"] = self.task_id
            item["release_date"] = get_content(case.get("createDate"))
            item["court_y"] = get_content(case.get("belongOrgName"))  # 法院
            item["court_t"] = get_content(case.get("trialCourt"))  # 法庭
            item["start_court_t"] = get_content(case.get("courtTime"))  # 开庭日期
            item["court_num"] = get_content(case.get("caseNo"))  # 案号
            item["court_case"] = get_content(case.get("caseDesc"))  # 案由
            item["trial_cause"] = get_content(case.get("judge")).strip()  # 审判人员
            item["site_name"] = self.site_name  # 网站名称
            item['bulletin_way'] = t_way
            b = BulletinCourt(**item)
            object_list.append(b)
        return object_list

    def get_total_page(self, json_data):
        # 获取总页数
        try:
            total_page = json_data["pages"]
            return int(total_page)
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.task_id, self.site_name, json_data)
            return 0


def get_content(content):
    return content if content else ""


if __name__ == "__main__":

    hainan_spider = Spider()
    hainan_spider.parse()
