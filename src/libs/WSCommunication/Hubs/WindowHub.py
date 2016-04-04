import logging
import time

from wshubsapi.Hub import Hub

from libs.MainApp import getMainApp, forceQuit


log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class WindowHub(Hub):

    def showApp(self):
        log.info("Showing web2board...")
        getMainApp().w2bGui.showApp()
        return True

    def closeApp(self):
        log.info("Closing web2board...")
        getMainApp().w2bGui.closeApp()
        return True

    def cleanConsole(self):
        log.info("cleaning web2board console...")
        getMainApp().w2bGui.cleanConsole()
        return True

    def forceClose(self, _sender):
        log.info("Client: {} force us to close".format(_sender))
        time.sleep(1)
        forceQuit()