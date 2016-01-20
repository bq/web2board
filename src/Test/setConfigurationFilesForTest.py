import logging

from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager


def run():
    log = initLogging(__name__)
    log.setLevel(logging.INFO)

if __name__ == '__main__':
    run()

