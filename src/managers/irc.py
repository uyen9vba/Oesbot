import logging
import socket
import ssl

import irc
import ratelimiter

from src.bot import Bot
from src.managers.scheduler import Scheduler, BackgroundScheduler

logger = logging.getLogger("salbot")

class IRCManager:
    def __init__(self, reactor, channel, host_channel):
        self.reactor = reactor
        self.channels = ["#" + channel]
        self.host_channel = "#" + host_channel
        self.connection = ServerConnection(self.reactor)
        self.ping_task = None
        self.message_count = 0
        self.whispers_per_minute = 0
        self.whispers_per_second = 0

        reactor.add_global_handler("welcome", self.on_welcome)
        reactor.add_global_handler("all_event", self.on_dispatch, -10)
        reactor.add_global_handler("disconnect", self.on_disconnect)

    @ratelimiter.RateLimiter(max_calls=1, period=2)
    def init(self):
        if self.connection is not None or self.ping_task is not None:
            raise AssertionError("Connection still active")

        try:
            self.create_connection()

            phrases = {"name": Bot.name, "version": Bot.version}

            for a in Bot.phrases["welcome"]:
                self.message(a.format({"name": Bot.name, "version": Bot.version}))

            return True
        except:
            logger.exception("Failed to open connection. Retrying")
            self.connection = None

            Scheduler.execute_delayed(2, lambda: self.init())
            
            return False

    def message(self, channel, message, whisper=False):
        if  self.ping_task is None or not self.can_send():
            logger.error("TMI rate limit was reached. Retrying")
            Scheduler.execute_delayed(2, self.message, channel, message)
             return 

        self.connection.privmsg(channel, message)
        self.message_count += 1

        Scheduler.execute_delayed(31, lambda: message_count -= 1)

        if whisper:
            self.whispers_per_minute += 1
            self.whispers_per_second += 1

            Scheduler.execute_delayed(1, lambda: message_count -= 1)
            Scheduler.execute_delayed(61, lambda: message_count -= 1)

    def whisper(self, name, message):
        self.message(f"#{Bot.name}", f"/w {name} {message}", whisper=True)

    def create_connection(self):
        ssl_factory = ssl.Factory(wrapper=ssl.wrap_socket)

        with self.reactor.mutex:
            self.reactor.connections.append(self.connection)

        self.connection.connect(
            "irc.chat.twitch.tv",
            6697,
            Bot.nickname,
            Bot.password,
            Bot.nickname,
            connect_factory=ssl_factory
        )
        self.connection.cap("REQ", "twitch.tv/commands", "twitch.tv/tags")

        self.ping_task = BackgroundScheduler.execute_interval(30, lambda: Scheduler.execute(self.ping))

    def ping(self):
        if self.connection is not None:
            self.connection.ping("tmi.twitch.tv")

    def can_send(self, whisper=False):
        if whisper:
            return (
                self.message_count < Bot.tmi_status.messages_per_30seconds and
                self.whispers_per_second < Bot.tmi_status.whispers_per_second and
                self.whispers_per_minute < Bot.tmi_status.whispers_per_minute
            )

    def on_welcome(self, ServerConnection, event):
        logger.info("Successfully connected IRC")
        ServerConnection.join(",".join(self.channels))

    def on_dispatch(self, ServerConnection, event):
        method = getattr(Bot, "on_" + event.type, None)

        if method is not None:
            try:
                method(ServerConnection, event)
            except:
                logger.exception("Uncaught exception (IRC event handler)")

    def on_disconnect(self, ServerConnection, event):
        logger.error(f"Disconnected from IRC ({event.arguments[0]})")
        self.connection = None

        self.ping_task.remove()
        self.ping_task = None

        self.init()

class ServerConnection(irc.client.ServerConnection):
    def __init__(self, reactor):
        self.reactor = reactor
        self.in_channel = False

    def send(self, string):
        if "\n" in string or "\r" in string:
            raise irc.client.InvalidCharacters("CR/LF not allowed in IRC commands")
        
        bytes = string.encode("utf-8") + b"\r\n"

        if len(bytes) > 2048:
            raise irc.client.MessageTooLong("Messages limited to 2048 bytes including CR/LF")

        if self.socket is None:
            raise irc.client.ServerNotConnectedError("Not connected")
        
        sender = getattr(self.socket, "write", self.socket.send)

        try:
            sender(bytes)
        except socket.error:
            self.disconnect("Connection reset by peer")