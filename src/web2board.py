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
import pprint
import signal
import click
import os

from Scripts.TestRunner import *
from libs import utils
from libs.LoggingUtils import initLogging
from libs.MainApp import getMainApp
from libs.PathsManager import PathsManager

log = initLogging(__name__)  # initialized in main
originalEcho = click.echo
originalSEcho = click.secho


def clickEchoForExecutable(message=None, file=None, nl=True, err=False, color=None, *args, **kwargs):
    if not utils.areWeFrozen():
        originalEcho(message, file, nl, err, color)
    log.debug(message)


click.echo = clickEchoForExecutable
click.secho = clickEchoForExecutable


def runSconsScript():
    pprint.pprint(sys.path)
    platformioPath = sys.argv.pop(-1)
    pathDiff = os.path.relpath(os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH), platformioPath)
    print
    os.chdir(platformioPath)
    sys.path.extend([pathDiff + os.sep + 'sconsFiles'])
    execfile(pathDiff + os.sep + "sconsFiles" + os.sep + "scons.py")


if "-Q" in sys.argv:
    runSconsScript()

if __name__ == "__main__":
    try:
        utils.killProcess("web2board")


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
