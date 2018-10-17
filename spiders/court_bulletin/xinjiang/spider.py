# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/17 16:55
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

    site_name = '新疆法院诉讼服务网'

    def __init__(self, taskid):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = 'http://220.171.35.30/ktggSearchResult.jspx?fyid=&ktdd=&page={page}'
        self.taskid = taskid

    def parse(self):
        log.info('开始抓取新疆法院诉讼服务网第{page}页信息'.format(page='1'))
        self.http.http_session(self.url.format(page='1'), 'get', headers=self.http.headers)
        r = self.http.parse_html()
        log.info('解析新疆法院诉讼服务网第{page}页信息'.format(page='1'))
        p_list = self.parse_list(r)
        b_list = list()
        for p in p_list:
            d_url = p['det_url']
            log.info('开始抓取新疆法院诉讼服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p)+1)))
            self.http.http_session(d_url, 'get', headers=self.http.headers)
            det_mess = self.http.parse_html()
            log.info('解析新疆法院诉讼服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p)+1)))
            self.parse_info(det_mess, p)
            t_way = self.taskid + str(time.time()) + '.txt'
            file_out(t_way, p['html'])
            p['bulletin_way'] = t_way
            p.pop('det_url')
            p.pop('html')
            p['taskid'] = self.taskid
            b = BulletinCourt(**p)
            b_list.append(b)
        log.info('存储新疆法院诉讼服务网第{page}页数据'.format(page='1'))
        self.mysql_client.session_insert_list(b_list)
        self.mysql_client.session_commit()
        p_total = self.page_total(r)
        for total in range(2, p_total):
            try:
                log.info('开始抓取新疆法院诉讼服务网第{page}页信息'.format(page=str(total)))
                self.http.http_session(self.url.format(page=str(total)), 'get', headers=self.http.headers)
                r = self.http.parse_html()
                log.info('解析重新疆法院诉讼服务网第{page}页信息'.format(page=str(total)))
                p_list = self.parse_list(r)
                b_list = list()
                for p in p_list:
                    d_url = p['det_url']
                    log.info('开始重新疆法院诉讼服务网第{page},第{strip}条信息'.format(page=str(total),
                                                                      strip=str(p_list.index(p) + 1)))
                    self.http.http_session(d_url, 'get', headers=self.http.headers)
                    det_mess = self.http.parse_html()
                    log.info('解析新疆法院诉讼服务网第{page},第{strip}条信息'.format(page=str(total),
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
                log.info('存储新疆法院诉讼服务网第{page}页数据'.format(page=str(total)))
                self.mysql_client.session_insert_list(b_list)
                self.mysql_client.session_commit()
            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url)
        self.mysql_client.session_close()
        log.info('抓取新疆法院诉讼服务网结束')

    def added_parse(self):
        pass

    def parse_list(self, r):
        doc = pq(r)
        trs = doc('table tr')
        p_list = list()
        for i in range(1, trs.size()):
            item = dict()
            tr = trs.eq(i)
            td1 = tr('td').eq(1)
            item['det_url'] = td1('a').attr('href')
            item['title'] = td1('a').attr('title')
            item['court_y'] = tr('td').eq(2).text()
            item['start_court_t'] = tr('td').eq(3).text()
            p_list.append(item)
        return p_list

    def parse_info(self, rs, item):
        doc = pq(rs)
        title = doc('title').text()
        con = doc('div.con')
        c_title = con('div.title').text()
        court = con('origin').text()
        p = con('div.content').children("p")
        c_html = ''
        for var in p.items():
            c_html += var.text() + '\r\n'
        html = title + '\r\n' + c_title + '\r\n' + court + '\r\n' + c_html
        item['html'] = html

    def page_total(self, res):
        try:
            doc = pq(res)
            jump = doc('div.jump div.skip').children('a')
            len = jump.eq(jump.length - 1)
            k = int(len.attr('onclick').replace('turnPage(', '').replace(')', ''))
            return k
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, '解析总页数异常')
            return 0


s = Spider("111111111")
s.parse()