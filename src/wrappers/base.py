import logging
import datetime

from urllib.parse import quote, urlparse, urlunparse
from requests import Session

from src.wrappers.cache import Cache

logger = logging.getLogger(__name__)

class BaseAPI:
    def __init__(self, url, redis=None):
        self.url = url
        self.session = Session()
        self.timeout = 20
    
    @staticmethod
    def check_url_scheme(url, default_scheme="https"):
        return urlunparse(urlparse(url, scheme=default_scheme))

    @staticmethod
    def 