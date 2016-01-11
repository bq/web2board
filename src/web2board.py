#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: April - May 2015                                                #
# Authors: Irene Sanz Nieto <irene.sanz@bq.com>,                        #
#          Sergio Morcuende <sergio.morcuende@bq.com>                   #
#                                                                       #
# -----------------------------------------------------------------------#
import importlib
import os
import signal
import ssl
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

from libs import utils
from libs.LoggingUtils import initLogging
from Scripts.TestRunner import *
from Scripts import afterInstallScript
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater

log = initLogging(__name__)  # initialized in main
isAppRunning = False
w2bServer = ""


def handleSystemArguments():
    parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=9876, type='int', action="store", dest="port", help="port (9876)")
    parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
    parser.add_option("--test", default='none', type='string', action="store", dest="testing",
                      help="options: [none, unit, integration, all]")
    parser.add_option("--afterInstall", default=False, action="store_true", dest="afterInstall",
                      help="setup packages and folder structure")

    options, args = parser.parse_args()
    log.info("init web2board with options: {}, and args: {}".format(options, args))

    if options.afterInstall:
        afterInstallScript.run()
        log.warning("exiting program...")
        os._exit(1)

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


def initializeServerAndCommunicationProtocol(options):
    global w2bServer
    importlib.import_module("libs.WSCommunication.Hubs")
    HubsInspector.inspectImplementedHubs()
    # do not call this line in executable
    if not utils.areWeFrozen():
        HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
    w2bServer = make_server(options.host, options.port, server_class=WSGIServer,
                            handler_class=WebSocketWSGIRequestHandler,
                            app=WebSocketWSGIApplication(handler_cls=ConnectionHandler))
    w2bServer.initialize_websockets_manager()
    return w2bServer


def updateLibrariesIfNecessary():
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
        updateLibrariesIfNecessary()
    except OSError:
        log.exception("unable to copy libraries files, there could be a permissions problem.")


def consoleViewer():
    global isAppRunning
    import sys
    import wx
    from frames.Web2boardWindow import Web2boardWindow

    app = wx.App(False)
    w2bgui = Web2boardWindow(None)
    w2bgui.Show()
    w2bgui.Raise()
    isAppRunning = True
    app.MainLoop()


def startConsoleViewerIfMac():
    if utils.isMac() or True:
        consoleViewer()


def main():
    global w2bServer
    while (utils.isMac() or True) and not isAppRunning:
        time.sleep(0.1)
    PathsManager.moveInternalConfigToExternalIfNecessary()
    options = handleSystemArguments()
    PathsManager.logRelevantEnvironmentalPaths()
    updateLibrariesIfNecessary()
    w2bServer = initializeServerAndCommunicationProtocol(options)

    log.info("listening...")
    w2bServer.serve_forever()


def startMain():
    if utils.isMac() or True:
        t = threading.Thread(target=main)
        t.daemon = True
        t.start()
    else:
        main()


if __name__ == "__main__":
    try:
        def closeSigHandler(signal, frame):
            global w2bServer
            log.warning("closing server")
            w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)


        signal.signal(signal.SIGINT, closeSigHandler)

        startMain()

        startConsoleViewerIfMac()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
