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

    site_name = '宁夏高级人民法院诉讼服务网'

    def __init__(self, taskid):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = 'http://ssfw.nxfy.gov.cn/ktgg/index.jhtml'
        self.taskid = taskid

    def parse(self):
        log.info('开始抓取宁夏高级人民法院诉讼服务网第{page}页信息'.format(page='1'))
        self.http.http_session(self.url.format(page='1'), 'get', headers=self.http.headers)
        r = self.http.parse_html()
        log.info('解析宁夏高级人民法院诉讼服务网第{page}页信息'.format(page='1'))
        doc = pq(r)
        skip = doc('div.skip').children('p').children('a')
        nurl = 'http://ssfw.nxfy.gov.cn'+ skip.eq(skip.length - 1).attr('href').replace('&amp;', '&')\
            .replace('pagecur=1', 'pagecur={pageno}')
        p_list = self.parse_list(r)
        b_list = list()
        for p in p_list:
            try:
                d_url = p['det_url']
                log.info('开始抓取宁夏高级人民法院诉讼服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
                self.http.http_session(d_url, 'get', headers=self.http.headers)
                det_mess = self.http.parse_html()
                log.info('解析宁夏高级人民法院诉讼服务网第{page},第{strip}条信息'.format(page='1', strip=str(p_list.index(p) + 1)))
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
        log.info('存储宁夏高级人民法院诉讼服务网第{page}页数据'.format(page='1'))
        self.mysql_client.session_insert_list(b_list)
        self.mysql_client.session_commit()
        p_total = self.page_total(r)
        for total in range(2, p_total):
            try:
                log.info('开始抓取宁夏高级人民法院诉讼服务网第{page}页信息'.format(page=str(total)))
                self.http.http_session(nurl.format(pageno=str(total)), 'get', headers=self.http.headers)
                r = self.http.parse_html()
                log.info('解析宁夏高级人民法院诉讼服务网第{page}页信息'.format(page=str(total)))
                p_list = self.parse_list(r)
                b_list = list()
                for p in p_list:
                    try:
                        d_url = p['det_url']
                        log.info('开始抓取宁夏高级人民法院诉讼服务网第{page},第{strip}条信息'.format(page=str(total),
                                                                               strip=str(p_list.index(p) + 1)))
                        self.http.http_session(d_url, 'get', headers=self.http.headers)
                        det_mess = self.http.parse_html()
                        log.info('解析宁夏高级人民法院诉讼服务网第{page},第{strip}条信息'.format(page=str(total),
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
                log.info('存储宁夏高级人民法院诉讼服务网第{page}页数据'.format(page=str(total)))
                self.mysql_client.session_insert_list(b_list)
                self.mysql_client.session_commit()
            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url)

        self.mysql_client.session_close()
        log.info('抓取宁夏高级人民法院诉讼服务网结束')

    def added_parse(self):
        pass

    def parse_list(self, r):
        p_list = list()
        doc = pq(r)
        sec = doc('ul.sec_list').children('div').children('li')
        for var in sec.items():
            item = dict()
            det_url = var('a').attr('href').replace('&amp;', '&')
            title = var('a').attr('title')
            start_court_t = re.search('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}', title).group()
            item['det_url'] = det_url
            item['title'] = title
            item['start_court_t'] = start_court_t
            p_list.append(item)
        return p_list

    def parse_info(self, rs, item):
        doc = pq(rs)
        con = doc('div.con')
        title = con('div.title').text()
        release_date = re.search('\d{4}-\d{2}-\d{2}', title).group()
        court_y = con('div.origin').text()
        p = con('div.content').children("p")
        c_html = ''
        for var in p.items():
            c_html += var.text() + '\r\n'
        html = title + '\r\n' + court_y + '\r\n' + c_html
        item['release_date'] = release_date
        item['html'] = html
        item['court_y'] = court_y

    def page_total(self, res):
        try:
            doc = pq(res)
            skip = doc('div.skip').children('p').children('a')
            tpage = int(skip.eq(skip.length - 2).text())
            return tpage
        except Exception:
            m = traceback.format_exc()
            SpiderException(m, self.taskid, self.site_name, '解析总页数异常')
            return 0


s = Spider("111111111")
s.parse()