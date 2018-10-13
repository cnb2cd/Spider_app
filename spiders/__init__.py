# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018-10-12
@desc
"""

import logging

from lib.logger_magic import initlog_file
from lib.db.mysql_basic import MysqlBasic

initlog_file()
logger = logging.getLogger()


class MainSpider:

    def __init__(self, task_id):
        """
        增加了 日志类
        增加了 db_session
        """
        self.logger = logger
        self.mysql_client = MysqlBasic(task_id=task_id)

    def parse(self):
        pass

    def added_parse(self):
        pass
