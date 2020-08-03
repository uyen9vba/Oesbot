import cgi
import datetime
import logging
import re
import sys
import urllib
import random

import irc.client
import requests

import src.managers.scheduler import ScheduleManager
import src.managers.database import DatabaseManager
import src.managers.tmi_constraints import TMIConstraints
import src.bot import Bot

class Salbot(Bot):
    """
    config = None
    args = None
    nickname = None
    tmi_constraints = None
    phrases = None
    channel = None
    streamer = None 
    web_domain = None
    """

    def init(self):
        self.phrases = self.config["phrases"]

        ScheduleManager.init()

        DatabaseManager.init(self.config["config"]["database"])

        self.nickname = self.config["config"].get("nickname", "salbot")

        if self.config["config"].getBoolean("verified", False):
            self.tmi_constraints = TMIConstraints.verified
        elif self.config["config"].getBoolean("known", False):
            self.tmi_constraints = TMIConstraints.known
        else:
            self.tmi_constraints = TMIConstraints.moderator