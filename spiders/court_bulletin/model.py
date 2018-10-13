# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/13 14:07
@desc 开庭公告
"""
from lib.db.mysql_basic import Base
from sqlalchemy import Column, String, DATE, Integer


class BulletinCourt(Base):

    __tablename__ = 'gov_bulletin_court'

    seriono = Column(Integer, primary_key=True)
    taskid = Column(String(50))
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

    def __repr__(self):
        format_field = f"\"task_id\":\"{self.taskid}\"" + \
                       f",\"release_date\":\"{self.release_date}\"" + \
                       f",\"title\":\"{self.title}\"" + \
                       f",\"bulletin_way\":\"{self.bulletin_way}\"" + \
                       f",\"court_y\":\"{self.court_y}\"" + \
                       f",\"court_t\":\"{self.court_t}\"" + \
                       f",\"start_court_t\":\"{self.start_court_t}\"" + \
                       f",\"court_num\":\"{self.court_num}\"" + \
                       f",\"court_case\":\"{self.court_case}\"" + \
                       f",\"undertake_dep\":\"{self.undertake_dep}\"" + \
                       f",\"plaintiff\":\"{self.plaintiff}\"" + \
                       f",\"trial_cause\":\"{self.trial_cause}\"" + \
                       f",\"defendant\":\"{self.defendant}\"" + \
                       f",\"court_part\":\"{self.court_part}\"" + \
                       f",\"court_end_t\":\"{self.court_end_t}\"" + \
                       f",\"court_status\":\"{self.court_status}\"" + \
                       f",\"party\":\"{self.party}\"" + \
                       f",\"site_name\":\"{self.site_name}\""
        format_field = "{" + format_field + "}"
        return format_field





