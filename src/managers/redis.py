import json
import logging

import redis

from src.managers.emote import EmoteManager

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self, **options):
        self.redis = redis.Redis(**{"decode_responses": True, **options})

    def cache(self, key, function, serializer=JSONSerializer(), expiry=120, force=False):
        if not force:
            cache = self.redis.get(key)
            if cache is not None:
                return serializer.deserialize(cache)

        logger.debug("Cache Miss: %s", key)

        if callable(expiry):
            expiry = expiry(function())

        if expiry > 0:
            self.redis.setex(key, expiry, serializer.serialize(function()))
        
        return function()

    @property
    def redis(self):
        return self.redis

    @staticmethod
    def pipeline(self):
        return redis.utils.pipeline(self.redis())

    @classmethod
    def publish(cls, channel, message):
        cls.redis.publish(channel, message)