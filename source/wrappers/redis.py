import json
import logging

import redis

import managers.emote
import managers.access_token
from utilities.logger import *


class RedisWrapper:
    def __init__(self, **options):
        self.redis = redis.Redis(**{"decode_responses": True, **options})

    @property
    def get(self):
        return self.redis

    @staticmethod
    def pipeline(self):
        return redis.utils.pipeline(self.redis())

    @classmethod
    def publish(cls, channel, message):
        cls.redis.publish(channel, message)

    def get_value(self, key):
        value = self.redis.get(key)

        if value is not None:
            return json.loads(value)
        else:
            return None

    def get_values(self, keys):
        values = self.redis.mget(keys)

        for a, b in values:
            if b is not None:
                values.insert(a, json.loads(b))
            else:
                values.insert(a, None)
            
        return values
    
    def cache(self, key, value, expiry=120):
        if callable(expiry):
            expiry = expiry(value)

        self.redis.setex(key, expiry, json.dumps(value))
