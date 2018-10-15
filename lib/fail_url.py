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

    seriono = Column(Integer, primary_key=True)
    taskid = Column(String(50))
    fail_url = Column(String(300))
    url_type = Column(String(10))
    req_time = Column(Integer())
    url_status = Column(Integer())
    site_name = Column(String(50))

    def __repr__(self):
        format_field = f"\"task_id\":\"{self.taskid}\"" + \
                       f",\"fail_url\":\"{self.fail_url}\"" + \
                       f",\"url_type\":\"{self.url_type}\"" + \
                       f",\"bulletin_way\":\"{self.bulletin_way}\"" + \
                       f",\"req_time\":\"{self.req_time}\"" + \
                       f",\"url_status\":\"{self.url_status}\"" + \
                       f",\"site_name\":\"{self.site_name}\""

        format_field = "{" + format_field + "}"
        return format_field
