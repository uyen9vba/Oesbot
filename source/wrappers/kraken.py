import wrappers.redis
import managers.http


class KrakenWrapper:
    def __init__(self, ClientAuth):
        self.url = "https://api.twitch.tv/kraken"
        self.auth = ClientAuth

    def get_global_emotes(self, force=False):
        key = "api:twitch:kraken:v5:global-emotes"
        value = RedisWrapper.get_value(key)

        if value is None or force:
            value = HTTPManager.get(self.url, "/chat/emoticon_images").json()
            RedisWrapper.cache(key=key, value=value, expiry=60 * 60)

        return value

    def get_channel_emotes(self, login, id_, force=False):
        key = f"api:twitch_emotes:channel-emotes:{login}"
        value = RedisWrapper.get_value(["channels", id_])

        if value is None or force:
            value = HTTPManager.get(url="https://api.twitchemotes.com/api/v5", endpoint="/channels", headers={"id": id_}).json.loads()
            RedisWrapper.cache(key=key, value=value, expiry=60 * 60)

        return value