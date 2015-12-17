import logging
import logging.config
import json

logging.config.dictConfig(json.load(open('logging.json')))

def getLog(name):
    return logging.getLogger(name)