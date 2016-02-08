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
import click

from Scripts.TestRunner import *
from libs import utils
from libs.LoggingUtils import initLogging
from libs.MainApp import getMainApp

log = initLogging(__name__)  # initialized in main
originalEcho = click.echo


def clickEchoForExecutable(message=None, file=None, nl=True, err=False, color=None):
    if not utils.areWeFrozen():
        originalEcho(message, file, nl, err, color)
    log.debug(message)

click.echo = clickEchoForExecutable

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
