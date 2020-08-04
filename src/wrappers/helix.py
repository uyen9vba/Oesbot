import logging
import time
import datetime
import math
import requests
import urllib

from src.managers.http import HTTPManager
from src.wrappers.redis import Redis
from src.utils.authorization import Authorization

logger = logging.getLogger(__name__)

class Helix:
    def __init__(self, redis=Redis, authorization=Authorization):
        self.url = "https://api.twitch.tv/helix"
        self.redis = redis
        self.authorization = authorization
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

    def userdata_by

    def app_access_token(self, scope=[]):
        response = HTTPManager.post("/oauth2/token",
            {
                "client_id": self.authorization.client_id
                "client_secret": self.authorization.client_secret,
                "grant_type": "client_credentials",
                "scope": (" ".join(scope))
            }
        )

        return 

    def user_access_token(self, code):
        response = HTTPManager.post("/oauth2/token"
            {
                "client_id": self.authorization.client_id
                "client_secret": self.authorization.client_secret,
                "code": code,
                "redirect_uri": self.authorization.redirect_url
                "grant_type": "authorization_code"
            }
        )

