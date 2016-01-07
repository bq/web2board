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
import urllib2
from urllib2 import HTTPError, URLError
import time
import threading
import signal
import ssl
from optparse import OptionParser
from wsgiref.simple_server import make_server

from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler
from wshubsapi.HubsInspector import HubsInspector

from libs.CompilerUploader import getCompilerUploader
from libs.LibraryUpdater import getLibUpdater
from libs.LoggingUtils import initLogging
from libs.PathsManager import *

log = initLogging(__name__)  # initialized in main
isAppRunning = False
w2bServer = ""


def handleSystemArguments():
    parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=9876, type='int', action="store", dest="port", help="port (9876)")
    parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
    parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
    parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert",
                      help="cert (./cert.pem)")
    parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
    parser.add_option("--test", default='none', type='string', action="store", dest="testing",
                      help="options: [none, unit, integration]")

    if sys.argv[1:]:
        log.debug('with arguments: {}'.format(sys.argv[1:]))
    options, args = parser.parse_args()
    testing = options.testing
    sys.argv[1:] = []

    if testing.lower() == "unit":
        from Test.runAllTests import runAllTests
        runAllTests()
        os._exit(1)

    log.info("init web2board with options: {}, and args: {}".format(options, args))

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
    libUpdater = getLibUpdater()
    try:
        libUpdater.downloadLibsIfNecessary()
    except (HTTPError, URLError):
        log.exception("unable to download libraries (might be a proxy problem)")
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

    class RedirectText(object):
        def __init__(self):
            self.out = ""

        def write(self, string):
            self.out += string

        def flush(self, *args):
            pass

        def get(self):
            aux = self.out
            self.out = ""
            return aux

    class MyForm(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, "Web2board", size=(900, 700))

            # Add a panel so it looks the correct on all platforms
            panel = wx.Panel(self, wx.ID_ANY)
            self.log = wx.TextCtrl(panel, wx.ID_ANY, size=(400, 300),
                                   style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

            self.timer = wx.Timer(self, 123456)
            self.Bind(wx.EVT_TIMER, self.onTimer)

            self.timer.Start(100)  # 1 second interval

            # Add widgets to a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.log, 1, wx.ALL | wx.EXPAND, 5)
            panel.SetSizer(sizer)

            # redirect text here
            self.redir = RedirectText()
            sys.stdout = self.redir

        def onTimer(self, *args):
            message = self.redir.get()
            self.log.WriteText(message)

    app = wx.App(False)
    frame = MyForm().Show()
    isAppRunning = True
    app.MainLoop()


def startConsoleViewerIfMac():
    if utils.isMac():
        consoleViewer()


def main():
    global w2bServer
    while utils.isMac() and not isAppRunning:
        time.sleep(0.1)
    PathsManager.moveInternalConfigToExternalIfNecessary()
    options = handleSystemArguments()
    PathsManager.logRelevantEnvironmentalPaths()
    compileUploader = getCompilerUploader()
    updateLibrariesIfNecessary()
    w2bServer = initializeServerAndCommunicationProtocol(options)

    log.info("listening...")
    w2bServer.serve_forever()


def startMain():
    if utils.isMac():
        t = threading.Thread(target=main)
        t.daemon = True
        t.start()
    else:
        main()


if __name__ == "__main__":
    try:
        startMain()


        def closeSigHandler(signal, frame):
            global w2bServer
            log.warning("closing server")
            w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)


        signal.signal(signal.SIGINT, closeSigHandler)

        startConsoleViewerIfMac()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
