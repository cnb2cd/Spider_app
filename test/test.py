# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from util.date_parse import *
from bs4 import BeautifulSoup
import pyquery
from util.date_parse import *
import time, datetime
import re
import math
f = open('a.txt', 'r', encoding='GB18030')
r = f.read()
rst = r.replace('&nbsp;', '')
f.close()


def today_date(rs):
    time0 = get_today_date()
    time1 = '2019-7-16'
    strftime0 = datetime.datetime.strptime(time1, "%Y-%m-%d")
    strftime1 = datetime.datetime.strptime(time0, "%Y-%m-%d")
    fg = strftime1 > strftime0
    if fg == True:
       print('//////////')
    pass


def run(rs):
    item = dict()
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
    print(item)


    pass


run(rst)