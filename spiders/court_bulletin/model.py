# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/13 14:07
@desc 开庭公告
"""
from lib.db.mysql_basic import Base
from sqlalchemy import Column, Integer, String, DATE


class BulletinCourt(Base):

    __tablename__ = 'gov_bulletin_court'

    taskid = Column(String(20))
    release_date = Column(DATE)
    title = Column(String(50))
    bulletin_way = Column(String(50))
    court_y = Column(String(50))
    court_t = Column(String(50))
    start_court_t = Column(DATE)
    court_num = Column(String(100))
    court_case = Column(String(500))
    undertake_dep = Column(String(100))
    trial_cause = Column(String(20))
    plaintiff = Column(String(400))
    defendant = Column(String(400))
    court_part = Column(String(200))
    schedule_time = Column(DATE)
    court_pur = Column(String(200))
    court_end_t = Column(DATE)
    court_status = Column(String(50))
    party = Column(String(400))
    site_name = Column(String(50))
    collection_time = Column(DATE)





