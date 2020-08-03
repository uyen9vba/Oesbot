import logging
import time
import datetime
import math

from requests import HTTPError

logger = logging.getLogger(__name__)

class TwitchHelix:
    def __init__(self, url, redis, token_manager):
        self.url = "https://api.twitch.tv/helix"
        self.redis = redis
        self.token_manager = token_manager

    def