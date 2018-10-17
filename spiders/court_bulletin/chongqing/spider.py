# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/17 09:55
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
import math
import time

log = logging.getLogger()


class Spider(MainSpider):

    site_name = '重庆法院公共服务网'

    def __init__(self, taskid):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = 'http://www.cqfygzfw.com/court/gg_listgg.shtml?gg.endDate={end}&gg.startDate={start}' \
                   '&gg.fydm=&gg.ggnr=&page={page}'
        self.taskid = taskid

    def parse(self):
        log.info('开始抓取重庆法院公共服务网第{page}页信息'.format(page='1'))
        ts = datetime.date.today()
        tm = datetime.date.today() + datetime.timedelta(days=365)
        self.http.http_session(self.url.format(end=str(tm), start=str(ts), page='1'), 'get', headers=self.http.headers)
        r = self.http.parse_html().replace('&#9658', '')
        log.info('解析重庆法院公共服务网第{page}页信息'.format(page='1'))
        p_list = self.parse_list(r)
        b_list = list()
        for p in p_list:
            d_url = 'http://www.cqfygzfw.com/court/gg_ggxx.shtml?gg.id=' + p['det_url']
            log.info('开始抓取重庆法院公共服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p)+1)))
            self.http.http_session(d_url, 'get', headers=self.http.headers)
            det_mess = self.http.parse_html()
            log.info('解析重庆法院公共服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p)+1)))
            self.parse_info(det_mess, p)
            t_way = self.taskid + str(time.time()) + '.txt'
            file_out(t_way, p['html'])
            p['bulletin_way'] = t_way
            p.pop('det_url')
            p.pop('html')
            p['taskid'] = self.taskid
            b = BulletinCourt(**p)
            b_list.append(b)
        log.info('存储天津法院网第{page}页数据'.format(page='1'))
        self.mysql_client.session_insert_list(b_list)
        self.mysql_client.session_commit()
        p_total = self.page_total(r)
        print(p_total)
        for total in range(2, p_total):
            try:
                log.info('开始抓取重庆法院公共服务网第{page}页信息'.format(page=str(total)))
                self.http.http_session(self.url.format(end=str(tm), start=str(ts), page=str(total)), 'get',
                                       headers=self.http.headers)
                r = self.http.parse_html().replace('&#9658', '')
                log.info('解析重庆法院公共服务网第{page}页信息'.format(page=str(total)))
                p_list = self.parse_list(r)
                b_list = list()
                for p in p_list:
                    d_url = 'http://www.cqfygzfw.com/court/gg_ggxx.shtml?gg.id=' + p['det_url']
                    log.info('开始抓取重庆法院公共服务网第{page},第{strip}条信息'.format(page=str(total),
                                                                       strip=str(p_list.index(p) + 1)))
                    self.http.http_session(d_url, 'get', headers=self.http.headers)
                    det_mess = self.http.parse_html()
                    log.info('解析重庆法院公共服务网第{page},第{strip}条信息'.format(page=str(total),
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
                log.info('存储重庆法院公共服务网第{page}页数据'.format(page=str(total)))
                self.mysql_client.session_insert_list(b_list)
                self.mysql_client.session_commit()

            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url)
            break
        self.mysql_client.session_close()
        log.info('抓取天津法院网结束')

    def added_parse(self):
        pass

    def parse_list(self, r):
        doc = pq(r)
        tb = doc('div.r_wenben table.table_ys tbody')
        trs = tb('tr')
        info_list = list()
        for tr in trs.items():
            item = dict()
            tds = tr('td')
            cy = tds.eq(0).text()
            cn = tds.eq(1).text().strip()
            st = tds.eq(2).text()
            du = tds.eq(1).children('a').attr('onclick').replace('openKtgg(\'', '').replace('\')', '').strip()
            item['court_y'] = cy
            item['court_num'] = cn
            item['start_court_t'] = st
            item['det_url'] = du
            info_list.append(item)
        return info_list


    def parse_info(self, rs, item):
        doc = pq(rs)
        title = doc('div.tc_window_bt').text()
        case_num = doc('td.tc_td01').text()
        content = doc('table.table_ys2 tr').eq(1).children('td').text()
        html = title + '\r\n' + case_num + '\r\n' + content
        item['html'] = html
        item['title'] = title

    def page_total(self, res):
        try:
            str0 = int(re.search('共\d*条', res).group().replace('共', '').replace('条', ''))
            connt = math.ceil(str0 / 15)
            return connt
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, '解析总页数异常')
            return 0


s = Spider("111111111")
s.parse()