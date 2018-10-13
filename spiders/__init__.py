# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018-10-12
@desc
"""

import logging

from lib.logger_magic import initlog_file
from lib.db.mysql_basic import get_session

initlog_file()
logger = logging.getLogger()


class MainSpider:

    def __init__(self):
        """
        增加了 日志类
        增加了 db_session
        """
        self.logger = logger
        self.db_session = get_session()

    def parse(self):
        pass

    def added_parse(self):
        pass
