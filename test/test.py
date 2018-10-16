# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from util.date_parse import *
from bs4 import BeautifulSoup
import pyquery


f = open('a.txt', 'r', encoding='gbk')
r = f.read()
rst = r.replace('&nbsp;', '')
f.close()
def parse_info(r1):
    rr = pq(r1)
    det = rr('div.detail')
    tit = det('div.title')
    title = tit('div.b_title').text()
    txt = tit('div.sth_a span').eq(0).text()
    time = txt.split('：')[2].strip()
    cont = det('div.text').text()
    html = title + '\r\n' + txt +'\r\n' + cont
    print(html)
    pass


parse_info(rst)