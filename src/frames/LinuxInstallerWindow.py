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
import subprocess
import sys
import time

from PySide import QtGui

from frames.UI_LinuxInstaller import Ui_LinuxInstallerWindow
from libs import utils
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager

try:
    import pwd
except:
    pass


class LinuxInstallerWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(LinuxInstallerWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui = Ui_LinuxInstallerWindow()
        self.ui.setupUi(self)
        self.installationPath = "/opt/web2board" if utils.isLinux() else PathsManager.TEST_SETTINGS_PATH

        self.ui.install.clicked.connect(self.installWeb2board)
        self.ui.cancel.clicked.connect(self.close)
        flags = QtGui.QMessageBox.StandardButton.Yes
        flags |= QtGui.QMessageBox.StandardButton.No
        self.log = None
        self.startLogger()
        self.askForSudo()

    def startLogger(self):
        fileHandler = logging.FileHandler(PathsManager.EXECUTABLE_PATH + os.sep + "error.log", 'a')
        fileHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(formatter)
        self.log = logging.getLogger()
        self.log.addHandler(fileHandler)
        self.log.setLevel(logging.DEBUG)

    def askForSudo(self):
        euid = os.geteuid()
        if euid != 0:
            print "Script not started as root. Running sudo.."
            args = ['gksudo', sys.executable] + sys.argv + [os.environ]
            # the next line replaces the currently-running process with the sudo
            os.execlpe('gksudo', *args)

    def addAllUsersToDialOut(self):
        self.notifyAllUsersInDialOut()
        allUsers = [p[0] for p in pwd.getpwall()]
        for user in allUsers:
            subprocess.call(["sudo", "adduser", user, "dialout"])

    def extractWeb2board(self):
        self.notifyExtractionWeb2board()
        if not os.path.exists(self.installationPath):
            os.makedirs(self.installationPath)

        utils.extractZip(PathsManager.RES_PATH + os.sep + "web2board.zip", self.installationPath)

    @asynchronous()
    def installWeb2board(self):
        try:
            self.addAllUsersToDialOut()
            self.extractWeb2board()
            self.ui.progressBar.setValue(90)
            time.sleep(0.5)  # wait a little bit for user experience
            self.installationCompleted()
        except:
            self.log.exception("failed installing web2board")
            self.errorInInstallationProcess()

    @InGuiThread()
    def notifyAllUsersInDialOut(self):
        self.ui.progressBar.setValue(10)
        self.ui.info.setText("Allowing all users to use serial ports")

    @InGuiThread()
    def notifyExtractionWeb2board(self):
        self.ui.progressBar.setValue(50)
        self.ui.info.setText("Extracting web2board application")

    @InGuiThread()
    def errorInInstallationProcess(self):
        self.ui.progressBar.setValue(0)
        self.ui.info.setText("Error!")
        message = "Unable to install web2board, check error.log for more info"
        QtGui.QMessageBox.critical(self, "Error", message)

    @InGuiThread()
    def installationCompleted(self):
        self.ui.progressBar.setValue(100)
        self.ui.info.setText("Web2board was successfully installer")
        message = """Web2board was successfully installed
It is necessary to restart your computer to use web2board.
Do you want to restart the computer now?"""
        flags = QtGui.QMessageBox.StandardButton.Yes
        flags |= QtGui.QMessageBox.StandardButton.No

        response = QtGui.QMessageBox.question(self, "Success", message, flags)
        if response == QtGui.QMessageBox.No:
            self.close()
        else:
            self.ui.info.setText("Restarting the computer")
            os.system('reboot now')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = LinuxInstallerWindow(None)
    mySW.show()
    sys.exit(app.exec_())
