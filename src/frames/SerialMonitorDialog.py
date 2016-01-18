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
from PySide.QtCore import QTimer

from frames.UI_serialMonitor import Ui_SerialMonitor
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)



class SerialConnection:
    def __init__(self, port):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = 9600
        self.serial.open()

    def getData(self):
        if self.serial.isOpen():
            out = ''
            try:
                while self.serial.inWaiting() > 0:
                    out += self.serial.read(1)
                if out != '':
                    return out
            except Exception as e:
                log.critical("error getting data {}".format(e), exc_info=1)

    def write(self, data):
        self.serial.write(data.encode())

    def changeBaudRate(self, value):
        self.serial.close()
        self.serial.baudrate = value
        self.serial.open()

    def close(self):
        self.serial.close()


class SerialMonitorDialog(QtGui.QDialog):
    def __init__(self, parent, port=None, *args, **kwargs):
        super(SerialMonitorDialog, self).__init__(*args, **kwargs)
        self.isClosed = False
        self.ui = Ui_SerialMonitor()
        self.ui.setupUi(self)
        self.ui.sendButton.clicked.connect(self.onSend)
        self.serialConnection = SerialConnection(port if port is not None else getCompilerUploader().getPort())
        self.messagesBuffer = []

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refreshConsole)
        self.timer.start()
        self.ui.clearButton.clicked.connect(self.onClear)

        self.ui.sendLineEdit.returnPressed.connect(self.onSend)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))

        self.ui.pauseButton.clicked.connect(self.onPauseButtonClicked)

    def closeEvent(self, event):
        self.serialConnection.close()
        self.isClosed = True
        i = 0
        while i < 30:  # 3 seconds of timeout
            try:
                i += 1
                SerialConnection(self.serialConnection.serial.port)
                break
            except:
                time.sleep(0.1)
        event.accept()

    def logText(self, message):
        if message is not None:
            textLines = self.ui.consoleTextEdit.toPlainText().split("\n")
            if len(textLines) >= 800 or len(textLines[-1]) > 300:
                self.ui.consoleTextEdit.setText(message)
            else:
                self.ui.consoleTextEdit.append(message)

    def onPauseButtonClicked(self):
        if self.ui.pauseButton.isChecked():
            self.logText('\n*** SERIAL MONITOR PAUSED ***\n\n')
            self.ui.pauseButton.setText("Paused")
        else:
            self.ui.pauseButton.setText("Pause")

    def refreshConsole(self):
        if not self.ui.pauseButton.isChecked():
            try:
                self.logText(self.serialConnection.getData())
            except:
                log.exception("Error reading serial")
                pass

    def onSend(self):
        message = self.ui.sendLineEdit.text()
        if message == "":
            return
        self.logText(message)
        self.serialConnection.write(message)
        self.ui.sendLineEdit.setText('')

    def onPause(self):
        if self.pauseButton.GetLabel() == 'Pause':
            self.pauseButton.SetLabel('Continue')
            self.Pause = True
        else:
            self.pauseButton.SetLabel('Pause')
            self.Pause = False

    def onClear(self):
        self.ui.consoleTextEdit.clear()
        self.ui.sendLineEdit.setText("")

    def onBaudRateChanged(self, event):
        self.serialConnection.changeBaudRate(self.dropdown.GetValue())

    @InGuiThread()
    def onThread(self):
        self.logText("testing")

@asynchronous()
def onThread(serialMonitor):
    time.sleep(2)
    for i in range(10):
        serialMonitor.onThread()
        time.sleep(1)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = SerialMonitor(None)
    onThread(mySW)
    mySW.show()
    sys.exit(app.exec_())
