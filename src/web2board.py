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
import zipfile
from datetime import datetime

from Scripts.TestRunner import *
from libs.Decorators.Asynchronous import asynchronous
from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Web2boardApp import getMainApp
from libs import utils

log = initLogging(__name__)  # initialized in main

@asynchronous()
def extractSconsFiles():
    if utils.areWeFrozen():
        log.debug("extacting scons files")
        before = datetime.now()
        with zipfile.ZipFile(PathsManager.RES_SCONS_ZIP_PATH, "r") as z:
            z.extractall(PathsManager.MAIN_PATH)
        log.debug("successfully extracted scons files in: {} ms".format((datetime.now() - before).microseconds/1000))

if __name__ == "__main__":
    try:
        extractSconsFiles()


        def closeSigHandler(signal, frame):
            log.warning("closing server")
            getMainApp().w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)


        app = getMainApp()

        signal.signal(signal.SIGINT, closeSigHandler)

        app.startMain()

        # app.startConsoleViewer()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)
    os._exit(1)
