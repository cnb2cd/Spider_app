# --*-- coding:utf-8 --*--
"""

@author wht
@time  2018/10/13 12:01
@desc 江西开庭公告
"""

from spiders import MainSpider
from lib.http_request import HttpRequest
from util.date_parse import get_today_date
from spiders.court_bulletin.model import BulletinCourt
from lib.spider_exception import SpiderException
import traceback
import logging


log = logging.getLogger()

headers = {
'Host':'www.jxfy.gov.cn',
'Connection':'keep-alive',
'Content-Length':'173',
'Pragma':'no-cache',
'Cache-Control':'no-cache',
'Accept':'application/json, text/javascript, */*; q=0.01',
'Origin':'http://www.jxfy.gov.cn',
'X-Requested-With':'XMLHttpRequest',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Referer':'http://www.jxfy.gov.cn/tingshen/list.jsp?nid=5348&filterform=true&live=false',
'Accept-Language':'zh-CN,zh;q=0.9'

}
H = HttpRequest("111111",'1111')
class Spider(MainSpider):

    task_id = "jiangxi"
    site_name = "江西庭审公开网"

    def __init__(self):
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        # self.http.headers['referer'] = 'http://www.jxfy.gov.cn/tingshen/list.jsp?nid=5348&filterform=true&live=false'
        # self.http.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers = headers

    def parse(self):

        date = get_today_date()

        form = {
            'isGeneral': 'Y',
            'belongOrgId': '',
            'liveStatus': '001',
            'page.pageSize': '20',
            'page.pageNo': '1',
            'gopenCourtDate': date,
            'page.orderBy': 'openCourtDate',
            'page.order': 'asc',
            'caseType': '',
            'searchWord': ''
        }

        url = "http://www.jxfy.gov.cn/api.do?method=ttrialliveliveinfo!listAjaxp.action"
        log.info("开始抓取==============江西庭审公开网")

        H.http_session(url, data=form, headers=self.headers)
        print(self.http.parse_json())

        if self.http.res_code() == 200:
            json_data = self.http.parse_json()
            item = self.parse_list(self, json_data)
            b = BulletinCourt(**item)
            self.mysql_client.session_insert(b)
            self.mysql_client.session_commit()
            self.mysql_client.session_close()
            total_page = self.get_total_page(json_data)
            for i in range(2, total_page + 1):
                try:
                    form["page.pageNo"] = i
                    log.info("开始抓取==============江西庭审公开网", "第{}页".format(i))
                    self.http.http_session(url, "post", data=form, headers=header)
                    if self.http.res_code() == 200:
                        json_data = self.http.parse_json()
                        item = self.parse_list(self, json_data)
                        b = BulletinCourt(**item)
                        self.mysql_client.session_insert(b)
                        self.mysql_client.session_commit()
                        self.mysql_client.session_close()
                    else:
                        SpiderException("抓取json异常", self.taskid, url, self.site_name)
                    break
                except Exception:
                    m = traceback.format_exc()
                    SpiderException(m, self.taskid, url, self.site_name)
        else:
            SpiderException("抓取json异常", self.taskid, url, self.site_name)


    def added_parse(self):
        pass

    def parse_list(self, json_data):
            case_list = json_data["message"]["result"]

            for case in case_list:
                item = {}
                item["taskid"] = self.task_id
                try:
                    item["release_date"] = case["lastBroadcastTimeString"]  # 发布日期
                except:
                    item["release_date"] = ""
                item["title"] = case["caseName"]  # 标题
                item["court_y"] = case["belongOrgName"]  # 法院
                try:
                    item["court_t"] = case["openCourtAddr"]  # 法庭
                except:
                    item["court_t"] = ""
                item["start_court_t"] = case["openCourtDateString"]  # 开庭日期
                item["court_num"] = case["caseNo"]  # 案号
                item["caseType"] = case["caseTypeString"]
                item["court_case"] = case["causePlacedOnFile"]  # 案由
                item["undertake_dep"] = ""  # 承办部门
                try:  # 审判人员
                    item["trial_cause"] = case["underJustice"]
                except:
                    item["trial_cause"] = ""
                try:
                    dex = case["litigants"].index("被告:")
                    item["plaintiff"] = case["litigants"][:dex]  # 原告
                    item["defendant"] = case["litigants"][dex:]  # 被告
                except:
                    item["plaintiff"] = ""
                    item["defendant"] = "被告:" + case["litigants"]
                try:
                    item["court_part"] = case["openCourtAddr"]  # 开庭地点
                except:
                    item["court_part"] = ""
                item["party"] = case["litigants"]  # 当事人
                item["site_name"] = self.site_name  # 网站名称
                try:
                    item["remarks"] = case["remarks"]
                except:
                    item["remarks"] = ""
                item["bulletin_way"] = "案件:" + item["title"] + ";归属法院：" + item["court_y"] + ";案号：" + item[
                    "court_num"] + ";案件类型：" + case["caseTypeString"] + ";承办法官：" + item["trial_cause"] + ";当事人：" + item[
                                           "party"] + ";开庭地点：" + item["court_part"] + ";开庭时间：" + item[
                                           "start_court_t"] + ";案件内容：" + item["remarks"]  # 公告内容
                return item

    def get_total_page(self, json_data):

        try:
            total_page = json_data["message"]["totalPages"]
            return int(total_page)
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, json_data)
            return 0

jiangxi_spider = Spider()
jiangxi_spider.parse()