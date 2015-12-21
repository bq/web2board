import json
import logging
import logging.config
import os

logging.config.dictConfig(json.load(open('res' + os.sep +'logging.json')))


def getLog(name):
    return logging.getLogger(name)
