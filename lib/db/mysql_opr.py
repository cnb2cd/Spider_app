# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/11 20:59
@desc  直接链接数据库
"""

from sqlalchemy import create_engine
import logging
from lib.config import mysql_setting

logger = logging.getLogger(__name__)


class MysqlDB(object):
    """
    数据库的链接
    """

    def __init__(self, **config):
        """
        :param config:
        """
        if not config:
            config = mysql_setting
        if not config:
            raise Exception("数据库配置失败")

        host = config.get("host")
        user = config.get("user")
        passwd = config.get("passwd")
        db = config.get("db")
        charset = config.get("charset")
        port = config.get("port")
        print("链接数据库:", config)
        self.engine = create_engine(
            "mysql+pymysql://" + user + ":" + passwd + "@" + host + ":" + port + "/" + db + "?charset=" + charset,
            pool_size=10, echo=False, pool_recycle=3600, encoding="utf-8")
        print("链接数据库: suc:", config)

    def execute_data(self, sql, *param):
        """
        执行sql
        :param sql: mysql 语句 可以带%s
        :param param: tuple
        :return:
        """
        conn = None
        result = {}
        suc = False
        data = None
        error = None
        try:
            conn = self.engine.connect()
            if param:
                cur = conn.execute(sql, param)
            else:
                cur = conn.execute(sql)
            if cur.returns_rows:
                data = cur.fetchall()
            suc = True
        except Exception as e:
            logger.error(sql+":"+str(param))
            error = str(e)
            logger.exception(str(e))
        finally:
            if conn:
                conn.close()
        result["suc"] = suc
        result["data"] = data
        result["error"] = error
        return result
