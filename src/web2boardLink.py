import logging
import os
import shutil
import sys
import subprocess

import time
from PySide import QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QMessageBox

import libs.utils as utils
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager

msgBox = None


def startLogger():
    fileHandler = logging.FileHandler(PathsManager.getHomePath()  + os.sep + "web2boardLink.log", 'a')
    fileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(fileHandler)
    log.setLevel(logging.DEBUG)

startLogger()
log = logging.getLogger(__name__)

@asynchronous()
def factoryReset(web2boardPath):
    try:
        time.sleep(5)
        log.info("deleting web2board of : {}".format(PathsManager.PROGRAM_PATH))
        if os.path.exists(PathsManager.PROGRAM_PATH):
            shutil.rmtree(PathsManager.PROGRAM_PATH)
        log.info("Extracting web2board...")
        shutil.copytree(utils.getModulePath() + os.sep + "web2board", PathsManager.PROGRAM_PATH)
        os.system(web2boardPath + " --afterInstall")
    finally:
        endMessageBox()
        log.exception("Failed performing Factory reset")

@InGuiThread()
def endMessageBox():
    global msgBox
    msgBox.setText("Web2board successfully configured")
    msgBox.setStandardButtons(QMessageBox.Ok)

if __name__ == '__main__':
    web2boardPath = '"' + os.path.join(PathsManager.PROGRAM_PATH, "web2board" + utils.getOsExecutableExtension()) + '"'
    print "web2boardPath: {}".format(web2boardPath)
    utils.killProcess("web2board"  + utils.getOsExecutableExtension())

    if (len(sys.argv) > 1 and sys.argv[1].lower() == "factoryreset") or not os.path.exists(PathsManager.PROGRAM_PATH):
        global msgBox
        log.debug("preforming factoryReset")
        app = QtGui.QApplication(sys.argv)
        task = factoryReset(web2boardPath)
        msgBox = QMessageBox(None)
        msgBox.setStandardButtons(0)
        msgBox.setAttribute(Qt.WA_DeleteOnClose)
        msgBox.setWindowTitle("Starting web2board")
        msgBox.setText("Web2board is configuring some files.\nThis can take a while but it will be done just once")
        msgBox.open()
        app.exec_()

    os.popen(web2boardPath)
