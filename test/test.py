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
rst = r.replace('&nbsp;', '').replace('&#9658', '')
f.close()


def today_date(rst):

    pass


today_date(rst)