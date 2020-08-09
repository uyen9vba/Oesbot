import cgi
import datetime
import logging
import re
import sys
import urllib
import random

import irc.client
import requests

import src.managers.schedule import ScheduleManager
import src.managers.database import DatabaseManager
import src.managers.tmi_status import TMIConstraints
import src.bot import Bot

class Salbot(Bot):
    """
    config = None
    args = None
    name = None
    tmi_status = None
    phrases = None
    channel = None
    streamer = None 
    web_domain = None
    """

    def init(self):
        self.phrases = self.config["phrases"]
        self.name = self.config["config"].get("name", "salbot")

        ScheduleManager.init()

        DatabaseManager.init(self.config["config"]["database"])

        #TMI Constraints
        if self.config["config"].getBoolean("verified", False):
            self.tmi_status = TMIStatus.verified
        elif self.config["config"].getBoolean("known", False):
            self.tmi_status = TMIStatus.known
        else:
            self.tmi_status = TMIStatus.moderator

        