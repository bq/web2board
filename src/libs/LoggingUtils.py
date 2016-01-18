import copy
import json
import logging
import logging.config
import os
import sys

from libs.PathsManager import PathsManager

__author__ = 'jorge.garcia'


class ColoredConsoleHandler(logging.StreamHandler):
    FILE_ENCODING = sys.getfilesystemencoding()
    def __init__(self, stream=None):
        super(ColoredConsoleHandler, self).__init__(stream)

    def handle(self, record):
        return super(ColoredConsoleHandler, self).handle(record)

    def emit(self, record):
        import libs.MainApp
        # Need to make a actual copy of the record
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

        super(ColoredConsoleHandler, self).emit(record)

        gui = libs.MainApp.getMainApp().w2bGui
        if gui is not None:
            myRecord.msg = self.format(myRecord)
            gui.logInConsole(myRecord)

        if myRecord.levelno >= 50:
            os._exit(1)


def initLogging(name):
    """
    :rtype: logging.Logger
    """
    if os.path.isfile(PathsManager.SETTINGS_LOGGING_CONFIG_PATH):
        logging.config.dictConfig(json.load(open(PathsManager.SETTINGS_LOGGING_CONFIG_PATH)))
    else:
        logging.config.dictConfig(json.load(open(PathsManager.RES_LOGGING_CONFIG_PATH)))
    logging.getLogger("ws4py").setLevel(logging.ERROR)

    return logging.getLogger(name)