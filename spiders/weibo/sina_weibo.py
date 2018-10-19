# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/16 18:55
@desc
"""

import copy
from pyquery import PyQuery as pq
import time
import re

from spiders import MainSpider
from lib.http_request import header
from .model.search_condition import SearchCondition
from .model.weibo_entity import Blogger
from .exception import NotSearchConditionException
from .net_http import send_http


class SinaWeiboSearch(MainSpider):

    time_regex = r"seqid:(\d+)"
    task_id = "sina_weibo_search"
    sitename = "s.weibo.com"
    search_page_title = "微博搜索"

    def __init__(self, search_condition):

        MainSpider.__init__(self, task_id=self.task_id)
        self.headers = copy.copy(header)
        if not isinstance(search_condition, SearchCondition):
            raise NotSearchConditionException("判断搜索的条件")
        self.search_condition = search_condition
        self.html = ""

    def parse(self):
        """
        执行函数
        :return:
        """
        self.search_page_action()
        self.get_total_page()
        has_next_page = self.has_next_page()
        while has_next_page:
            self.search_condition.page += 1
            self.search_page_action()
            has_next_page = self.has_next_page()

    def added_parse(self):
        """
        补漏
        :return:
        """
        pass

    def search_page_action(self):
        """
        搜索页面的数据
        :return: code 0 正确  1errorpage 2验证码 3正常
        """
        url = self.search_condition.get_ser_condition_url()
        code, html = send_http(url, headers=self.headers)
        self.html = html

        is_error_page = self.check_out_is_error_page(code)
        self.logger.info(url+":"+str(is_error_page))
        if is_error_page:
            self.logger.error(html)
            return

        is_yzm = self.check_out_is_yzm_page()
        self.logger.info(url + ":" + str(is_error_page))
        if is_yzm:
            self.logger.error(html)
            self.verify_yzm_action()
            return

        is_content = self.parse_content()
        if is_content:
            self.analyzer_doc_add_db()
        else:
            self.logger.error(html)

    def parse_content(self):
        """
        将搜索的html页面 转化为 document
        :return:
        """
        is_content = False
        items = pq(self.html)('div[@action-type="feed_list_item"]').items()
        items = list(items)
        if len(items) > 0:
            is_content = True
            return is_content
        else:
            return False

    def check_out_is_error_page(self, rep_code):
        """
        判断是不是有错误的页面
        :param rep_code:
        :return:
        """
        html = self.html
        is_err_page = True
        if rep_code != 200 or not html:
            return is_err_page

        if not isinstance(html, str):
            return is_err_page

        if html.startswith("{"):
            return is_err_page

        doc_ = pq(html).find("title").text()
        if doc_ != self.search_page_title:
            return is_err_page

        return not is_err_page

    def check_out_is_yzm_page(self):
        """
        判断是不是有验证码
        :return: True 是验证码页面 False 不是
        """
        # todo
        return False

    def verify_yzm_action(self):
        """
        验证码的处理
        :return:
        """
        pass

    def analyzer_doc_add_db(self):
        """
        解析页面的数据
        :return:
        """

        contents = pq(self.html)("div[@action-type='feed_list_item']").items()
        item_list = []
        for content in contents:
            item = {}
            mid = content.attr("mid")
            content_node = content("p[@node-type='feed_list_content']").eq(0)
            nick_name = content_node.attr("nick-name")
            content_str = content_node.text()
            content_node_forward = content("div[@node-type='feed_list_forwardContent']").eq(0)
            content_forward_str = content_node_forward.text()
            time_url_info = content('p[@class="from"]').eq(-1)("a").eq(0)
            url = "https://" + time_url_info.attr("href")
            suda_data = time_url_info.attr("suda-data")
            time_data = time_url_info.text()
            data = re.search(self.time_regex, suda_data)
            time_stamp_str = data.group(1)[0:10]
            date_ = time_parse(time_stamp_str, time_data)
            content_str = content_str + content_forward_str if content_forward_str else content_str

            item["author"] = nick_name
            item['publish_time'] = date_
            item['content'] = content_str
            item['blogger_url'] = url
            item['blogger_id'] = mid
            item['key_word'] = self.search_condition.ser_word
            blogger = Blogger(**item)
            item_list.append(blogger)

        self.mysql_client.session_insert_list(item_list)
        self.mysql_client.session_commit()

    def get_total_page(self):
        """
        总共多少页
        :return:
        """
        res_txt = pq(self.html)('.result').text()
        self.logger.info(res_txt)

    def has_next_page(self):
        res_txt = pq(self.html)('.next').attr("href")
        self.logger.info(str(res_txt))
        return True if res_txt else False


def time_parse(time_stamp, time_str):
    """
    微博搜索到的数据的时间制定 格式化
    :param time_stamp:  搜索时的时间戳
    :param time_str:  类似于： 4秒前
                        5分钟前 今天12:12 05月03号 12:11
                        2017年12月10日 12:11
    :return:
    """

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


def action_test():
    try:
        search_condition = SearchCondition(ser_word="梅西", ser_time_start="2018-10-19")
        SinaWeiboSearch(search_condition).parse()
    except Exception as e:
        print(e)


