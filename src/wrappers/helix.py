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

    def get_userdata_by_auth(self, ClientAuth):
        return self.redis.cache(
            redis_key=f"api:twitch:helix:user:by-auth:{ClientAuth}",
            method=lambda: HTTPManager.get("/users", self.url, authorization=ClientAuth),
            expiry=lambda response: 30 if response None else 300
        )

    def get_userdatas_by_id(self, user_ids):
        return self.redis.cache_batch(
            user_ids,
            redis_method=lambda user_id: f"api:twitch:helix:user:by-id:{user_id}",
            method=lambda user_ids: self.get_userdatas("id", user_ids),
            expiry=lambda response: 30 if response is None else 300
        )

    def get_userdatas_by_login(self, logins):
        return self.redis.cache_batch(
            logins,
            redis_method=lambda login: f"api:twitch:helix:user:by-login:{login}",
            method=lambda logins: self.get_userdatas("login", logins),
            expiry=lambda response: 30 if response is None else 300
        )

    def get_userdatas(self, key_type, keys):
        userdatas = []
        # HelixAPI constrains request to 100 users
        for key_batch in (seq[a : a + 100] for a in range(0, len(seq), 100)):
            response = HTTPManager.get("/users", self.url, {key_type: key_batch}).json()

            response_map = {entry[key_type]: entry for entry in response["data"]}

            for key in key_batch:
                userdatas.append(response_map.get(key, None))

        return userdatas

    def get_user_id(self, login):
        userdata = self.get_userdata_by_login(login)

        return userdata["id"]

    def get_users(self, login):
        response = HTTPManager.get(self.url, ["group", "user", login, "chatters"])

        users = []

        for category in response["chatters"].values():
            users.extend(category)

        return users

    def get_follow_since(self, from_id, to_id):
        return self.redis.cache(
            redis_key=f"api:twitch:helix:follow-since:{from_id}:{to_id}",
            method=lambda: HTTPManager.get("/users/follows", self.url, {"from_id": from_id, "to_id": to_id})
            expiry=lambda response: 30 if response is None else 300
        )

    def get_profile_image_url(self, user_id):
        userdata = self.get_userdata_by_id(user_id)

        return userdata["profile_image_url"]

    def get_subscribers_page(self, broadcaster_id, auth, page_cursor=None):
        response = HTTPManager.get(
            "/subscribers",
            {"broadcaster_id": broadcaster_id, **self.page(page_cursor)},
            authorization=auth
        )

        subscribers = [a["user_id"] for a in response["data"]]
        page_cursor = response["page"]["cursor"]

        return subscribers, page_cursor

    def get_subscribers(self, broadcaster_id, auth):
        return self.get_pages(self.get_subscribers_page, broadcaster_id, auth)

    @staticmethod
    def page(page_cursor=None):
        if (page_cursor is None):
            return {}
        else:
            return {"after": page_cursor}

    @staticmethod
    def get_pages(method, *args,  **kwargs):
        page_cursor = None
        responses = []

        while True:
            response, page_cursor = method(page_cursor=page_cursor, *args, **kwargs)
            responses.extend(response)

            if len(response) <= 0:
                break

        return responses

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
            return HTTPManager.request(method, self.url, endpoint, params, headers, json)
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