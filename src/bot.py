import cgi
import datetime
import logging
import re
import sys
import urllib
import random
import abc

import irc.client
import requests

import src.managers.scheduler import ScheduleManager
import src.managers.database import DatabaseManager

class Bot:
    @abstractmethod
    def __init__(self, config, args):
        pass

    @property
    def password(self):
        return f"oauth:{self.token_manager.token.access_token}"