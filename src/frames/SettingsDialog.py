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
import sys
import time

from PySide import QtGui
from frames.UI_settingsDialog import Ui_SettingsDialog
from libs.Config import Config

log = logging.getLogger(__name__)


class SettingsDialog(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.isClosed = False
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.setUpSettings()

        self.ui.ok.clicked.connect(self.onOk)
        self.ui.cancel.clicked.connect(self.close)

        self.__closeFromOk = False

    def setUpSettings(self):
        self.ui.wsIP.setText(Config.webSocketIP)
        self.ui.wsPort.setValue(Config.webSocketPort)
        self.ui.proxy.setText(Config.proxy)

        if Config.logLevel <= logging.DEBUG:
            self.ui.logLevelDebug.setChecked(True)
        elif Config.logLevel <= logging.INFO:
            self.ui.logLevelInfo.setChecked(True)
        elif Config.logLevel <= logging.WARNING:
            self.ui.logLevelWarnig.setChecked(True)
        elif Config.logLevel <= logging.ERROR:
            self.ui.logLevelError.setChecked(True)
        elif Config.logLevel <= logging.CRITICAL:
            self.ui.logLevelCritial.setChecked(True)

        self.ui.checkUpdates.setChecked(Config.checkOnlineUpdates)

    def closeEvent(self, event):
        if self.__closeFromOk:
            QtGui.QMessageBox.information(self, "Info", "It is necessary to restart web2board to apply changes")
            event.accept()
        else:
            reply = QtGui.QMessageBox.question(self, "Are you sure you want to quit? ",
                                               "Changes will be lost",
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def onOk(self):
        Config.webSocketIP = self.ui.wsIP.text()
        Config.wsPort = self.ui.wsPort.value()
        Config.proxy = self.ui.proxy.text()

        if self.ui.logLevelDebug.isChecked():
            Config.logLevel = logging.DEBUG
        elif self.ui.logLevelInfo.isChecked():
            Config.logLevel = logging.INFO
        elif self.ui.logLevelWarnig.isChecked():
            Config.logLevel = logging.WARNING
        elif self.ui.logLevelError.isChecked():
            Config.logLevel = logging.ERROR
        elif self.ui.logLevelCritial.isChecked():
            Config.logLevel = logging.CRITICAL

        Config.checkOnlineUpdates = self.ui.checkUpdates.isChecked()
        Config.storeConfigInFile()
        self.__closeFromOk = True
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    Config.readConfigFile()
    mySW = SettingsDialog(None)
    mySW.show()
    sys.exit(app.exec_())
