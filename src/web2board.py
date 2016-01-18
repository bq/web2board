#!/usr/bin/env python

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
from libs.MainApp import getMainApp
import psutil

log = initLogging(__name__)  # initialized in main

if __name__ == "__main__":
    try:
        precess = []
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() in ("web2board.exe", "web2board", "web2board.app") and proc.pid != os.getpid():
                log.warning("killing a running web2board application")
                proc.kill()

        def closeSigHandler(signal, frame):
            log.warning("closing server")
            getMainApp().w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)

        app = getMainApp()

        signal.signal(signal.SIGINT, closeSigHandler)

        qtApp = app.startMain()
        sys.exit(qtApp.exec_())
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
