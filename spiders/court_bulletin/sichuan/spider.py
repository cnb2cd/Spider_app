# --*-- coding:utf-8 --*--
"""
@author wq
@time  2018/10/18 19:09
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
    "Content-Length": "30",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "111.230.134.78:8081",
    "Origin": "http://111.230.134.78:8081",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://111.230.134.78:8081/sdgl/webapp/sfsdweb/notice_no.html?fydm=51",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64"
                  ") AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    }


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "sichuan"
        self.site_name = "四川法院司法公开网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):

        form = {
            "ah": "",
            "page": "1",
            "fydm": "51",
            "limit": "9",
            "nd": ""
            }

        url = "http://111.230.134.78:8081/sdgl/app/sdggsd_list"
        log.info("开始抓取=============={}".format(self.site_name))
        log.info("开始抓取=============={},第{}页".format(self.site_name, str(form['page'])))
        self.http.set_charset("unicode")
        self.http.http_session(url, "post", data=form, headers=self.headers)

        if self.http.res_code() == 200:
            json_data = self.http.parse_json()
            object_list = self.parse_list(json_data, form)
            # log.info("开始存储=============={},第{}页".format(self.site_name, str(form['page'])))
            # self.mysql_client.session_insert_list(object_list)
            # self.mysql_client.session_commit()
            # total_page = self.get_total_page(json_data)
            # for i in range(2, total_page + 1):
            #     try:
            #         form["page"] = i
            #         log.info("开始抓取=============={},第{}页".format(self.site_name, i))
            #         self.http.http_session(url, "post", data=form, headers=self.headers)
            #         if self.http.res_code() == 200:
            #             json_data = self.http.parse_json()
            #             object_list = self.parse_list(json_data, form)
            #             log.info("开始存储=============={},第{}页".format(self.site_name, str(form['page'])))
            #             self.mysql_client.session_insert_list(object_list)
            #             self.mysql_client.session_commit()
            #         else:
            #             SpiderException("抓取json{},第{}页异常".format(self.site_name, str(form['page'])
            #                                                      ), self.task_id, url, self.site_name)
            #
            #     except Exception:
            #         m = traceback.format_exc()
            #         SpiderException(m, self.task_id, url, self.site_name)
            #
            #     # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
            #
            #     break
            # self.mysql_client.session_close()
        else:
            SpiderException("抓取json{},第{}页异常".format(self.site_name, str(form['page'])
                                                     ), self.task_id, url, self.site_name)
        log.info("抓取{}结束".format(self.site_name))


    def added_parse(self):
        pass

    def parse_list(self, json_data, form):
        # 解析获取到的json
        log.info("开始解析{}第{}页".format(self.site_name, (form['page'])))
        t_way = self.task_id + str(time.time()) + '.txt'
        file_out(t_way, str(json_data))
        object_list = list()
        case_list = json_data["data"]
        for case in case_list:
            pub_data = case["clsj"]
            formdata = {
                "ggsdid": "{}".format(str(case['ggsdid'])),
                "ssfy": "{}".format(str(case['fydm']))
                }
            ur = "http://111.230.134.78:8081/sdgl/app/getGgsdInfo.do"
            self.http.http_session(ur, "post", data=formdata, headers=self.headers)
            json = self.http.parse_json()["data"]
            item = dict()
            # item["taskid"] = self.task_id
            item["court_y"] = get_content(json.get("SSFYMC"))  # 法院
            # item["court_t"] = get_content(case.get("FT"))  # 法庭
            # item["start_court_t"] = get_content(case.get("KTRQSTRING"))  # 开庭日期
            item["court_num"] = json.get("AH")  # 案号
            # item["court_case"] = get_content(case.get("AY"))  # 案由
            # item["trial_cause"] = get_content(case.get("SPZ")).strip()  # 审判人员
            # item["site_name"] = self.site_name  # 网站名称
            # item['bulletin_way'] = t_way
            # item["undertake_dep"] = get_content(case.get("CBBM"))
            # item["plaintiff"] = get_content(case.get("YG")).replace("原告:", "")
            # item["defendant"] = get_content(case.get("BG")).replace("被告:", "")
            # item["schedule_time"] = get_content(case.get("PQRQ"))
            print(item)
            # b = BulletinCourt(**item)
            # object_list.append(b)
            break
        return object_list

    def get_total_page(self, json_data):
        # 获取总页数
        try:
            total_page = json_data["total"]
            return int(total_page ) // 10
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.task_id, self.site_name, json_data)
            return 0


def get_content(content):
    return content if content else ""


if __name__ == "__main__":

    sichuan_spider = Spider()
    sichuan_spider.parse()
