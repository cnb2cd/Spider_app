# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/18 15:17
@desc
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, TIMESTAMP, Text, Column
Base = declarative_base()


class Blogger(Base):

    __tablename__ = 'weibo_search_blogger'
    id = Column(Integer, primary_key=True)
    author = Column(String(50))
    publish_time = Column(TIMESTAMP())
    content = Column(Text())
    blogger_url = Column(String(200))
    blogger_id = Column(String(50))
    key_word = Column(String(50))









