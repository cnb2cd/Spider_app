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


def today_date(rst):
    doc = pq(rst)
    ct = doc('div.ggnr')
    h2 = ct('h2').text()
    h3 = ct('h3').text()
    p = ct('p').text()
    t1 = ct('div.text-01').text()
    t2 = ct('div.text-02').text()
    html = h2 + '\r\n' + h3 + '\r\n' + p + '\r\n' + t1 + '\r\n' + t2
    print(html)

    pass


today_date(rst)