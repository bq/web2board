import copy
import importlib
import json
import logging
import logging.config
import logging.handlers
import os
import sys
import time

from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager

__author__ = 'jorge.garcia'
FILE_ENCODING = sys.getfilesystemencoding()


def getDecodedMessage(record, handler):
    # Need to make an actual copy of the record
    # to prevent altering the message for other loggers
    myRecord = copy.copy(record)
    try:
        handler.format(myRecord)
    except:
        try:
            myRecord.msg = myRecord.msg.decode(FILE_ENCODING)
            handler.format(myRecord)
        except:
            try:
                myRecord.msg = myRecord.msg.decode("utf-8", errors="replace")
                handler.format(myRecord)
            except:
                myRecord.msg = "Unable to format record"
    return myRecord


class ColoredConsoleHandler(logging.StreamHandler):

    def __init__(self, stream=None):
        super(ColoredConsoleHandler, self).__init__(stream)

    def handle(self, record):
        return super(ColoredConsoleHandler, self).handle(record)

    def emit(self, record):
        module = importlib.import_module("libs.MainApp")
        myRecord = getDecodedMessage(record, self)
        super(ColoredConsoleHandler, self).emit(myRecord)

        gui = module.getMainApp().w2bGui
        if gui is not None:
            myRecord.msg = self.format(myRecord)
            gui.logInConsole(myRecord)

        if myRecord.levelno >= 50:
            self.asyncEnding()

    @asynchronous()
    def asyncEnding(self):
        time.sleep(2)
        os._exit(1)


class RotatingHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(RotatingHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        return super(RotatingHandler, self).handle(record)

    def emit(self, record):
        myRecord = getDecodedMessage(record, self)
        super(RotatingHandler, self).emit(myRecord)



def initLogging(name):
    """
    :rtype: logging.Logger
    """
    if PathsManager.MAIN_PATH == PathsManager.getCopyPathForUpdate():
        fileh = logging.FileHandler(PathsManager.getCopyPathForUpdate() + os.sep + "info.log", 'a')
        fileh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileh.setFormatter(formatter)
        log = logging.getLogger()
        log.addHandler(fileh)
        log.setLevel(logging.DEBUG)
    else:
        logging.config.dictConfig(json.load(open(PathsManager.RES_LOGGING_CONFIG_PATH)))
        logging.getLogger("ws4py").setLevel(logging.ERROR)

    return logging.getLogger(name)