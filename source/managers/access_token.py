import datetime
import abc
import json

import wrappers.redis
from managers.http import HTTPManager


class AccessTokenManager():
    def __init__(self, RedisWrapper, key, AccessToken=None, expire=True):
        self.redis_wrapper = RedisWrapper
        self.key = key
        self.access_token = AccessToken
        self.expire = expire
        
    def refresh(self):
        logger.debug("Refreshing OAuth token")
        new_token = self.token.refresh()
        self.save(new_token)
        self.token = new_token

    @classmethod
    def load(self):
        value = redis_wrapper.get_value(self.key)

        if value is None:
            return None

    def save(self):
        if self.expire:
            expire_in = self.token.expires_in.total_seconds() * self.access_token.token_refresh_threshold

            self.redis.setex(self.key, int(expire_in), json.dumps(token()))
        else:
            self.redis.set(self.redis_key, json.dumps(token.json()))


class AppAccessTokenManager(AccessTokenManager):
    def __init__(self, RedisWrapper, ClientAuth, AccessToken):
        key = f"authentication:app-access-token:{ClientAuth.client_id}:{json.dumps(AccessToken.scope)}"

        super().__init__(RedisWrapper, key, AccessToken)


class UserAccessTokenManager(AccessTokenManager):
    def __init__(self, RedisWrapper, username, user_id, AccessToken):
        key = f"authentication:user-access-token:{user_id}"

        super().__init__(RedisWrapper, key, AccessToken)
        self.username = username
        self.user_id = user_id


class AccessToken():
    def __init__(self, access_token, created_at, expires_in, token_type, refresh_token, scope):
        self.access_token = access_token
        self.created_at = created_at
        self.expires_in = expires_in
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.scope = scope

        self.token_refresh_threshold = 0.9
        self.expires_at = None
        
        if expires_in is not None:
            self.expires_at = self.created_at + datetime.timedelta(seconds=self.expires_in)
        else:
            self.expires_at = None

    @abc.abstractmethod
    def can_refresh(self):
        pass

    def should_refresh(self):
        if not self.can_refresh():
            return False

        if self.expires_at is not None:
            expires_after = self.expires_at - self.created_at
        else:
            expires_after = datetime.timedelta(hours=1)

        token_age = datetime.datetime.utcnow() - self.created_at

        max_token_age = expires_after * self.token_refresh_threshold

        return token_age >= max_token_age

    def json(self):
        if self.expires_in is None:
            expires_in_ms = None
        else:
            expires_in_ms = self.expires_in * 1000

        return {
            "access_token": self.access_token,
            "created_at": self.created_at.timestamp() * 1000,
            "expires_in": expires_in_ms,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
            "scope": self.scope
        }


class UserAccessToken(AccessToken):
    @classmethod
    @staticmethod
    def init(cls, access_token):
        return cls(
            access_token=access_token,
            created_at=None,
            expires_in=None,
            token_type="bearer",
            refresh_token=None,
            scope=[]
        )

    def can_refresh(self):
        return self.refresh_token is not None

    def refresh(self, ClientAuth, refresh_token):
        if not UserAccessToken.can_refresh():
            raise ValueError("This user access token has no refresh token")

        response = HTTPManager.post(
            self.url,
            "/oauth2/token",
            {
                "client_id": self.ClientAuth.client_id,
                "client_secret": self.ClientAuth.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )

        return AccessToken(
            token=response["token"],
            created_at=datetime.datetime.utcnow(),
            expires_in=self.expires_in(response),
            token_type=response["token_type"],
            refresh_token=response.get("refresh_token", None),
            scope=response.get("scope", [])
        )

    def __init__(self, url, ClientAuth):
        value = HTTPManager.request(
            method="GET",
            url=url + "/oauth2/authorize",
            params={
                "client_id": ClientAuth.client_id,
                "client_secret": ClientAuth.client_secret,
                "response_type": "token",
                "redirect_uri": ClientAuth.redirect_uri
            }
        )

        print(value)

        return super().__init__(
            access_token=value.get("access_token"),
            created_at=datetime.datetime.utcnow(),
            expires_in=value.get("expires_in"),
            token_type=value.get("token_type"),
            refresh_token=value.get("refresh_token"),
            scope=value.get("scope", [])
        )


class AppAccessToken(AccessToken):
    def can_refresh(self):
        return True

    def refresh(self):
        return self.get(self.scope)

    def __init__(self, url, ClientAuth, scope=[]):
        value = HTTPManager.request(
            method="POST",
            url=url + "/oauth2/token",
            params={
                "client_id": ClientAuth.client_id,
                "client_secret": ClientAuth.client_secret,
                "grant_type": "client_credentials",
                "scope": (" ".join(scope))
            }
        ).json()

        super().__init__(
            access_token=value.get("access_token"),
            created_at=datetime.datetime.utcnow(),
            expires_in=value.get("expires_in"),
            token_type=value.get("token_type"),
            refresh_token=value.get("refresh_token"),
            scope=value.get("scope")
        )