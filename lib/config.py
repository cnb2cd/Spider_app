# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/11 19:25
@desc  配置文件
"""
import os
py_pro = os.getenv("PY_PRO")


class EmailSender:
    """
    邮件的发送者的 信息
    """
    mail_host = "smtp.aliyun.com"
    mail_user = "tigerobo001@aliyun.com"
    mail_pass = "tigerobo2017"


class RedisConnectConfig:
    """
    Redis 链接的配置
    """
    tiger_local = "tiger_local"
    tiger_spider_1 = "tiger_spider-1"
    tiger_spider_1_local = "tiger_spider-1_local"
    config_ = {
        tiger_local: {
                        "host": "192.168.0.200",
                        "port": 6379,
                        "db": 0,
                        "password": "tigerobo2017"
                       },
        tiger_spider_1: {
                          "host": "10.0.6.200",
                          "port": 6379,
                          "db": 0,
                          "password": "wht123456"
                        },
        tiger_spider_1_local: {
                        "host": "127.0.0.1",
                        "port": 6379,
                        "db": 0,
                        "password": "wht123456"
        }

    }


class MysqlConnectConfig:
    """
    mysql  链接的配置
    """
    tiger_spider = "tiger_spider"
    tiger_local = "tiger_local"
    config_ = {
        tiger_local: {
            "host": "192.168.0.200",
            "user": "wechat",
            "passwd": "wechattask",
            "db": "test_spider",
            "charset": "utf8",
            "port": "3306"
        },
        tiger_spider: {
            "host": "rm-uf681sz3um9oi3yg9.mysql.rds.aliyuncs.com",
            "user": "datap_db_admin",
            "passwd": "Superdatap_!",
            "db": "spider",
            "charset": "utf8",
            "port": "3306"
        }
    }


class LoggerConfig:
    format_str = "%(asctime)s -%(module)s-[%(lineno)s]-%(thread)s-%(levelname)s - %(message)s"
    file_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/"+"log/logger"


mysql_setting = MysqlConnectConfig.config_.get(MysqlConnectConfig.tiger_spider) if py_pro \
                 else MysqlConnectConfig.config_.get(MysqlConnectConfig.tiger_local)

redis_setting = RedisConnectConfig.config_.get(RedisConnectConfig.tiger_spider_1_local) if py_pro \
                else RedisConnectConfig.config_.get(RedisConnectConfig.tiger_local)
