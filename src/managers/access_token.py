import datetime

from abc import abstractmethod

from src.wrappers.redis import RedisTokenStorage

class AccessTokenManager(ABC):
    def __init__(self, RedisTokenStorage=None, AccessToken=None):
        self.storage = RedisTokenStorage
        self.token = AccessToken

    def init(self):
        token = self.storage.load()

        if 

    def refresh(self):
        logger.debug("Refreshing OAuth token")
        new_token = self.token.refresh()
        self.save(new_token)
        self.token = new_token

class AccessToken(ABC):
    def __init__(self, access_token, created_at, expires_in, token_type, refresh_token, scope):
        self.access_token = access_token
        self.created_at = created_at
        self.expires_in = expires_in
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.scope = scope
        self.token_refresh_threshold
        
        if expires_in is not None:
            self.expires_at = self.created_at + self.expires_in
        else:
            self.expires_at = None

    @abstractmethod
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
            expires_in_ms = self.expires_in.total_seconds() * 1000

        return {
            "access_token": self.access_token,
            "created_at": self.created_at.timestamp() * 1000,
            "expires_in": expires_in_ms,
            "token_type": self.token_type
            "refresh_token": self.refresh_token,
            "scope": self.scope
        }

    @classmethod
    def cls_from_json(cls, json):
        if json["expires_in"] is None:
            expires_in = None
        else:
            expires_in = datetime.timedelta(milliseconds=json_data["expires_in"])

        return cls(
            access_token=json_data["access_token"],
            created_at=datetime.datetime.fromtimestamp(json["created_at"] / 1000, tz=datetime.timezone.utc)
            expires_in=expires_in,
            token_type=json["token_type"],
            refresh_token=json["refresh_token"],
            scope=json["scope"]
        )

    def expires_in(response):
        expires_in_s = response.get("expires_in", self.url, None)

        if expires_in_s is None:
            expires_in = None
        else:
            expires_in = datetime.timedelta(seconds=expires_in_s)

        return expires_in

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

    def refresh(self, refresh_token):
        if not UserAccessToken.can_refresh():
            raise ValueError("This user access token has no refresh token")

        response = HTTPManager.post(
            "/oauth2/token",
            self.url,
            {
                "client_id": self.client_auth.client_id,
                "client_secret": self.client_auth.client_secret,
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


    def get(self, url, code):
        response = HTTPManager.post(
            "/oauth2/token",
            url,
            {
                "client_id": self.client_auth.client_id
                "client_secret": self.client_auth.client_secret,
                "code": code,
                "redirect_uri": self.client_auth.redirect_url
                "grant_type": "authorization_code"
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


class AppAccessToken(AccessToken):
    def can_refresh(self):
        return True

    def refresh(self):
        return self.get(self.scope)

    def get(self, url, scope=[]):
        response = HTTPManager.post(
            "/oauth2/token",
            url,
            {
                "client_id": self.client_auth.client_id
                "client_secret": self.client_auth.client_secret,
                "grant_type": "client_credentials",
                "scope": (" ".join(scope))
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