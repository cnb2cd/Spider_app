# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/10/11 22:09
@redis 链接
"""

import redis
import logging


from lib.config import redis_setting

logger = logging.getLogger(__name__)


class RedisClient(object):

    def __init__(self, **kwargs):
        """
        Args:
            host: str, Redis ip/hostname
            port, int, Redis port
            db: int, Redis default database
            password: int(optional)
        """
        if not kwargs:
            kwargs = redis_setting

        if kwargs:
            self.pool = redis.ConnectionPool(**kwargs)
        else:
            raise Exception("redis 初始化参数不能为空")
        self.client = redis.Redis(connection_pool=self.pool, socket_timeout=1.0, socket_connect_timeout=1.0)




