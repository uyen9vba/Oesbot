import requests

import wrappers.redis
import managers.http


class BTTVWrapper:
    def __init__(self):
        self.url = "https://api.betterttv.net/3"

    def get_global_emotes(self, force=False):
        key = "api:bttv:global-emotes"
        value = RedisWrapper.get_value(key)

        if value is None or force:
            value = HTTPManager.request(
                method="GET",
                url=self.url + "/cached/emotes/global"
            ).json()
            RedisWrapper.cache(key=key, value=value, expiry=60 * 60)

        return value

    def get_channel_emotes(self, login, force=False):
        key = f"api:ffz:channel-emotes:{login}"
        value = RedisWrapper.get_value(key)

        if value is None or force:
            try:
                value = HTTPManager.request(
                    method="GET",
                    url=self.url,
                    params=["cached", "users", "twitch", login]
                ).json()
            except requests.HTTPError as a:
                if a.response.status_code == 404:
                    return []
                else:
                    raise a

            RedisWrapper.cache(key=key, value=value, expiry=60 * 60)

        return value
