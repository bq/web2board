import copy
import json
import logging.config
import os

import click

from libs.PathsManager import PathsManager

__author__ = 'jorge.garcia'


class ColoredConsoleHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super(ColoredConsoleHandler, self).__init__(stream)

    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers

        myRecord = copy.copy(record)
        try:
            self.format(myRecord)
        except:
            myRecord.msg = "Unable to format record"
            self.format(myRecord)
        style = self.__getStyle(myRecord)
        click.secho(self.format(myRecord), **style)
        # self.__addColor(myRecord)

        # logging.StreamHandler.emit(self, myRecord)
        # if myRecord.levelno >= 50:
        #     os._exit(1)

    def __getStyle(self, myRecord):
        """
        Supported color names:

        * ``black`` (might be a gray)
        * ``red``
        * ``green``
        * ``yellow`` (might be an orange)
        * ``blue``
        * ``magenta``
        * ``cyan``
        * ``white`` (might be light gray)
        * ``reset`` (reset the color code only)

        :param myRecord:
        :return: Dict
        """
        style = {"fg": None, "bg": None, "bold": True, "blink": None, "underline": None}
        try:
            levelNo = myRecord.levelno
            if levelNo >= 50:  # CRITICAL / FATAL
                style["fg"] = 'red'
                style["bg"] = 'white'
                style["underline"] = True
            elif levelNo >= 40:  # ERROR
                style["fg"] = 'red'
            elif levelNo >= 30:  # WARNING
                style["fg"] = 'magenta'
            elif levelNo >= 20:  # INFO
                style["fg"] = 'green'
            elif levelNo >= 10:  # DEBUG
                style["fg"] = 'cyan'
            else:  # NOTSET and anything else
                pass
        except:
            pass
        return style


def initLogging(name):
    if os.path.isfile(PathsManager.SETTINGS_LOGGING_CONFIG_PATH):
        logging.config.dictConfig(json.load(open(PathsManager.SETTINGS_LOGGING_CONFIG_PATH)))
    else:
        logging.config.dictConfig(json.load(open(PathsManager.RES_LOGGING_CONFIG_PATH)))
    logging.getLogger("ws4py").setLevel(logging.ERROR)

    return logging.getLogger(name)