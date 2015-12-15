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
import logging
import os
import signal
import ssl
from optparse import OptionParser
from wsgiref.simple_server import make_server

from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler
from wshubsapi.HubsInspector import HubsInspector

from libs.CompilerUploader import getCompilerUploader

# from libs.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

compilerUploader = getCompilerUploader()


if __name__ == "__main__":
    importlib.import_module("libs.WSCommunication.Hubs")
    HubsInspector.inspectImplementedHubs()

    # do not call this function in executable
    # HubsInspector.constructPythonFile("libs/WSCommunication/Hubs/Clients")
    HubsInspector.constructJSFile("libs/WSCommunication/Hubs/Clients")

    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=9876, type='int', action="store", dest="port", help="port (9876)")
    parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
    parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
    parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert",
                      help="cert (./cert.pem)")
    parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")

    (options, args) = parser.parse_args()
    log.debug("init web2board with options: {}, and args: {}".format(options, args))

    server = make_server(options.host, options.port, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=ConnectionHandler))
    server.initialize_websockets_manager()


    def close_sig_handler(signal, frame):
        server.server_close()
        os._exit(1)


    signal.signal(signal.SIGINT, close_sig_handler)

    log.debug("starting...")
    target = server.serve_forever()
