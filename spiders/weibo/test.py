# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/18 19:38
@desc
"""

from pyquery import PyQuery as pq
import re
import time

def time_parse(time_stamp, time_str):

    if not isinstance(time_str, str):
        return

    time_stamp = int(time_stamp)
    if time_str.find("秒") > -1:
        time_sec = time_str.split("秒")[0].strip()
        time_stamp = time_stamp - int(time_sec)
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))
        return date

    if time_str.find("分") > -1:
        time_min = time_str.split("分")[0].strip()
        time_stamp = time_stamp - int(time_min) * 60
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))
        return date

    if time_str.find("今天") > -1:
        time_str = time_str.split("今天")[1].strip()
        date = time.strftime("%Y-%m-%d", time.localtime(time_stamp))
        date += " "+time_str
        return date

    if time_str.find("年") > -1:
        time_all = time_str.strip()
        time_tup = time.strptime(time_all, "%Y年-%m月-%d日 %H:%M")
        date = time.strftime("%Y-%m-%d %H:%M:%S", time_tup)
        return date

    if time_str.find("日") > -1:
        year_ = time.strftime("%Y", time.localtime(time_stamp))
        date = year_ + "-" + time_str.replace("月", "-").replace("日", "")
        return date


regex = r"seqid:(\d+)"
pq = pq(filename='weibo_search.html')
title = pq("title").text()
contents = pq("div[@action-type='feed_list_item']").items()
for content in contents:
    mid = content.attr("mid")
    content_node = content("p[@node-type='feed_list_content']").eq(0)
    nick_name = content_node.attr("nick-name")
    content_str = content_node.text()
    content_node_forward = content("div[@node-type='feed_list_forwardContent']").eq(0)
    content_forward_str = content_node_forward.text()
    time_url_info = content('p[@class="from"]').eq(-1)("a").eq(0)
    # time_url_info.make_links_absolute()
    url = "https://" + time_url_info.attr("href")
    suda_data = time_url_info.attr("suda-data")
    time_data = time_url_info.text()
    data = re.search(regex, suda_data)
    time_stamp_str = data.group(1)[0:10]
    date_ = time_parse(time_stamp_str, time_data)










