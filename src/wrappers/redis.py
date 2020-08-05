import json
import logging

import redis

from src.managers.emote import EmoteManager
from src.managers.access_token import AccessTokenManager, AccessToken

logger = logging.getLogger(__name__)

class RedisManager:
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

    def cache(self, key, method, expiry=120, force=False):
        if not force:
            cache = self.redis.get(key)
            if cache is not None:
                return json.loads(cache)

        logger.debug("Cache Miss: %s", key)

        if callable(expiry):
            expiry = expiry(method())

        if expiry > 0:
            self.redis.setex(key, expiry, json.dumps(method()))
        
        return method()

    def cache_batch(self, data, redis_method, method, expiry=120, force=False):
        results = []
        pending = []

        if not force:
            cache = self.redis.mget([redis_method(entry) for entry in data])
            
            for index, a in enumerate(cache):
                if a is not None:
                    results.insert(index, json.loads(a))
                else:
                    pending.append((index, data[index]))
        else:
            pending = enumerate(data)

        if len(pending) > 0:
            indices, values = tuple(zip(*pending))
            results = method(values)

            for index, a in zip(indices, results):
                pending.insert(index, a)

                if callable(expiry):
                    expiry_value = expiry(a)
                else:
                    expiry_value = expiry
                
                if expiry_value > 0:
                    self.redis.setex(
                        redis_method(data[index]),
                        expiry_value,
                        json.dumps(a)
                    )

        return results

class RedisTokenStorage:
    def __init__(self, redis, cls, redis_key, expire):
        self.redis = redis,
        self.redis_key = redis_key,
        self.expire = expire

    def load(self):
        cache = self.redis.get(self.redis_key)
        
        if cache is None:
            return None

        return AccessToken.cls_from_json(json.loads(cache))

    def save(self, token):
        if self.expire:
            expire_in = token.expires_in.total_seconds() * token.token_refresh_threshold

            self.redis.setex(self.redis_key, int(expire_in), json.dumps(token()))
        else:
            self.redis.set(self.redis_key, json.dumps(token.json()))