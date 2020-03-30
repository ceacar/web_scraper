import sys
from typing import TypeVar
import errors
from flask import current_app as app
from werkzeug.contrib.cache import SimpleCache
import time
import redis

T = TypeVar('T')

class Cacher:
    """
    use a cacher to cache key value pair store
    """


    def __init__(self):
        self.conn = redis.StrictRedis(
            host = app.config["REDIS_URL"],
            port = app.config["REDIS_PORT"])
        cache = SimpleCache()
        self.internal_cache = cache
        self.time_out = int(app.config["TTL_TIMEOUT"])

    def cache_item(self, key, value):
        #TTL for cache
        self.internal_cache.set(key, value, timeout = self.time_out)

    def save(self, key: str, value: T):
        #save to redis
        try:
            self.conn.set(key, value)
        except Exception as e:
            print("saved to redis failed")
            print(e)
            return

        #save value with epoch time for ttl in cache
        self.cache_item(key, value)

    def retrieve_value_from_redis(self, key: str) -> T:
        try:
            res_byte = self.conn.get(key)
            res = res_byte.decode()
            return res

        except Exception as e:
            print(e)
            print("redis get failed")
            return None

    def get(self, key: str) -> T:
        value = self.internal_cache.get(key)

        if value:
            return value
        else:
            value = self.retrieve_value_from_redis(key)
            self.cache_item(key, value)
            return value

__cacher = None

def get_cacher():
    #singleton
    global __cacher

    if not __cacher:
        __cacher = Cacher()

    return __cacher
