import copy
import importlib
import json
import logging
import logging.config
import logging.handlers
import os
import sys
import time
from datetime import datetime
from logging import Handler

from wshubsapi.hubs_inspector import HubsInspector

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
        my_record = getDecodedMessage(record, self)
        super(ColoredConsoleHandler, self).emit(my_record)

        if my_record.levelno >= 50:
            self.async_ending()

    @asynchronous()
    def async_ending(self):
        time.sleep(2)
        module = importlib.import_module("libs.MainApp")
        module.forceQuit()


class RotatingHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(RotatingHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        return super(RotatingHandler, self).handle(record)

    def emit(self, record):
        my_record = getDecodedMessage(record, self)
        super(RotatingHandler, self).emit(my_record)


class HubsHandler(Handler):
    def __init__(self, *args, **kwargs):
        super(HubsHandler, self).__init__(*args, **kwargs)
        HubsInspector.inspect_implemented_hubs()

    def handle(self, record):
        return super(HubsHandler, self).handle(record)

    def emit(self, record):
        if '\n{"function": "onLoggingMessage"' in record.msg:
            return
        from libs.WSCommunication.Hubs.LoggingHub import LoggingHub
        r = getDecodedMessage(record, self)
        logging_hub = HubsInspector.get_hub_instance(LoggingHub)
        logging_hub.records_buffer.append(r)
        subscribedClients = logging_hub.clients.getSubscribedClients()
        subscribedClients.onLoggingMessage(datetime.now().isoformat(), r.levelno, r.msg, self.format(r))


def init_logging(name):
    """
    :rtype: logging.Logger
    """
    if PathsManager.MAIN_PATH == PathsManager.get_copy_path_for_update():
        file_handler = logging.FileHandler(PathsManager.get_copy_path_for_update() + os.sep + "info.log", 'a')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        log = logging.getLogger()
        log.addHandler(file_handler)
        log.setLevel(logging.DEBUG)
    else:
        logging.config.dictConfig(json.load(open(PathsManager.RES_LOGGING_CONFIG_PATH)))
        logging.getLogger("ws4py").setLevel(logging.ERROR)

    return logging.getLogger(name)