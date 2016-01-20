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
import shutil

from Scripts.TestRunner import *
from libs import utils
from libs.LoggingUtils import initLogging
from libs.MainApp import getMainApp
from libs.PathsManager import PathsManager

log = initLogging(__name__)  # initialized in main

if __name__ == "__main__":
    try:
        utils.killProcess("web2boardLink")

        if PathsManager.MAIN_PATH == PathsManager.getCopyPathForUpdate() and len(sys.argv) > 1:
            print "updating process"
            print "killing original web2board"
            utils.killProcess("web2board")
            if os.path.exists(PathsManager.getOriginalPathForUpdate()):
                print "removing original files"
                shutil.rmtree(PathsManager.getOriginalPathForUpdate())
            print "extracting files"
            utils.extractZip(sys.argv[1], PathsManager.getOriginalPathForUpdate())
            sys.exit(1)


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
