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
import logging
import os
import sys
import time

from PySide import QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QMessageBox

import libs.MainApp
from frames.SerialMonitorDialog import SerialMonitorDialog
from frames.UI_web2board import Ui_Web2board
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
        self.updaterDialog = None

        self.trayIcon = None
        self.trayIconMenu = None
        if libs.MainApp.isTrayIconAvailable():
            self.createTrayIcon()
        self.ui.updateGroupbox.hide()

        self.__lastCurrentSize = 0
        self.__lastProgressChecked = None
        self.__lastVersionDownloaded = ""

        def quit(*args):
            os._exit(1)

        self.ui.forceClose.clicked.connect(quit)

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

    def closeEvent(self, event):
        if libs.MainApp.isTrayIconAvailable():
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
        if libs.MainApp.isTrayIconAvailable():
            self.trayIcon.showMessage(title, message, icon)

    @InGuiThread()
    def showConfirmDialog(self, text, title="Confirm"):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(title)
        msgBox.setInformativeText(text)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Ok)
        return msgBox.exec_() == QMessageBox.Ok

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
        self.serialMonitor.close()
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

    @InGuiThread()
    def startDownload(self, version):
        self.__lastVersionDownloaded = version
        self.ui.updateGroupbox.show()
        self.ui.info.setText("Starting the download process")
        self.__lastProgressChecked = time.clock()

    @InGuiThread()
    def refreshProgressBar(self, current, total, percentage):
        period = (time.clock() - self.__lastProgressChecked)
        self.__lastProgressChecked = time.clock()
        vel = (current - self.__lastCurrentSize) / (period * 1000.0)
        self.__lastCurrentSize = current
        if vel != 0:
            remaining = (long(total) - current) / (vel * 1000.0)
        else:
            remaining = "infinite"
        text = "downloading {0:.1f} Kb/s, {1} of {2}, remaining: {3:.0f} s"
        self.ui.info.setText(text.format(vel, current, total, remaining))
        self.ui.progressBar.setValue(int(percentage) + 1)

    @InGuiThread()
    def downloadEnded(self, task):
        self.ui.updateGroupbox.hide()
        self.ui.progressBar.setValue(0)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = Web2boardWindow(None)
    mySW.show()
    sys.exit(app.exec_())
