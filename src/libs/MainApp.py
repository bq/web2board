import importlib
import logging
import os
import time
import urllib2
from PySide import QtGui
from optparse import OptionParser
from urllib2 import HTTPError, URLError
from wsgiref.simple_server import make_server

import sys

from PySide.QtCore import Qt
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from libs.WSCommunication.ConnectionHandler import WSConnectionHandler
from wshubsapi.HubsInspector import HubsInspector

from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs import utils
from Scripts.TestRunner import runAllTests, runIntegrationTests, runUnitTests
from Scripts import afterInstallScript
from libs.PathsManager import PathsManager
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater

log = logging.getLogger(__name__)
__mainApp = None


class MainApp:
    def __init__(self):
        self.w2bGui = None
        """:type : frames.Web2boardWindow.Web2boardWindow"""
        self.w2bServer = None
        self.isAppRunning = False

    @asynchronous()
    def __handleTestingOptions(self, testing):
        sys.argv[1:] = []
        if testing != "none":
            if testing == "unit":
                runUnitTests()
            elif testing == "integration":
                runIntegrationTests()
            elif testing == "all":
                runAllTests()

            log.warning("\nexiting program in 10s")
            time.sleep(3)
            os._exit(1)

    def handleSystemArguments(self):
        parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
        parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
        parser.add_option("--port", default=9876, type='int', action="store", dest="port", help="port (9876)")
        parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
        parser.add_option("--test", default='none', type='string', action="store", dest="testing",
                          help="options: [none, unit, integration, all]")
        parser.add_option("--afterInstall", default=False, action="store_true", dest="afterInstall",
                          help="setup packages and folder structure")
        parser.add_option("--board", default="uno", type='string', action="store", dest="board",
                          help="board connected for integration tests")
        parser.add_option("--logLevel", default="info", type='string', action="store", dest="logLevel",
                          help="show more or less info, options[debug, info, warning, error, critical")

        options, args = parser.parse_args()
        log.info("init web2board with options: {}, and args: {}".format(options, args))

        logLevels = {"debug": logging.DEBUG,"info": logging.INFO,"warning": logging.WARNING,
                     "error": logging.ERROR,"critical": logging.CRITICAL}
        logging.getLogger().setLevel(logLevels[options.logLevel.lower()])

        if options.afterInstall:
            afterInstallScript.run()

        if not os.environ.get("platformioBoard", False):
            os.environ["platformioBoard"] = options.board
            getCompilerUploader().setBoard(options.board)

        self.__handleTestingOptions(options.testing.lower())

        return options

    def initializeServerAndCommunicationProtocol(self, options):
        importlib.import_module("libs.WSCommunication.Hubs")
        HubsInspector.inspectImplementedHubs()
        # do not call this line in executable
        if not utils.areWeFrozen():
            HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
        self.w2bServer = make_server(options.host, options.port, server_class=WSGIServer,
                                     handler_class=WebSocketWSGIRequestHandler,
                                     app=WebSocketWSGIApplication(handler_cls=WSConnectionHandler))
        self.w2bServer.initialize_websockets_manager()
        return self.w2bServer

    @asynchronous()
    def updateLibrariesIfNecessary(self):
        try:
            getBitbloqLibsUpdater().readCurrentVersionInfo()
            getBitbloqLibsUpdater().restoreCurrentVersionIfNecessary()
        except (HTTPError, URLError):
            log.error("unable to download libraries (might be a proxy problem)")
            proxyName = raw_input("introduce proxy name: ")
            proxy = urllib2.ProxyHandler({'http': proxyName})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            self.updateLibrariesIfNecessary()
        except OSError:
            log.exception("unable to copy libraries files, there could be a permissions problem.")

    def startConsoleViewer(self):
        from frames.Web2boardWindow import Web2boardWindow

        app = QtGui.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        self.w2bGui = Web2boardWindow(None)
        if not utils.isTrayIconAvailable():
            self.w2bGui.setWindowState(Qt.WindowMinimized)
            self.w2bGui.show()
        self.isAppRunning = True
        return app

    @asynchronous()
    def startServer(self, options):
        while not self.isAppRunning:
            time.sleep(0.1)

        self.w2bServer = self.initializeServerAndCommunicationProtocol(options)

        try:
            log.info("listening...")
            self.w2bServer.serve_forever()
        finally:
            os._exit(1)

    def startMain(self):
        app = self.startConsoleViewer()
        PathsManager.moveInternalConfigToExternalIfNecessary()
        self.updateLibrariesIfNecessary()
        options = self.handleSystemArguments()
        PathsManager.logRelevantEnvironmentalPaths()
        # self.updateLibrariesIfNecessary()
        if not options.afterInstall:
            self.startServer(options)

        return app

    def isSerialMonitorRunning(self):
        return self.w2bGui is not None and self.w2bGui.isSerialMonitorRunning()


def getMainApp():
    global __mainApp
    if __mainApp is None:
        __mainApp = MainApp()
    return __mainApp
