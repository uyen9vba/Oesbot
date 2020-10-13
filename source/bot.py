import cgi
import datetime
import re
import sys
import urllib
import random
import abc

from managers.database import DatabaseManager
from managers.irc_ import IRCManager
from managers.command import CommandManager
from managers.phrase import PhraseManager
from managers.access_token import AppAccessToken, AppAccessTokenManager, UserAccessTokenManager, UserAccessToken
from managers.scheduler import Scheduler, BackgroundScheduler
from wrappers.helix import HelixWrapper
from wrappers.redis import RedisWrapper
from utilities.client_auth import ClientAuth
from utilities.logger import *
from utilities.tmi import *


class Bot:
    def __init__(self, config, args):
        self.args = args
        self.config = config["config"]
        self.phrases = config["phrases"]
        self.twitch = config["twitch"]
        self.api = config["api"]

        self.client_auth = ClientAuth(
            client_id=self.twitch.get("client_id"),
            client_secret=self.twitch.get("client_secret"),
            redirect_uri=self.twitch.get("redirect_uri")
        )

        if self.config.getboolean("verified", False):
            self.tmi_status = TMIStatus.verified
        elif self.config.getboolean("known", False):
            self.tmi_status = TMIStatus.known
        else:
            self.tmi_status = TMIStatus.moderator

        self.database_manager = DatabaseManager(url=self.api.get("database"))
        self.redis_wrapper = RedisWrapper()

        self.app_access_token = AppAccessToken(
            url=self.api.get("twitch"),
            ClientAuth=self.client_auth
        )

        self.app_access_token_manager = AppAccessTokenManager(
            RedisWrapper=self.redis_wrapper,
            ClientAuth=self.client_auth,
            AccessToken=self.app_access_token
        )

        self.helix_wrapper = HelixWrapper(
            url=self.api.get("helix"),
            config=self.config,
            RedisWrapper=self.redis_wrapper,
            ClientAuth=self.client_auth,
            AccessTokenManager=self.app_access_token_manager
        )

        self.bot_userdata = self.helix_wrapper.get_userdata_by_login(self.config.get("name"))
        self.channel_userdata = self.helix_wrapper.get_userdata_by_login(self.config.get("channel"))

        """
        self.bot_access_token_manager = UserAccessTokenManager(
            RedisWrapper=self.redis_wrapper,
            username=self.config.get("name"),
            user_id=self.bot_userdata["data"][0]["id"],
            AccessToken=UserAccessToken(
                url=self.api.get("twitch"),
                ClientAuth=self.client_auth
            )
        )
        """

        print(self.client_auth.client_secret)

        print(self.bot_userdata)

        self.irc_manager = IRCManager(self)
        self.command_manager = CommandManager(self.database_manager)
        self.phrase_manager = PhraseManager(self.database_manager)

        if self.channel_userdata["data"][0]["id"] is None:
            raise ValueError("Config: channel name not found on https://api.twitch.tv/helix")
        
        if self.bot_userdata["data"][0]["id"] is None:
            raise ValueError("Config: bot name not found on https://api.twitch.tv/helix")

        if args.build:
            print("Build mode: shutting down in 30...")
            self.quit()
            Scheduler.execute_delayed(delay=30, method=lambda: self.quit())
            
    def password(self):
        return f"oauth:{self.bot_access_token_manager.access_token.access_token}"

    def parse_message(self, message, source, event, tags={}, whisper=False):
        message = message.lower()

        # if not whisper and event.target ==
        #

    def quit(self, **options):
        self.commit()

        try:
            BackgroundScheduler.scheduler.print_jobs()
            BackgroundScheduler.scheduler.shutdown(wait=False)
        except a:
            logger.exception("Error while shutting down APScheduler")

        try:
            for a in self.phrases["quit"]:
                self.irc_manager.message(self.channel, a)
        except:
            logger.exception("Exception caught while trying to message quit phrase")
            
        sys.exit(0)

    def commit(self):
        for key, a in self.command_manager.commands:
            a.commit()

        for key, a in self.phrase_manager.phrases:
            a.commit()

    def start(self):
        self.irc_manager.create_connection()
        self.irc_manager.reactor.process_forever()