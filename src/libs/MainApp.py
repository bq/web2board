import json
import logging
import os
import sys
import time
import urllib2
from optparse import OptionParser
from urllib2 import HTTPError, URLError

from PySide import QtGui
from tornado import web, ioloop
from wshubsapi.HubsInspector import HubsInspector

from Scripts.TestRunner import runAllTests, runIntegrationTests, runUnitTests
from libs import utils
from libs.Config import Config
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.InGuiThread import InGuiThread
from libs.PathsManager import PathsManager
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
from libs.WSCommunication.Clients.WSHubsApi import HubsAPI
from libs.WSCommunication.ConnectionHandler import WSConnectionHandler

log = logging.getLogger(__name__)
__mainApp = None


class MainApp:
    def __init__(self):
        self.w2bGui = None
        """:type : frames.Web2boardWindow.Web2boardWindow"""
        self.w2bServer = None
        self.isAppRunning = False
        self.qtApp = None

    @InGuiThread()
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
            time.sleep(10)
            os._exit(1)

    def parseSystemArguments(self):
        parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
        parser.add_option("--host", default=Config.webSocketIP, type='string', action="store", dest="host", help="hostname (localhost)")
        parser.add_option("--port", default=Config.webSocketPort, type='int', action="store", dest="port", help="port (9876)")
        parser.add_option("--test", default='none', type='string', action="store", dest="testing",
                          help="options: [none, unit, integration, all]")
        parser.add_option("--board", default="uno", type='string', action="store", dest="board",
                          help="board connected for integration tests")
        parser.add_option("--logLevel", default=Config.logLevel, type='string', action="store", dest="logLevel",
                          help="show more or less info, options[debug, info, warning, error, critical")
        parser.add_option("--update2version", default=None, type='string', action="store", dest="update2version",
                          help="auto update to version")
        parser.add_option("--proxy", default=Config.proxy, type='string', action="store", dest="proxy",
                          help="define proxy for internet connections")

        return parser.parse_args()

    def handleSystemArguments(self, options, args):
        log.info("init web2board with options: {}, and args: {}".format(options, args))
        utils.setLogLevel(options.logLevel)

        if not os.environ.get("platformioBoard", False):
            os.environ["platformioBoard"] = options.board

        if options.proxy is not None:
            proxy = urllib2.ProxyHandler({'http': options.proxy})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)

        if options.update2version is not None:
            log.debug("updating version")
            getWeb2boardUpdater().update(PathsManager.getDstPathForUpdate(options.update2version))

        self.__handleTestingOptions(options.testing.lower())

        return options

    def initializeServerAndCommunicationProtocol(self, options):
        # do not call this line in executable
        if not utils.areWeFrozen():
            HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
            HubsInspector.constructPythonFile(path="libs/WSCommunication/Clients")
        self.w2bServer = web.Application([
            (r'/(.*)', WSConnectionHandler),
        ])
        Config.webSocketPort = options.port
        self.w2bServer.listen(options.port)
        return self.w2bServer

    @asynchronous()
    def updateLibrariesIfNecessary(self):
        try:
            getBitbloqLibsUpdater().restoreCurrentVersionIfNecessary()
        except (HTTPError, URLError) as e:
            log.error("unable to download libraries (might be a proxy problem)")
            proxyName = raw_input("introduce proxy name: ")
            proxy = urllib2.ProxyHandler({'http': proxyName})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            self.updateLibrariesIfNecessary()
        except OSError:
            log.exception("unable to copy libraries files, there could be a permissions problem.")

    @asynchronous()
    def checkConnectionIsAvailable(self):
        time.sleep(1)
        self.api = HubsAPI("ws://{0}:{1}".format(Config.webSocketIP, Config.webSocketPort))
        try:
            self.api.connect()
        except Exception as e:
            pass
        else:
            log.info("connection available")

    def startServer(self, options):
        self.w2bServer = self.initializeServerAndCommunicationProtocol(options)

        try:
            log.info("listening...")
            # self.checkConnectionIsAvailable()
            ioloop.IOLoop.instance().start()
        finally:
            forceQuit()

    def startMain(self):
        Config.readConfigFile()
        PathsManager.cleanPioEnvs()
        options, args = self.parseSystemArguments()
        self.updateLibrariesIfNecessary()
        self.handleSystemArguments(options, args)
        log.debug("Enviromental data:")
        try:
            log.debug(json.dumps(os.environ.data, indent=4, encoding=sys.getfilesystemencoding()))
        except:
            log.exception("unable to log environmental data")
        try:
            PathsManager.logRelevantEnvironmentalPaths()
        except:
            log.exception("Unable to log Paths")
        if options.update2version is None:
            self.startServer(options)
            self.testConnection()

    def isSerialMonitorRunning(self):
        return self.w2bGui is not None and self.w2bGui.isSerialMonitorRunning()

    @asynchronous()
    def testConnection(self):
        import socket
        time.sleep(2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((Config.getClientWSIP(), Config.webSocketPort))
        if result == 0:
            log.debug("Port is open")
        else:
            log.error("Port: {} could not be opened, check Antivirus configuration".format(Config.webSocketPort))


def getMainApp():
    global __mainApp
    if __mainApp is None:
        __mainApp = MainApp()
    return __mainApp


def isTrayIconAvailable():
    return utils.isWindows() and QtGui.QSystemTrayIcon.isSystemTrayAvailable()


@InGuiThread()
def forceQuit():
    try:
        mainApp = getMainApp()
        mainApp.w2bGui.closeTrayIcon()
        mainApp.qtApp.quit()
    finally:
        pass
