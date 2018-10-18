# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/18 10:43
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
from util.date_parse import get_today_date
import time

log = logging.getLogger()


class Spider(MainSpider):

    site_name = '河北法院网'

    def __init__(self, taskid):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = 'http://hbgy.hbsfgk.org/ktgg/index.jhtml'
        self.taskid = taskid

    def parse(self):
        log.info('开始抓取河北法院网第{page}页信息'.format(page='1'))
        self.http.http_session(self.url.format(page='1'), 'get', headers=self.http.headers)
        r = self.http.parse_html()
        log.info('解析河北法院网第{page}页信息'.format(page='1'))
        doc = pq(r)
        skip = doc('div.turn_page').children('p').children('a.sp_next')
        nurl = 'http://hbgy.hbsfgk.org' + skip.attr('href').replace('pagecur=1', 'pagecur={pageno}')
        p_list = self.parse_list(r)
        b_list = list()
        for p in p_list:
            try:
                d_url = p['det_url']
                log.info('开始抓取河北法院网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
                self.http.http_session(d_url, 'get', headers=self.http.headers)
                det_mess = self.http.parse_html()
                log.info('解析河北法院网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
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
        log.info('存储河北法院网第{page}页数据'.format(page='1'))
        self.mysql_client.session_insert_list(b_list)
        self.mysql_client.session_commit()
        p_total = self.page_total(r)
        for total in range(2, p_total):
            try:
                log.info('开始抓取河北法院网第{page}页信息'.format(page=str(total)))
                self.http.http_session(nurl.format(pageno=str(total)), 'get', headers=self.http.headers)
                r = self.http.parse_html()
                log.info('解析河北法院网第{page}页信息'.format(page=str(total)))
                p_list = self.parse_list(r)
                b_list = list()
                for p in p_list:
                    try:
                        d_url = p['det_url']
                        log.info('开始河北法院网第{page},第{strip}条信息'.format(page=str(total),
                                                                     strip=str(p_list.index(p) + 1)))

                        self.http.http_session(d_url, 'get', headers=self.http.headers)
                        det_mess = self.http.parse_html()
                        log.info('解析河北法院网第{page},第{strip}条信息'.format(page=str(total),
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
                log.info('存储河北法院网第{page}页数据'.format(page=str(total)))
                self.mysql_client.session_insert_list(b_list)
                self.mysql_client.session_commit()
            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url)
            time0 = get_today_date()
            time1 = self.get_n_t(r)
            strftime0 = datetime.datetime.strptime(time1, "%Y-%m-%d")
            strftime1 = datetime.datetime.strptime(time0, "%Y-%m-%d")
            fg = strftime1 > strftime0
            if fg == True:
                break

        self.mysql_client.session_close()
        log.info('抓取河北法院网结束')

    def added_parse(self):
        pass

    def parse_list(self, r):
        doc = pq(r)
        p_list = list()
        sec = doc('ul.sswy_news').children('li')
        for var in sec.items():
            item = dict()
            det_url = var('a').attr('href')
            title = var('a').attr('title')
            start_court_t = re.search('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}', title).group()
            item['det_url'] = det_url
            item['title'] = title
            item['start_court_t'] = start_court_t
            p_list.append(item)
        return p_list

    def parse_info(self, rs, item):
        doc = pq(rs)
        doc = pq(rs)
        con = doc('div.ywzw_con_inner')
        p1 = con.children().eq(0).text()
        h3 = con.children().eq(1).text()
        p2 = con.children().eq(2).text()
        p3 = con.children().eq(3).text()
        p4 = con.children().eq(4).text()
        p5 = con.children().eq(5).text()
        html = p1 + '\r\n' + h3 + '\r\n' + p2 + '\r\n' + p3 + '\r\n' + p4 + '\r\n' + p5
        item['html'] = html
        item['court_y'] = h3
        item['release_date'] = re.search('\d{4}-\d{2}-\d{2}', p1).group()

    def page_total(self, res):
        try:
            doc = pq(res)
            skip = doc('div.turn_page').children('p').children('a')
            tpage = int(skip.eq(skip.length - 2).text())
            if tpage > 500:
                return 500
            else:
                return tpage
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, '解析总页数异常')
            return 0

    def get_n_t(self, r):
        doc = pq(r)
        lst = doc('ul.sswy_news').children('li')
        li = lst.eq(lst.length - 1).children('a').attr('title')
        tm = re.search('\d{4}-\d{2}-\d{2}', li).group()
        return tm

s = Spider("111111111")
s.parse()