#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2015                                                     #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
# -----------------------------------------------------------------------#

import sys
import time
from PySide import QtGui

import logging

import serial
from PySide.QtGui import QTextCursor

from frames.UI_serialMonitor import Ui_SerialMonitor
from libs.CompilerUploader import CompilerUploader
from libs.Config import Config
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager
from libs.WSCommunication.Clients.WSHubsApi import HubsAPI

log = logging.getLogger(__name__)

class SerialMonitorDialog(QtGui.QMainWindow):
    def __init__(self, parent, port=None, *args, **kwargs):
        super(SerialMonitorDialog, self).__init__(*args, **kwargs)
        self.api = HubsAPI("ws://{0}:{1}".format(Config.webSocketIP, Config.webSocketPort))
        self.api.connect()
        self.api.defaultOnError = lambda error: "failed executing action due to: {}".format(error)
        self.isClosed = False
        self.ui = Ui_SerialMonitor()
        self.ui.setupUi(self)
        self.ui.sendButton.clicked.connect(self.onSend)
        self.messagesBuffer = []

        self.ui.clearButton.clicked.connect(self.onClear)
        self.ui.sendLineEdit.returnPressed.connect(self.onSend)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui.baudrateBox.currentIndexChanged.connect(self.onBaudrateChanged)
        self.ui.pauseButton.clicked.connect(self.onPauseButtonClicked)
        self.port = port if port is not None else CompilerUploader().getPort()

        self.api.SerialMonitorHub.client.received = self.refreshConsole
        self.api.SerialMonitorHub.server.startConnection(self.port) \
            .done(lambda x: log.debug("Successfully connected to serial port"),
                  lambda error: log.error("Unable to connect to serial port due to: {}".format(error)))
        self.api.SerialMonitorHub.server.subscribeToHub()

    def showEvent(self, *args, **kwargs):
        super(SerialMonitorDialog, self).showEvent(*args, **kwargs)

    def closeEvent(self, event):
        self.isClosed = True
        self.api.SerialMonitorHub.server.closeConnection(self.port)
        time.sleep(0.5)
        self.api.wsClient.close()
        event.accept()

    @InGuiThread()
    def logText(self, message):
        if message is not None and isinstance(message, basestring):
            message = message.replace("\r", "")
            textLines = self.ui.consoleTextEdit.toPlainText().split("\n")
            if len(textLines) >= 800 or len(textLines[-1]) > 300:
                self.ui.consoleTextEdit.setText(message)
            else:
                self.ui.consoleTextEdit.moveCursor(QTextCursor.End)
                self.ui.consoleTextEdit.insertPlainText(message)
                self.ui.consoleTextEdit.moveCursor(QTextCursor.End)

    def onPauseButtonClicked(self):
        if self.ui.pauseButton.isChecked():
            self.logText('\n*** SERIAL MONITOR PAUSED ***\n\n')
            self.ui.pauseButton.setText("Paused")
        else:
            self.ui.pauseButton.setText("Pause")

    def refreshConsole(self, port, data):
        if not self.ui.pauseButton.isChecked() and port == self.port:
            try:
                self.logText(data)
            except:
                log.exception("Error reading serial")
                pass

    def onSend(self):
        message = self.ui.sendLineEdit.text()
        if message == "":
            return
        self.api.SerialMonitorHub.server.write(self.port, message)
        self.ui.sendLineEdit.setText('')

    def onClear(self):
        self.ui.consoleTextEdit.clear()
        self.ui.sendLineEdit.setText("")

    def onBaudrateChanged(self, event):
        self.api.SerialMonitorHub.server.changeBaudrate(self.port, int(self.ui.baudrateBox.currentText())) \
            .done(lambda x: log.debug("Successfully changed baudrate to {}".format(self.ui.baudrateBox.currentText())),
                  lambda error: log.error("Unable to change baudrate due to: {}".format(error)))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = SerialMonitorDialog(None, port="COM7")
    mySW.show()
    sys.exit(app.exec_())
