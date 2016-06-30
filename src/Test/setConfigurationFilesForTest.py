import logging

from libs.LoggingUtils import init_logging
from libs.PathsManager import PathsManager


def run():
    log = init_logging(__name__)
    log.setLevel(logging.INFO)

if __name__ == '__main__':
    run()

