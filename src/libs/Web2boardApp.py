import importlib
import logging
import os
import threading
import time
import urllib2
from copy import deepcopy
from optparse import OptionParser
from urllib2 import HTTPError, URLError
from wsgiref.simple_server import make_server

import sys
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler
from wshubsapi.HubsInspector import HubsInspector

from libs.Decorators.Asynchronous import asynchronous
from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs import utils
from Scripts.TestRunner import runAllTests, runIntegrationTests, runUnitTests
from Scripts import afterInstallScript
from libs.PathsManager import PathsManager
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
log = logging.getLogger(__name__)
__web2BoardApp = None


class Web2boardApp:
    def __init__(self):
        self.w2bGui = None
        """:type : frames.Web2boardWindow.Web2boardWindow"""
        self.w2bServer = None
        self.isAppRunning = False

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

        options, args = parser.parse_args()
        log.info("init web2board with options: {}, and args: {}".format(options, args))

        if options.afterInstall:
            afterInstallScript.run()
            log.warning("exiting program...")
            os._exit(1)

        if not os.environ.get("platformioBoard", False):
            os.environ["platformioBoard"] = options.board

        testing = options.testing.lower()
        sys.argv[1:] = []
        if testing != "none":
            if testing == "unit":
                runUnitTests()
            elif testing == "integration":
                runIntegrationTests()
            elif testing == "all":
                runAllTests()
            log.warning("exiting program...")
            os._exit(1)

        return options

    def initializeServerAndCommunicationProtocol(self, options):
        importlib.import_module("libs.WSCommunication.Hubs")
        HubsInspector.inspectImplementedHubs()
        # do not call this line in executable
        if not utils.areWeFrozen():
            HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
        self.w2bServer = make_server(options.host, options.port, server_class=WSGIServer,
                                     handler_class=WebSocketWSGIRequestHandler,
                                     app=WebSocketWSGIApplication(handler_cls=ConnectionHandler))
        self.w2bServer.initialize_websockets_manager()
        return self.w2bServer

    def updateLibrariesIfNecessary(self):
        libUpdater = getBitbloqLibsUpdater()
        try:
            libUpdater.onlineVersionInfo = deepcopy(libUpdater.currentVersionInfo)
            if libUpdater.isNecessaryToUpdate():
                libUpdater.update()
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
        import wx
        from frames.Web2boardWindow import Web2boardWindow

        app = wx.App(False)
        self.w2bGui = Web2boardWindow(None)
        self.w2bGui.Hide()
        self.w2bGui.Raise()
        self.isAppRunning = True
        return app

    @asynchronous()
    def updateLibrariesAndStartServer(self):
        while not self.isAppRunning:
            time.sleep(0.1)

        try:
            getBitbloqLibsUpdater().restoreCurrentVersionIfNecessary()
            self.w2bServer.serve_forever()
            log.info("listening...")
        finally:
            os._exit(1)

    def startMain(self):
        app = self.startConsoleViewer()

        PathsManager.logRelevantEnvironmentalPaths()
        PathsManager.moveInternalConfigToExternalIfNecessary()
        options = self.handleSystemArguments()
        # self.updateLibrariesIfNecessary()
        self.w2bServer = self.initializeServerAndCommunicationProtocol(options)
        self.updateLibrariesAndStartServer()

        return app

    def isSerialMonitorRunning(self):
        return self.w2bGui is not None and self.w2bGui.isSerialMonitorRunning()

def getMainApp():
    global __web2BoardApp
    if __web2BoardApp is None:
        __web2BoardApp = Web2boardApp()
    return __web2BoardApp