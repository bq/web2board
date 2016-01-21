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
from datetime import datetime

import time
from PySide import QtGui

from frames.UI_Updater import Ui_Updater
from libs.PathsManager import PathsManager
from libs.Decorators.InGuiThread import InGuiThread
from libs.Downloader import Downloader
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
from libs import utils

log = logging.getLogger(__name__)


class UpdaterDialog(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(UpdaterDialog, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui = Ui_Updater()
        self.ui.setupUi(self)
        self.web2boardUpdater = getWeb2boardUpdater()
        self.downloader = self.web2boardUpdater.downloader
        self.destinationZipFile = os.path.join(PathsManager.MAIN_PATH, os.pardir, "000.zip")
        self.__lastCurrentSize = 0
        self.__lastProgressChecked = None

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def download(self, versionInfo=None):
        self.ui.info.setText("Starting the download process")
        self.ui.title.setText("Downloading")
        self.__lastProgressChecked = time.clock()
        url = self.web2boardUpdater.getDownloadUrl(versionInfo)
        self.downloader.download(url,
                                 infoCallback=self.refreshProgressBar,
                                 dst=self.destinationZipFile,
                                 finishCallback=self.downloadEnded)

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
        self.ui.progressBar.hide()
        self.ui.title.setText("Extracting new version")
        self.web2boardUpdater.update(self.destinationZipFile)
        utils.extractZip(self.destinationZipFile, PathsManager.getOriginalPathForUpdate())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = UpdaterDialog(None)
    mySW.download()
    mySW.show()
    sys.exit(app.exec_())
