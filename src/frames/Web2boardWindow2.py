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

from PySide.QtCore import QTimer

from frames.SerialMonitorDialog import SerialMonitorDialog
from frames.UI_web2board import Ui_Web2board
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)



class RedirectText(object):
    def __init__(self, parent, originalStdOut, writeCallback):
        self.parent = parent
        self.originalStdOut = originalStdOut
        self.outs = []
        self.writeCallback = writeCallback

    def write(self, string):
        self.writeCallback(string)
        self.originalStdOut(string)

    def flush(self, *args):
        pass

    def get(self):
        aux = self.outs
        self.outs = []
        return aux

class Web2boardWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Web2boardWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui = Ui_Web2board()
        self.ui.setupUi(self)
        self.availablePorts =[]
        self.autoPort = None
        self.ui.searchPorts.clicked.connect(self.onSearchPorts)
        self.compileUpdater = getCompilerUploader()

        originalStdOut = sys.stdout.write
        self.redir = RedirectText(self, originalStdOut, self.logInConsole)
        sys.stdout = self.redir
        sys.stderr = self.redir
        self.serialMonitor = None

    def onSearchPorts(self):
        self.ui.searchPorts.setEnabled(False)
        self.ui.statusbar.showMessage("Searching ports...")
        self.__getPorts()

    @asynchronous()
    def __getPorts(self):
        try:
            self.availablePorts = self.compileUpdater.getAvailablePorts()
            self.autoPort = self.compileUpdater.getPort()
        finally:
            self.onRefreshFinished()

    @InGuiThread()
    def onRefreshFinished(self):
        lastPortSelection = self.ui.ports.currentText()
        self.ui.statusbar.showMessage("")
        self.ui.ports.clear()
        portsInCombo = ["AUTO sadfsdfsdf"] + self.availablePorts
        for i, port in enumerate(portsInCombo):
            if port == self.autoPort:
                portsInCombo[i] = self.autoPort + " (ok)"
        self.ui.ports.addItems(portsInCombo)
        try:
            selectionIndex = portsInCombo.index(lastPortSelection)
        except:
            selectionIndex = 0
        self.ui.ports.setCurrentIndex(selectionIndex)

        self.ui.searchPorts.setEnabled(True)

    @InGuiThread()
    def logInConsole(self, message):
        if message.endswith("\n"):
            message = message[:-1]
        message = message.replace("\n","<br>")
        message = message.replace("  ","&nbsp;&nbsp;&nbsp;&nbsp;")
        self.ui.console.append(message)

    @InGuiThread()
    def startSerialMonitorApp(self, port):
        self.serialMonitor = SerialMonitorDialog(None, port)
        self.serialMonitor.show()

    @InGuiThread()
    def closeSerialMonitorApp(self):
        self.serialMonitor.Close()
        self.serialMonitor = None

    def isSerialMonitorRunning(self):
        return self.serialMonitor is not None

    @InGuiThread()
    def showApp(self):
        self.show()
        self.raise_()

