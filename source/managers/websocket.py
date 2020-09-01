import json
import threading
import pathlib
import importlib

from bot import Bot

from static.static import logger

class WebSocketServer:
    def __init__(self, WebSocketManager, port, ssl, key_path=None, crt_path=None, unix_socket_path=None):
        self.websocket_manager = WebSocketManager

class WebSocketManager:
    def __init__(self):
        self.clients = []

        if "websocket" not in Bot.config:
            logger.debug("Websocket not found in config")
            
            return

        if Bot.config["websocket"] == "1":
            ssl = bool(config.get("ssl", "0") == "1")
            port = int(config.get("port", "443" if ssl else "80"))
            key_path = config.get("key_path", "")
            crt_path = config.get("crt_path", "")
            unix_socket_path = config.get("unix_socket_path", None)

        if ssl:
            if (key_path or crt_path) == "":
                logger.error("SSL enabled in config, but missing key_path or crt_path")

        self.websocketserver = WebSocketServer(self, port, ssl, key_path, crt_path, unix_socket_path)