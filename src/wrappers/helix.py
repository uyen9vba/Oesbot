import logging
import time
import datetime
import math
import requests
import urllib

from src.managers.http import HTTPManager
from src.wrappers.redis import Redis
from src.utils.client_auth import ClientAuth
from src.utils.access_token import AccessToken, UserAccessToken, AppAccessToken

logger = logging.getLogger(__name__)

class Helix:
    def __init__(self, redis=Redis, client_auth=ClientAuth):
        self.url = "https://api.twitch.tv/helix"
        self.redis = redis
        self.client_auth = client_auth
        self.timeout = 20

    def userdata(self, key_type, keys):
        userdatas = []
        # HelixAPI constrains request to 100 users
        for key_batch in (seq[a : a + 100] for a in range(0, len(seq), 100)):
            response = HTTPManager.get("/users", self.url, {key_type: key_batch}).json()

            response_map = {entry[key_type]: entry for entry in response["data"]}

            for key in key_batch:
                userdatas.append(response_map.get(key, None))

        return userdatas

    def userdata_by_login(self, login):
        response = HTTPManager.get("/users", self.url, {"login": login}).json()

        if len(response["data"]) <= 0:
            return None

        return response["data"][0]

    def userdata_by_id(self, login):
        response = HTTPManager.get("/users", self.url, {"id": user_id}).json()

        if len(response["data"]) <= 0:
            return None

        return response["data"][0]

    def users(self, login):
        response = HTTPManager.get(self.url, ["group", "user", login, "chatters"])

        users = []

        for category in response["chatters"].values():
            users.extend(category)

        return users

    def request(self, method, endpoint, params, headers, auth=None, json=None):
        if isinstance(auth, ClientAuth):
            auth_headers = {"Client-ID": auth.client_id}
        elif isinstance(auth, AccessTokenManager):
            auth_headers = {
                "Client-ID": auth.client_id,
                "Authrorization": f"{"Bearer"} {auth.access_token}"
            }
        elif isinstance(auth, tuple):
            (client_auth, AccessToken) = auth

            auth_headers = {
                "Client"
            }