# -*- coding: utf-8 -*-

"""
@author pxm
@time  2018/10/15 11:11
@desc
"""

from spiders import MainSpider
from lib.http_request import HttpRequest
from lib.spider_exception import SpiderException
import traceback
import logging
from pyquery import PyQuery as pq
from spiders.court_bulletin.model import BulletinCourt

log = logging.getLogger()



class Spider(MainSpider):

    site_name = '天津法院网'

    def __init__(self, taskid, url):
        MainSpider.__init__(self, task_id=taskid)
        self.http = HttpRequest(taskid, self.site_name)
        self.url = url

    def parse(self):
        log.info('开始抓取==================天津法院网')
        ct = 0
        while ct < 30:
            self.http.http_session(self.url, 'get', headers=self.http.headers)
            try:
                r = self.http.parse_html()
                p_list = self.parse_list(r)
                ic = self.is_c(r)
                object_list = list()
                for i in p_list:
                    try:
                        d_url = 'http://tjfy.chinacourt.org' + i['det_url']
                        self.http.http_session(d_url, 'get', headers=self.http.headers)
                        rl = self.http.parse_html()
                        print(rl)
                        self.parse_info(rl, i)
                        #需要写出文件
                        print(i)
                        i.pop('det_url')
                        i.pop('html')
                        b = BulletinCourt(**i)
                        object_list.append(b)
                        break
                    except Exception:
                        m = traceback.format_exc()
                        SpiderException(m, self.taskid, self.site_name, self.url)
                self.mysql_client.session_insert_list(object_list)
                self.mysql_client.session_commit()
                if ic == 0:
                    break
            except Exception:
                m = traceback.format_exc()
                SpiderException(m, self.taskid, self.site_name, self.url)
            ct += 1
            break
        self.mysql_client.session_close()
    def added_parse(self):
        pass

    def parse_list(self, r):
        doc = pq(r)
        main = doc('div#main')
        ul = main('ul li').items()
        p_list = list()
        for l in ul:
            item = dict()
            hr = l('a').attr('href')
            title = l('a').attr('title')
            time = l('span.right').text()
            item["taskid"] = '111111111'
            item['det_url'] = hr
            item['start_court_t'] = time
            p_list.append(item)
        return p_list

    def parse_info(self, rs, item):
        rr = pq(rs)
        det = rr('div.detail')
        tit = det('div.title')
        title = tit('div.b_title').text()
        txt = tit('div.sth_a span').eq(0).text()
        time = txt.split('：')[2].strip()
        cont = det('div.text').text()
        html = title + '\r\n' + txt + '\r\n' + cont
        item['release_date'] = time
        item['html'] = html
        item['title'] = title

    def is_c(self, res):
        try:
            doc = pq(res)
            d = doc('#category .paginationControl').eq(0)
            c = int(d('.current').text())
            a = d('a')

            count = 0
            for var in a.items():
                count = count + 1
                s = var.text()
                if s == '下一页':
                    break

            t = a.eq(count - 2)
            ts = int(t.text())
            if ts <= c:
                return 0
            else:
                return 1
        except Exception:
            return 1


s=Spider("111111111", "http://tjfy.chinacourt.org/article/index/id/MzDIMTCwMDAwNCACAAA=.shtml")
s.parse()