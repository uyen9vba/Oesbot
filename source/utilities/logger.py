import logging
import sys

logger = logging.getLogger("bot")
logger_stdout = logging.StreamHandler(sys.stdout)
logger_stderr = logging.StreamHandler(sys.stderr)


def debug():
    logger.setLevel(logging.DEBUG)
    logger_stdout.setLevel(logging.DEBUG)
    logger_stderr.setLevel(logging.WARNING)


logging.getLogger().addHandler(logger_stdout)
logging.getLogger().addHandler(logger_stderr)