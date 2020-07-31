import argparse

def parse_args():
    arg_parser = argparse.argumentParser()
    arg_parser.add_argument(
        "--config", "-c", default="config.ini", help="Choose config (default: config.ini)"
    )
    
    return arg_parser.parse_args()
