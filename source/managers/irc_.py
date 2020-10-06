import socket
import ssl

import irc.client
import ratelimiter
import tempora.schedule

from utilities.logger import *
from managers.scheduler import Scheduler, BackgroundScheduler


class IRCManager:
    def __init__(self, Bot):
        self.bot = Bot
        self.reactor = irc.client.Reactor()
        self.channels = ["#" + self.bot.config.get("channel")]
        self.host_channel = "#" + self.bot.config.get("host_channel")
        self.server_connection = None
        self.ping_task = None
        self.message_count = 0
        self.whispers_per_minute = 0
        self.whispers_per_second = 0

        self.reactor.add_global_handler(event="welcome", handler=self.on_welcome)
        self.reactor.add_global_handler(event="all_event", handler=self.on_dispatch, priority=-10)
        self.reactor.add_global_handler(event="disconnect", handler=self.on_disconnect)

    def message(self, channel, message, whisper=False):
        if self.ping_task is None and not self.can_send():
            logger.error("TMI rate limit was reached. Retrying")
            Scheduler.execute_delayed(
                delay=2,
                method=lambda: self.message(channel, message, whisper)
            )

            return

        self.server_connection.privmsg(channel, message)
        self.message_count += 1

        Scheduler.execute_delayed(31, lambda: self.message_count.__setattr__(self.message_count - 1))

        if whisper:
            self.whispers_per_minute += 1
            Scheduler.execute_delayed(61, lambda: self.whispers_per_minute.__setattr__(self.whispers_per_minute - 1))

            self.whispers_per_second += 1
            Scheduler.execute_delayed(1, lambda: self.whispers_per_second.__setattr__(self.whispers_per_second - 1))

    def whisper(self, name, message):
        self.message(f"#{self.bot.name}", f"/w {name} {message}", whisper=True)

    @ratelimiter.RateLimiter(max_calls=1, period=2)
    def create_connection(self):
        if self.server_connection is not None or self.ping_task is not None:
            raise AssertionError("create_connection() should not be called while a connection is active")

        try:
            self.server_connection = irc.client.ServerConnection(self.reactor)

            with self.reactor.mutex:
                self.reactor.connections.append(self.server_connection)

            self.server_connection.connect(
                server="irc.chat.twitch.tv",
                port=6697,
                nickname=self.bot.config.get("name"),
                password="oauth:e7t4ngyv3wlyftay1yaovo9xzgmh80",
                username=self.bot.config.get("name"),
                connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket)
            )
            self.server_connection.cap("REQ", "twitch.tv/commands", "twitch.tv/tags")

            self.ping_task = BackgroundScheduler.execute_interval(
                interval=30,
                method=lambda: Scheduler.execute_delayed(delay=0, method=self.ping),
            )
        except:
            logger.exception("Failed to open connection. Retrying")
            self.server_connection = None
            
            Scheduler.execute_delayed(delay=2, method=self.create_connection())

    def ping(self):
        if self.server_connection is not None:
            self.server_connection.ping(target="tmi.twitch.tv")

    def can_send(self, whisper=False):
        if whisper:
            return (
                self.message_count < self.bot.tmi_status.messages_per_30seconds and
                self.whispers_per_second < self.bot.tmi_status.whispers_per_second and
                self.whispers_per_minute < self.bot.tmi_status.whispers_per_minute
            )

    def on_welcome(self, ServerConnection, event):
        logger.info("Successfully connected IRC")
        
        for a in self.channels:
            self.server_connection.join(a)
            self.message(a, self.bot.phrases.get("welcome"))

    def on_dispatch(self, ServerConnection, event):
        method = getattr(Bot, "on_" + event.type, None)

        if method is not None:
            try:
                method(ServerConnection, event)
            except:
                logger.exception("Uncaught exception (IRC event handler)")

    def on_disconnect(self, ServerConnection, event):
        logger.error(f"Disconnected from IRC ({event.arguments[0]})")

        for a in channels:
            self.message(a, self.bot.phrases.get("quit"))
            
        self.server_connection = None

        self.ping_task.remove()
        self.ping_task = None

        self.create_connection()


class ServerConnection(irc.client.ServerConnection):
    def __init__(self, reactor):
        super().__init__(reactor)

        self.in_channel = False
"""
    def send_raw(self, string):
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
"""