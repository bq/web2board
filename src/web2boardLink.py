import logging
import os
import shutil
import sys

import time


import libs.utils as utils
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager


def startLogger():
    fileHandler = logging.FileHandler(PathsManager.getHomePath() + os.sep + "web2boardLink.log", 'a')
    fileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(fileHandler)
    log.setLevel(logging.DEBUG)

if utils.areWeFrozen():
    os.chdir(os.path.join(PathsManager.MAIN_PATH, "web2board"))
    PathsManager.setAllConstants()
msgBox = None
startLogger()
log = logging.getLogger(__name__)
web2boardPath = os.path.join(PathsManager.PROGRAM_PATH, "web2board" + utils.getOsExecutableExtension())
WATCHDOG_TIME = 60

@asynchronous()
def factoryReset():
    global msgBox
    try:
        startWatchdog()
        logMessage("deleting web2board in: {}".format(PathsManager.PROGRAM_PATH))
        if os.path.exists(PathsManager.PROGRAM_PATH):
            shutil.rmtree(PathsManager.PROGRAM_PATH)
        logMessage("Extracting web2board...")
        shutil.copytree(utils.getModulePath() + os.sep + "web2board", PathsManager.PROGRAM_PATH)
        msgBox.endSuccessful()
    except:
        log.exception("Failed performing Factory reset")
        msgBox.endError()


@asynchronous()
def startWatchdog():
    global msgBox
    timePassed = 0
    while not msgBox.taskEnded and timePassed < WATCHDOG_TIME:
        time.sleep(0.3)
        timePassed += 0.3
    if timePassed >= WATCHDOG_TIME:
        msgBox.endError()


def isFactoryReset():
    return len(sys.argv) > 1 and (sys.argv[1].lower() == "factoryreset" or sys.argv[1].lower() == "--factoryreset")


def logMessage(message):
    global msgBox
    log.info(message)
    msgBox.showMessage(message)


def startDialog():
    global msgBox
    from PySide import QtGui
    from libs.Decorators.InGuiThread import InGuiThread
    from PySide.QtGui import QDialog
    from frames.UI_Link import Ui_Link
    from PySide.QtGui import QMovie
    app = QtGui.QApplication(sys.argv)

    class LinkDialog(QDialog):
        def __init__(self, *args, **kwargs):
            super(LinkDialog, self).__init__(*args, **kwargs)
            self.ui = Ui_Link()
            self.setWindowIcon(QtGui.QIcon(PathsManager.RES_ICO_PATH))
            self.ui.setupUi(self)
            self.ui.tryAgain.setVisible(False)
            self.ui.tryAgain.clicked.connect(self.retry)
            self.taskEnded = False
            self.successfullyEnded = False
            self.movie = QMovie(os.path.join(PathsManager.RES_ICONS_PATH, "loading.gif"))
            self.ui.loading.setMovie(self.movie)
            self.movie.start()
            self.show()

        def closeEvent(self, evt):
            if self.taskEnded:
                evt.accept()
                return
            quit_msg = "It is not possible to quit while configuring files\nThis task can take up to {} seconds"
            QtGui.QMessageBox.warning(self, 'Warning!', quit_msg.format(WATCHDOG_TIME), QtGui.QMessageBox.Ok)
            evt.ignore()

        @InGuiThread()
        def showMessage(self, message):
            self.ui.status.setText(message)

        @InGuiThread()
        def endSuccessful(self):
            self.taskEnded = True
            self.ui.close.setEnabled(True)
            self.successfullyEnded = True
            self.showMessage("Web2board successfully configured")

        @InGuiThread()
        def endError(self):
            self.taskEnded = True
            self.showMessage("Failed to configure file.\nplease try again later or check log.")
            self.ui.tryAgain.setVisible(True)
            self.ui.close.setEnabled(True)
            self.movie.stop()

        def retry(self):
            self.taskEnded = False
            self.ui.close.setEnabled(False)
            self.ui.tryAgain.setVisible(False)
            factoryReset()

    msgBox = LinkDialog()
    return app


if __name__ == '__main__':

    print "web2boardPath: {}".format(web2boardPath)
    utils.killProcess("web2board" + utils.getOsExecutableExtension())
    if isFactoryReset() or not os.path.exists(PathsManager.PROGRAM_PATH):
        global msgBox
        app = startDialog()
        task = factoryReset()
        app.exec_()

    if msgBox is None or msgBox.successfullyEnded:
        os.popen('"{}"'.format(web2boardPath))
