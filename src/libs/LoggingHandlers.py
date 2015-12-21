import copy
import logging
import os

from libs.TerminalController import TerminalController

__author__ = 'jorge.garcia'


class ColoredConsoleHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super(ColoredConsoleHandler, self).__init__(stream)
        self.terminalController = TerminalController()

    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers

        myRecord = copy.copy(record)
        try:
            self.format(myRecord)
        except:
            myRecord.msg = "Unable to format record"
            self.format(myRecord)

        self.__addColor(myRecord)

        logging.StreamHandler.emit(self, myRecord)
        if myRecord.levelno >= 50:
            os._exit(1)

    def __addColor(self, myRecord):
        try:
            levelNo = myRecord.levelno
            if levelNo >= 50:  # CRITICAL / FATAL
                color = '${RED}${BOLD}${BG_YELLOW}'
            elif levelNo >= 40:  # ERROR
                color = '${RED}'
            elif levelNo >= 30:  # WARNING
                color = '${YELLOW}'
            elif levelNo >= 20:  # INFO
                color = '${GREEN}'
            elif levelNo >= 10:  # DEBUG
                color = '${CYAN}'
            else:  # NOTSET and anything else
                color = '${NORMAL}'

            myRecord.msg = self.terminalController.render(color + myRecord.msg + '${NORMAL}')
        except:
            # if error parsing message, just let the default handler
            pass
