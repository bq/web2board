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
import urllib2
from urllib2 import HTTPError, URLError

import time

import libs.LoggingUtils  # necessary for package, do not remove!
import libs.WSCommunication.Hubs  # necessary for package, do not remove!

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


def handleSystemArguments():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
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
    HubsInspector.inspectImplementedHubs()
    # do not call this line in executable
    if not utils.areWeFrozen():
        HubsInspector.constructJSFile(path="libs/WSCommunication/Clients")
    server = make_server(options.host, options.port, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=ConnectionHandler))
    server.initialize_websockets_manager()
    return server


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
        def __init__(self, aWxTextCtrl):
            self.out = aWxTextCtrl

        def write(self, string):
            self.out.WriteText(string)

        def flush(self, *args):
            pass

    class MyForm(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, "Web2board", size=(900, 700))

            # Add a panel so it looks the correct on all platforms
            panel = wx.Panel(self, wx.ID_ANY)
            log = wx.TextCtrl(panel, wx.ID_ANY, size=(400, 300),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

            # Add widgets to a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
            panel.SetSizer(sizer)

            # redirect text here
            redir = RedirectText(log)
            sys.stdout = redir

    app = wx.App(False)
    frame = MyForm().Show()
    isAppRunning = True
    app.MainLoop()


def startConsoleViewerIfMac():
    if utils.isMac() or False:
        t = threading.Thread(target=consoleViewer)
        t.daemon = True
        t.start()
        while not isAppRunning:
            time.sleep(0.1)


def main():
    startConsoleViewerIfMac()
    PathsManager.moveInternalConfigToExternalIfNecessary()
    options = handleSystemArguments()
    PathsManager.logRelevantEnvironmentalPaths()
    compileUploader = getCompilerUploader()
    updateLibrariesIfNecessary()
    server = initializeServerAndCommunicationProtocol(options)

    def closeSigHandler(signal, frame):
        log.warning("closing server")
        server.server_close()
        log.warning("server closed")
        os._exit(1)

    signal.signal(signal.SIGINT, closeSigHandler)

    log.info("listening...")
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
