import logging
import time
import datetime
import math
import requests
import urllib

from requests import HTTPError

from src.managers.http import HTTPManager
from src.wrappers.redis import RedisManager
from src.utils.client_auth import ClientAuth
from src.utils.access_token import AccessToken, UserAccessToken, AppAccessToken

logger = logging.getLogger(__name__)

class HelixManager:
    def __init__(self, RedisManager, ClientAuth, AccessTokenManager):
        self.url = "https://api.twitch.tv/helix"
        self.redis = RedisManager
        self.auth = ClientAuth
        self.token_manager = AccessTokenManager

    def get_userdata(self, key_type, keys):
        userdatas = []
        # HelixAPI constrains request to 100 users
        for key_batch in (seq[a : a + 100] for a in range(0, len(seq), 100)):
            response = HTTPManager.get("/users", self.url, {key_type: key_batch}).json()

            response_map = {entry[key_type]: entry for entry in response["data"]}

            for key in key_batch:
                userdatas.append(response_map.get(key, None))

        return userdatas

    def get_userdata_by_login(self, login):
        return self.redis.cache(
            redis_key=f"api:twitch:helix:user:by-login:{login}",
            method=lambda: HTTPManager.get("/users", self.url, {"login": login}).json(),
            expiry=lambda response: 30 if response None else 300
        )

    def get_userdata_by_id(self, user_id):
        return self.redis.cache(
            redis_key=f"api:twitch:helix:user:by-id:{user_id}",
            method=lambda: HTTPManager.get("/users", self.url, {"id": user_id}).json(),
            expiry=lambda response: 30 if response None else 300
        )

    def get_userdata_by_auth(self, auth):
        return self.redis.cache(
            redis_key=f"api:twitch:helix:user:by-auth:{auth}",
            method=lambda: HTTPManager.get("/users", self.url, auth=auth),
            expiry=lambda response: 30 if response None else 300
        )

    def get_users(self, login):
        response = HTTPManager.get(self.url, ["group", "user", login, "chatters"])

        users = []

        for category in response["chatters"].values():
            users.extend(category)

        return users

    def request(self, method, endpoint, params, headers, auth=None, json=None):
        if isinstance(auth, ClientAuth):
            auth_headers = {"Client-ID": auth.client_id}
        else:
            auth_headers = {}

        if headers is None:
            headers = auth_headers
        else:
            headers = {**headers, **auth_headers}

        try:
            HTTPManager.request(method, self.url, endpoint, params, headers, json)
        except HTTPError as a:
            if (a.response_status_code == 401 and "WWW-Authenticate" in a.response_headers):
                return HTTPManager.request(method, self.url, endpoint, params, headers, json)
            elif a.response_status_code == 429:
                rate_limit_reset = datetime.datetime.fromtimestamp(int(a.response_headers["Ratelimit-Reset"]), tz.timezone.utc)
                time_to_wait = rate_limit_reset - datetime.datetime.utcnow()

                time.sleep(math.ceil(time_to_wait.total_seconds()))
                return HTTPManager.request(method, self.url, endpoint, params, headers, auth, json)
            else:
                raise a