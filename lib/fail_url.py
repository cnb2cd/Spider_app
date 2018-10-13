# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/13 16:08
@desc  失败链接
"""
from lib.db.mysql_basic import Base
from sqlalchemy import Column, Integer, String, DATE

class FailUrl(Base):

    __tablename__ = 'gov_bulletin_fail_url'

    taskid = Column(String(50))
    fail_url = Column(String(300))
    url_type = Column(String(10))
    req_time = Column(int(10))
    url_status = Column(int(1))
    site_name = Column(String(50))


