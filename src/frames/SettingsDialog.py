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
from PySide.QtGui import QFileDialog

from frames.UI_settingsDialog import Ui_SettingsDialog
from libs import utils
from libs.Config import Config
from libs.PathsManager import PathsManager

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
        self.ui.searchLibrariesDirButton.clicked.connect(self.__openFileDialog)

        self.__closeFromOk = False

    def __openFileDialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.ui.librariesDir.setText(folder.encode("utf-8"))

    def setUpSettings(self):
        self.ui.wsIP.setText(Config.webSocketIP)
        self.ui.wsPort.setValue(Config.webSocketPort)
        self.ui.proxy.setText(Config.proxy)
        self.ui.librariesDir.setText(Config.getPlatformioLibDir())

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
            QtGui.QMessageBox.information(self, "Info", "You might need to restart web2board to apply changes")
            event.accept()
        else:
            reply = QtGui.QMessageBox.question(self, "Are you sure you want to quit? ",
                                               "Changes will be lost",
                                               QtGui.QMessageBox.No,
                                               QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def onOk(self):
        if not os.path.exists(self.ui.librariesDir.text()):
            QtGui.QMessageBox.warning(self, "Warning", "Libraries directory does not exist")
            return
        Config.webSocketIP = self.ui.wsIP.text()
        Config.webSocketPort = self.ui.wsPort.value()
        Config.proxy = self.ui.proxy.text()
        if self.ui.librariesDir.text().encode(sys.getfilesystemencoding()) != Config.getPlatformioLibDir():
            Config.setPlatformioLibDir(self.ui.librariesDir.text().encode(sys.getfilesystemencoding()))
            PathsManager.cleanPioEnvs()

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
        utils.setLogLevel(Config.logLevel)

        Config.checkOnlineUpdates = self.ui.checkUpdates.isChecked()
        Config.storeConfigInFile()
        self.__closeFromOk = True
        self.close()
