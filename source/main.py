import configparser
import argparse
import os
import sys

from bot import Bot
from utilities.logger import *
from managers.http import HTTPManager
from managers.scheduler import Scheduler, BackgroundScheduler
from managers.irc_ import IRCManager


def main(args):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    filepath = config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding="utf-8")

    if not filepath:
        logger.error("Config path missing or invalid")
        sys.exit(0)

    HTTPManager.init()
    Scheduler.init()
    BackgroundScheduler.init()

    bot = Bot(config, args)
    print(args)

    bot.start()


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", "-c", default="config.ini", help="Choose config (default: config.ini)")

    args_parser.add_argument("--build")
    args = args_parser.parse_args()
    print(args)

    debug()

    main(args)
