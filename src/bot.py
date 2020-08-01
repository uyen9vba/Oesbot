import cgi
import datetime
import logging
import re
import sys
import urllib
import random

import irc.client
import requests

import managers.scheduler import ScheduleManager

class Bot:
    def __init__(self, config, args):
        self.config = config
        self.args = args

        ScheduleManager.init()

