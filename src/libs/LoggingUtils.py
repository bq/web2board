import copy
import importlib
import json
import logging
import logging.config
import os
import sys
import time

from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager

__author__ = 'jorge.garcia'


class ColoredConsoleHandler(logging.StreamHandler):
    FILE_ENCODING = sys.getfilesystemencoding()
    def __init__(self, stream=None):
        super(ColoredConsoleHandler, self).__init__(stream)

    def handle(self, record):
        return super(ColoredConsoleHandler, self).handle(record)

    def emit(self, record):
        module = importlib.import_module("libs.MainApp")

        # Need to make an actual copy of the record
        # to prevent altering the message for other loggers
        myRecord = copy.copy(record)
        try:
            self.format(myRecord)
        except:
            try:
                myRecord.msg = myRecord.msg.decode(self.FILE_ENCODING)
                self.format(myRecord)
            except:
                try:
                    myRecord.msg = myRecord.msg.decode("utf-8", errors="replace")
                    self.format(myRecord)
                except:
                    myRecord.msg = "Unable to format record"

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