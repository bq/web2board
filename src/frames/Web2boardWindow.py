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
import os
import sys
import time
from PySide import QtGui
import logging

from PySide.QtCore import Qt, QTimer

from frames.SerialMonitorDialog import SerialMonitorDialog
from frames.UI_web2board import Ui_Web2board
from libs import utils
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)


class Web2boardWindow(QtGui.QMainWindow):
    CONSOLE_MESSAGE_DIV = "<div style='color:{fg}; font-weight:{bold}'; text-decoration:{underline} >{msg}</div>"

    def __init__(self, *args, **kwargs):
        super(Web2boardWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui = Ui_Web2board()
        self.ui.setupUi(self)
        self.availablePorts = []
        self.autoPort = None
        self.ui.searchPorts.clicked.connect(self.onSearchPorts)
        self.compileUpdater = getCompilerUploader()
        self.serialMonitor = None

        self.trayIcon = None
        self.trayIconMenu = None
        if utils.isTrayIconAvailable():
            self.createTrayIcon()

    def __getConsoleKwargs(self, record):
        record.msg = record.msg.encode("utf-8")
        style = dict(fg=None, bg=None, bold="normal", underline="none", msg=record.msg)
        try:
            levelNo = record.levelno
            if levelNo >= 50:  # CRITICAL / FATAL
                style["fg"] = 'red'
                style["bold"] = "bold"
                style["underline"] = "underline"
            elif levelNo >= 40:  # ERROR
                style["fg"] = 'red'
                style["bold"] = "bold"
            elif levelNo >= 30:  # WARNING
                style["fg"] = 'orange'
            elif levelNo >= 20:  # INFO
                style["fg"] = 'green'
            elif levelNo >= 10:  # DEBUG
                style["fg"] = 'blue'
            else:  # NOTSET and anything else
                pass
        except:
            pass
        return style

    def onSearchPorts(self):
        self.ui.searchPorts.setEnabled(False)
        self.ui.statusbar.showMessage("Searching ports...")
        self.__getPorts()

    def createTrayIcon(self):
        def onTrayIconActivated(reason):
            if reason == QtGui.QSystemTrayIcon.ActivationReason.Trigger:
                self.show()

        showAppAction = QtGui.QAction("ShowApp", self, triggered=self.showApp)
        quitAction = QtGui.QAction("&Quit", self, triggered=QtGui.qApp.quit)

        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(showAppAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.trayIcon.setToolTip("Web2board application")
        self.trayIcon.activated.connect(onTrayIconActivated)
        self.trayIcon.messageClicked.connect(self.show)
        self.trayIcon.show()

        self.ui.forceClose.clicked.connect(lambda *args: os._exit(1))

    def closeEvent(self, event):
        if utils.isTrayIconAvailable():
            self.hide()
            self.showBalloonMessage("Web2board is running in background.\nClick Quit to totally end the application")
        else:
            self.setWindowState(Qt.WindowMinimized)
        event.ignore()

    @InGuiThread()
    def logInConsole(self, record):
        kwargs = self.__getConsoleKwargs(record)
        message = self.CONSOLE_MESSAGE_DIV.format(**kwargs)

        if message.endswith("\n"):
            message = message[:-1]
        message = message.replace("\n", "<br>")
        message = message.replace("  ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        self.ui.console.append(message.decode("utf-8"))
        if record.levelno >= logging.ERROR:
            self.showBalloonMessage("Critical error occurred\nPlease check the history log",
                                    icon=QtGui.QSystemTrayIcon.Warning)

    @InGuiThread()
    def showBalloonMessage(self, message, title="Web2board", icon=QtGui.QSystemTrayIcon.Information):
        if utils.isTrayIconAvailable():
            self.trayIcon.showMessage(title, message, icon)

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
    def startSerialMonitorApp(self, port):
        self.serialMonitor = SerialMonitorDialog(None, port)
        self.serialMonitor.show()
        self.serialMonitor.raise_()
        self.serialMonitor.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    @InGuiThread()
    def closeSerialMonitorApp(self):
        self.serialMonitor.Close()
        self.serialMonitor = None

    def isSerialMonitorRunning(self):
        return self.serialMonitor is not None

    @InGuiThread()
    def showApp(self):
        if not self.isVisible():
            self.show()
            self.setWindowState(Qt.WindowNoState)
            self.raise_()

    @InGuiThread()
    def changeConnectedStatus(self):
        self.ui.wsConnectedLabel.setText("Connected")


@asynchronous()
def onThread(serialMonitor):
    time.sleep(2)
    serialMonitor.showBalloonMessage(
            "Don't believe me. Honestly, I don't have a clue.\nClick this balloon for details.")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = Web2boardWindow(None)
    onThread(mySW)
    mySW.show()
    sys.exit(app.exec_())
