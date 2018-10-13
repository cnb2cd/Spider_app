# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/11 20:57
@desc 使用sql
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

from lib.spider_exception import SpiderException
from lib.config import mysql_setting
if not mysql_setting:
    raise Exception("在sqlalchemy初始化的时候失败了")

host = mysql_setting.get("host")
user = mysql_setting.get("user")
passwd = mysql_setting.get("passwd")
db = mysql_setting.get("db")
charset = mysql_setting.get("charset")
port = mysql_setting.get("port")

engine = create_engine(
            "mysql+pymysql://" + user + ":" + passwd + "@" + host + ":" + port + "/" + db + "?charset=" + charset,
            pool_size=30, echo=False, pool_recycle=3600, encoding="utf-8")
Base = declarative_base()


class MysqlBasic:

    def __init__(self):
        self.db_session = get_session()
        self.data_list = []

    def session_commit(self, task_id):
        suc = False
        try:
            self.db_session.commit()
            suc = True
        except Exception as e:
            self.db_session.rollback()
            SpiderException(traceback.format_exc(), task_id, self.data_list)
        return suc

    def session_insert(self, data):
        self.data_list = []
        self.data_list.append(data)
        self.db_session.add(data)

    def session_insert_list(self, data_list):
        self.data_list = []
        self.data_list = data_list
        self.db_session.add_all(data_list)

    def session_close(self):
        self.db_session.close()





def get_session():
    Base.metadata.create_all(engine)
    session_m = sessionmaker(bind=engine)
    session = session_m()
    return session





