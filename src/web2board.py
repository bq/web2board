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
import signal

from Scripts.TestRunner import *
from libs.LoggingUtils import initLogging
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Updaters.Updater import VersionInfo
from libs.Web2boardApp import getWebBoardApp

log = initLogging(__name__)  # initialized in main

if __name__ == "__main__":
    try:


        def closeSigHandler(signal, frame):
            log.warning("closing server")
            getWebBoardApp().w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)


        app = getWebBoardApp()

        signal.signal(signal.SIGINT, closeSigHandler)

        wxApp = app.startMain()
        app.w2bGui.Show()

        wxApp.MainLoop()

        # app.startConsoleViewer()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
