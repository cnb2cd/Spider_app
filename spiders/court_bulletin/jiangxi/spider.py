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


class Spider(MainSpider):

    def __init__(self):
        self.task_id = "jiangxi"
        self.site_name = "江西庭审公开网"
        MainSpider.__init__(self, task_id=self.task_id)
        self.http = HttpRequest(self.task_id, self.site_name)
        self.headers = headers

    def parse(self):
        date = get_today_date()
        form = {
            'isGeneral': 'Y',
            'belongOrgId': '',
            'liveStatus': '001',
            'page.pageSize': '20',
            'page.pageNo': '1',
            'gopenCourtDate': date + ' 00:00:00',
            'page.orderBy': 'openCourtDate',
            'page.order': 'asc',
            'caseType': '',
            'searchWord': ''
        }

        url = "http://www.jxfy.gov.cn/api.do?method=ttrialliveliveinfo!listAjaxp.action"
        log.info("开始抓取==============江西庭审公开网")

        self.http.http_session(url, "post", data=form, headers=self.headers)

        if self.http.res_code() == 200:
            json_data = self.http.parse_json()
            object_list = self.parse_list(json_data)
            self.mysql_client.session_insert_list(object_list)
            self.mysql_client.session_commit()
            total_page = self.get_total_page(json_data)
            for i in range(2, total_page + 1):
                try:
                    form["page.pageNo"] = i
                    log.info("开始抓取==============江西庭审公开网,第{}页".format(i))
                    self.http.http_session(url, "post", data=form, headers=self.headers)
                    if self.http.res_code() == 200:
                        json_data = self.http.parse_json()
                        object_list = self.parse_list(json_data)
                        self.mysql_client.session_insert_list(object_list)
                        self.mysql_client.session_commit()
                    else:
                        SpiderException("抓取json异常", self.task_id, url, self.site_name)

                except Exception:
                    m = traceback.format_exc()
                    SpiderException(m, self.task_id, url, self.site_name)
                # 目前为测试状态，只抓取前两页内容，正式上线前将break删掉
                break
        else:
            SpiderException("抓取json异常", self.task_id, url, self.site_name)


    def added_parse(self):
        pass

    def parse_list(self, json_data):
        # 解析获取到的json

        object_list = list()
        case_list = json_data["message"]["result"]
        for case in case_list:

            item = dict()
            item["taskid"] = self.task_id
            item["release_date"] = case.get("lastBroadcastTimeString")  # 发布日期
            item["title"] = get_content(case.get("caseName"))  # 标题
            item["court_y"] = get_content(case.get("belongOrgName"))  # 法院
            item["court_t"] = get_content(case.get("openCourtAddr"))  # 法庭
            item["start_court_t"] = get_content(case.get("openCourtDateString"))  # 开庭日期
            item["court_num"] = get_content(case.get("caseNo"))  # 案号
            item["case_type"] = get_content(case.get("caseTypeString"))  # 案件类型
            item["court_case"] = get_content(case.get("causePlacedOnFile"))  # 案由
            item["trial_cause"] = get_content(case.get("underJustice")).strip()  # 审判人员

            try:
                dex = case["litigants"].index("被告:")
                item["plaintiff"] = case["litigants"][:dex].replace("原告:", "")[:-1]  # 原告
                item["defendant"] = case["litigants"][dex:].replace("被告:", "")  # 被告
            except:
                item["plaintiff"] = ""
                item["defendant"] = case.get("litigants")

            item["site_name"] = self.site_name  # 网站名称

            # remarks = get_content(case.get("remarks"))
            # item["bulletin_way"] = "案件:" + item["title"] + ";归属法院：" + item["court_y"] + ";案号：" + item[
            #     "court_num"] + ";案件类型：" + case["caseTypeString"] + ";承办法官：" + item[
            #     "trial_cause"] + ";当事人：" + item["party"] + ";开庭地点：" + item[
            #     "court_part"] + ";开庭时间：" + item["start_court_t"] + ";案件内容：" + remarks  # 公告内容

            b = BulletinCourt(**item)
            object_list.append(b)
        return object_list

    def get_total_page(self, json_data):
        # 获取总页数
        try:
            total_page = json_data["message"]["totalPages"]
            return int(total_page)
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.task_id, self.site_name, json_data)
            return 0


def get_content(content):
    return content if content else ""


if __name__ == "__main__":

    jiangxi_spider = Spider()
    jiangxi_spider.parse()
