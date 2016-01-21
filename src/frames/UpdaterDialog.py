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

from PySide import QtGui

from frames.UI_Updater import Ui_Updater
from libs.PathsManager import PathsManager
from libs.Decorators.InGuiThread import InGuiThread
from libs.Downloader import Downloader
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
from libs import utils

log = logging.getLogger(__name__)


class UpdaterDialog(QtGui.QDialog):
    def __init__(self, parent, port=None, *args, **kwargs):
        super(UpdaterDialog, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
        self.ui = Ui_Updater()
        self.ui.setupUi(self)
        self.web2boardUpdater = getWeb2boardUpdater()
        self.downloader = Downloader()
        self.destinationZipFile = os.path.join(PathsManager.MAIN_PATH, os.pardir, "000.zip")

    def closeEvent(self, event):
        self.hide()

    def download(self):
        url = self.web2boardUpdater.downloadOnlineVersionInfo().file2DownloadUrl
        self.downloader.download(url,
                                 infoCallback=self.refreshProgressBar,
                                 dst=self.destinationZipFile,
                                 finishCallback=self.downloadEnded)

    @InGuiThread()
    def refreshProgressBar(self, current, total, percentage):
        self.ui.info.setText("downloaded {0} of {1}".format(current, total))
        self.ui.progressBar.setValue(int(percentage) + 1)

    @InGuiThread()
    def downloadEnded(self, task):
        self.ui.progressBar.hide()
        self.ui.title.setText("Extracting new version")
        utils.extractZip(self.destinationZipFile, PathsManager.getOriginalPathForUpdate())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = UpdaterDialog(None)
    mySW.download()
    mySW.show()
    sys.exit(app.exec_())
