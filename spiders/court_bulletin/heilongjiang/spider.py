# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/17 19:38
@desc
"""

from spiders import MainSpider
from lib.http_request import HttpRequest
from lib.spider_exception import SpiderException
import traceback
import logging
from pyquery import PyQuery as pq
from spiders.court_bulletin.model import BulletinCourt
from util.file import file_out
import datetime
import re
import time

log = logging.getLogger()


class Spider(MainSpider):

    site_name = '黑龙江法院网'

    def __init__(self, taskid):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = 'http://www.hljcourt.gov.cn/ktgg/index.php?p={page}&st={start}&et={end}'
        self.taskid = taskid

    def parse(self):
        log.info('开始抓取黑龙江法院网第{page}页信息'.format(page='1'))
        ts = datetime.date.today()
        tm = datetime.date.today() + datetime.timedelta(days=365)
        self.http.http_session(self.url.format(page='1', start=str(ts), end=str(tm)), 'get', headers=self.http.headers)
        self.http.set_charset('gb2312')
        r = self.http.parse_html()
        print(r)
        log.info('解析抓取黑龙江法院网第{page}页信息'.format(page='1'))
        p_list = self.parse_list(r)
        b_list = list()
        for p in p_list:
            try:
                d_url = 'http://www.hljcourt.gov.cn/ktgg/' + p['det_url']
                log.info('开始抓取黑龙江法院网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
                self.http.http_session(d_url, 'get', headers=self.http.headers)
                det_mess = self.http.parse_html()
                log.info('解析黑龙江法院网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
                self.parse_info(det_mess, p)
                t_way = self.taskid + str(time.time()) + '.txt'
                file_out(t_way, p['html'])
                p['bulletin_way'] = t_way
                p.pop('det_url')
                p.pop('html')
                p['taskid'] = self.taskid
                b = BulletinCourt(**p)
                b_list.append(b)
            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, d_url)
            break
        log.info('存储黑龙江法院网第{page}页数据'.format(page='1'))
        self.mysql_client.session_insert_list(b_list)
        self.mysql_client.session_commit()
        p_total = self.page_total(r)
        for total in range(2, p_total):
            try:
                log.info('开始抓取黑龙江法院网第{page}页信息'.format(page=str(total)))
                self.http.http_session(self.url.format(page=str(total), start=str(ts), end=str(tm)), 'get',
                                       headers=self.http.headers)
                r = self.http.parse_html()
                log.info('解析黑龙江法院网第{page}页信息'.format(page=str(total)))
                p_list = self.parse_list(r)
                b_list = list()
                for p in p_list:
                    try:
                        d_url = 'http://www.hljcourt.gov.cn/ktgg/' + p['det_url']
                        log.info('开始抓取黑龙江法院网第{page},第{strip}条信息'.format(page=str(total),
                                                                        strip=str(p_list.index(p) + 1)))
                        self.http.http_session(d_url, 'get', headers=self.http.headers)
                        det_mess = self.http.parse_html()
                        log.info('解析黑龙江法院网第{page},第{strip}条信息'.format(page=str(total),
                                                                      strip=str(p_list.index(p) + 1)))
                        self.parse_info(det_mess, p)
                        t_way = self.taskid + str(time.time()) + '.txt'
                        file_out(t_way, p['html'])
                        p['bulletin_way'] = t_way
                        p.pop('det_url')
                        p.pop('html')
                        p['taskid'] = self.taskid
                        b = BulletinCourt(**p)
                        b_list.append(b)
                    except Exception:
                        m = traceback.format_exc()
                        SpiderException(m, self.taskid, self.site_name, d_url)

                log.info('存储黑龙江法院网第{page}页数据'.format(page=str(total)))
                self.mysql_client.session_insert_list(b_list)
                self.mysql_client.session_commit()

            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url.format(end=str(tm), start=str(ts),
                                                                                page=str(total)))
        self.mysql_client.session_close()
        log.info('抓取黑龙江法院网结束')

    def added_parse(self):
        pass

    def parse_list(self, r):
        info_list = list()
        doc = pq(r)
        tb = doc('table tbody').children('tr').children('td')
        k = int(tb.size() / 5)
        for i in range(0, k):
            item = dict()
            title = tb.eq(i * 5 + 1).text()
            court_num = tb.eq(i * 5 + 2).text()
            court_part = tb.eq(i * 5 + 3).text()
            start_court_t = tb.eq(i * 5 + 4).text()
            det_url = tb.eq(i * 5 + 1).children('div').children('a').attr('href')
            item['title'] = title
            item['court_num'] = court_num
            item['court_part'] = court_part
            item['start_court_t'] = start_court_t
            item['det_url'] = det_url
            info_list.append(item)
        return info_list

    def parse_info(self, rs, item):
        doc = pq(rs)
        ct = doc('div.ggnr')
        h2 = ct('h2').text()
        h3 = ct('h3').text()
        p = ct('p').text()
        t1 = ct('div.text-01').text()
        t2 = ct('div.text-02').text()
        html = h2 + '\r\n' + h3 + '\r\n' + p + '\r\n' + t1 + '\r\n' + t2
        item['html'] = html
        item['court_y'] = h2

    def page_total(self, res):
        try:
            k = int(re.search('共\d*页', res).group().replace('共', '').replace('页', ''))
            return k
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, '解析总页数异常')
            return 0


s = Spider("111111111")
s.parse()