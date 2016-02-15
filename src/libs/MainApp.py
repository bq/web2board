import importlib
import logging
import os
import sys
import time
import urllib2
from optparse import OptionParser
from urllib2 import HTTPError, URLError
from wsgiref.simple_server import make_server

from PySide import QtGui
from PySide.QtCore import Qt
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
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
        logLevels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
                     "error": logging.ERROR, "critical": logging.CRITICAL}

        log.info("init web2board with options: {}, and args: {}".format(options, args))

        logLevel = options.logLevel if isinstance(options.logLevel, int) else logLevels[options.logLevel.lower()]
        logging.getLogger().handlers[0].level = logLevel

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
        importlib.import_module("libs.WSCommunication.Hubs")
        HubsInspector.inspectImplementedHubs()
        # do not call this line in executable
        if not utils.areWeFrozen():
            HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
            HubsInspector.constructPythonFile(path="libs/WSCommunication/Clients")
        self.w2bServer = make_server(options.host, options.port, server_class=WSGIServer,
                                     handler_class=WebSocketWSGIRequestHandler,
                                     app=WebSocketWSGIApplication(handler_cls=WSConnectionHandler))
        self.w2bServer.initialize_websockets_manager()
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

    def startConsoleViewer(self):
        from frames.Web2boardWindow import Web2boardWindow

        app = QtGui.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        self.w2bGui = Web2boardWindow(None)
        if not isTrayIconAvailable():
            self.w2bGui.setWindowState(Qt.WindowMinimized)
            self.w2bGui.show()
        self.isAppRunning = True
        return app

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

    @asynchronous()
    def startServer(self, options):
        while not self.isAppRunning:
            time.sleep(0.1)

        self.w2bServer = self.initializeServerAndCommunicationProtocol(options)

        try:
            log.info("listening...")
            self.checkConnectionIsAvailable()
            self.w2bServer.serve_forever()
        finally:
            os._exit(1)

    def startMain(self):
        Config.readConfigFile()
        options, args = self.parseSystemArguments()
        app = self.startConsoleViewer()
        self.updateLibrariesIfNecessary()
        self.handleSystemArguments(options, args)
        PathsManager.logRelevantEnvironmentalPaths()
        if options.update2version is None:
            self.startServer(options)

        return app

    def isSerialMonitorRunning(self):
        return self.w2bGui is not None and self.w2bGui.isSerialMonitorRunning()

    @InGuiThread()
    def executeSconsScript(self):
        def revert_io():
            # This call is added to revert stderr and stdout to the original
            # ones just in case some build rule or something else in the system
            # has redirected them elsewhere.
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__
        import res.Scons.sconsFiles.scons
        try:
            class auxFile:
                def __init__(self, *args):
                    self.buffer = ""

                def write(self, message):
                    try:
                        self.buffer += message
                    except:
                        try:
                            self.buffer += message.encode("utf-8")
                        except:
                            self.buffer += message.decode(sys.getfilesystemencoding())

                def writelines(self, messages):
                    self.buffer += "\n".join(messages)

                def flush(self, *args):
                    pass

            sys.stderr = auxFile()
            sys.stdout = auxFile()
            import res.Scons.sconsFiles.SCons.Script
            res.Scons.sconsFiles.SCons.Script.main()

        except SystemExit as e:
            outBuffer = sys.stdout.file.buffer
            errBuffer = sys.stderr.file.buffer
            returnObject = {"returncode": e.code, "out": sys.stdout.file.buffer, "err": sys.stderr.file.buffer}
            revert_io()
            sys.stdout.write(outBuffer)
            sys.stderr.write(errBuffer)
            return returnObject

        except:
            log.exception("failed to execute Scons script")
        finally:
            revert_io()


def getMainApp():
    global __mainApp
    if __mainApp is None:
        __mainApp = MainApp()
    return __mainApp


def isTrayIconAvailable():
    return utils.isWindows() and QtGui.QSystemTrayIcon.isSystemTrayAvailable()
