import time
import datetime
import math
import io
import urllib

import requests

from managers.http import HTTPManager
from wrappers.redis import RedisWrapper
import managers.access_token
import utilities.logger


class HelixWrapper:
    def __init__(self, url, config, RedisWrapper=None, ClientAuth=None):
        self.url = url
        self.config = config
        self.redis_wrapper = RedisWrapper
        self.client_auth = ClientAuth

    def get_userdata_by_login(self, login):
        key = f"api:twitch:helix:user:by-login:{login}"
        value = self.redis_wrapper.get_value(key)

        if value is None:
            value = HTTPManager.request(
                method="GET",
                url=self.url + "/users",
                params={"login": login},
                headers={"Client-ID": self.client_auth.client_id}
            ).json()
            #value = HTTPManager.get(self.url, "/users", {"login": login}).json()
            self.redis_wrapper.cache(key=key, value=value, expiry=30)

        return value

    def get_userdata_by_id(self, id_):
        key = f"api:twitch:helix:user:by-id:{id_}"
        value = self.redis_wrapper.get_value(key)

        if value is None:
            value = self.session.request(
                method="GET",
                url=self.url + "/users",
                params={"id": id_}
            ).json()
            #value = HTTPManager.get("/users", self.url, {"id": id_}).json()
            self.redis_wrapper.cache(key=key, value=value, expiry=30)

        return value

    def get_userdatas_by_login(self, logins):
        keys = []

        for a in logins:
            keys.append(f"api:twitch:helix:user:by-login:{a}")

        values = self.redis_wrapper.get_values(keys)

        for a, b in values:
            if b is None:
                value = HTTPManager.get(self.url, "/users", {"login": logins[a]}).json()
                self.redis_wrapper.cache(key=keys[a], value=value, expiry=30)
                
                values.insert(a, value)

        return values

    def get_userdatas_by_id(self, ids):
        keys = []

        for a in ids:
            keys.append(f"api:twitch:helix:user:by-id:{a}")

        values = self.redis_wrapper.get_values(keys)

        for a, b in values:
            if b is None:
                value = HTTPManager.get("/users", self.url, {"id": ids[a]}).json()
                self.redis_wrapper.cache(key=keys[a], value=value, expiry=30)

                values.insert(a, value)

        return values

    def get_userdatas(self, key_type, keys):
        userdatas = []
        # HelixAPI constrains request to 100 users
        for key_batch in (seq[a : a + 100] for a in range(0, len(seq), 100)):
            response = HTTPManager.get("/users", self.url, {key_type: key_batch}).json()

            response_map = {entry[key_type]: entry for entry in response["data"]}

            for key in key_batch:
                userdatas.append(response_map.get(key, None))

        return userdatas

    def get_users(self, login):
        response = HTTPManager.get(self.url, ["group", "user", login, "chatters"])

        users = []

        for category in response["chatters"].values():
            users.extend(category)

        return users

    def get_follow_since(self, from_id, to_id):
        key = f"api:twitch:helix:follow-since:{from_id}:{to_id}"
        value = self.redis_wrapper.get_value(key)

        if value is None:
            value = HTTPManager.get("/users/follows", self.url, {"from_id": from_id, "to_id": to_id})
            self.redis_wrapper.cache(key=key, value=value, expiry=30)

        return value

    def get_profile_image(self, login, id_):
        userdata = self.get_userdata_by_id(id_)
        path = f"static/images/logo_{login}.png"

        tn_path = f"static/images/logo_{login}_tn.png"
        bytes = HTTPManager.get(userdata["profile_image_url"]).content

        with open(path, "wb") as file:
            file.write(bytes)

        read_stream = io.BytesIO(bytes)
        #

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
