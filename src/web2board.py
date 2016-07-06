#!/usr/bin/env python

# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------#
#                                                                        #
# This file is part of the web2board project                             #
#                                                                        #
# Copyright (C) 2015 Mundo Reader S.L.                                   #
#                                                                        #
# Date: April - May 2015                                                 #
# Authors: Irene Sanz Nieto <irene.sanz@bq.com>,                         #
#          Sergio Morcuende <sergio.morcuende@bq.com>                    #
#                                                                        #
# -----------------------------------------------------------------------#

import importlib
import pprint
import signal
import click
from wshubsapi.hubs_inspector import HubsInspector

from Scripts.TestRunner import *
from libs.LoggingUtils import init_logging
from libs.PathsManager import PathsManager

log = init_logging(__name__)  # initialized in main
originalEcho = click.echo
originalSEcho = click.secho


def get_echo_function(original):
    def click_echo_for_executable(message, *args, **kwargs):
        try:
            original(message, *args, **kwargs)
        except:
            log.debug(message)
    return click_echo_for_executable


click.echo = get_echo_function(originalEcho)
click.secho = get_echo_function(originalSEcho)


def click_confirm(message):
    print message
    return True

click.confirm = click_confirm


def run_scons_script():
    pprint.pprint(sys.path)
    platformio_path = sys.argv.pop(-1)
    path_diff = os.path.relpath(os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH), platformio_path)
    os.chdir(platformio_path)
    sys.path.extend([path_diff + os.sep + 'sconsFiles'])
    execfile(path_diff + os.sep + "sconsFiles" + os.sep + "scons.py")

if "-Q" in sys.argv:
    run_scons_script()
    os._exit(1)

if "parallelCompile" == sys.argv[-1]:
    sys.argv.pop()
    import ParallelCompiler
    ParallelCompiler.run()
    sys.exit()

if __name__ == "__main__":
    try:
        importlib.import_module("libs.WSCommunication.Hubs")
        from libs.MainApp import force_quit, MainApp
        app = MainApp()

        def close_sig_handler(signal, frame):
            try:
                log.warning("closing server")
                app.w2b_server.server_close()
                log.warning("server closed")
            except:
                log.warning("unable to close server")
            force_quit()
        HubsInspector.inspect_implemented_hubs()

        signal.signal(signal.SIGINT, close_sig_handler)
        app.start_main()
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            raise e
        else:
            log.critical("critical exception", exc_info=1)

    os._exit(1)
