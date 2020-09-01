import configparser
import argparse
import os
import sys

from bot import Bot
from utilities.logger import *


def run(args):
    config = configparser.ConfigParser()

    if not config.read("C:/Users/Niklas/Projects/Oesbot/source/config.ini", encoding="utf-8"):
        logger.error("Config path missing")
        sys.exit(0)

    bot = Bot(config, args)

    bot.start()


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", "-c", default="config.ini", help="Choose config (default: config.ini)")
    args = args_parser.parse_args()

    debug()

    run(args)
