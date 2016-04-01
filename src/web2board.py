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

print(0)
import importlib
print(1)
import pprint
print(2)
import signal
print(3)
import click
print(4)
from wshubsapi.HubsInspector import HubsInspector

print(5)
from Scripts.TestRunner import *
print(6)
from libs.LoggingUtils import initLogging
print(7)
from libs.PathsManager import PathsManager

log = initLogging(__name__)  # initialized in main
originalEcho = click.echo
originalSEcho = click.secho

def getEchoFunction(original):
    def clickEchoForExecutable(message, *args, **kwargs):
        try:
            original(message, *args, **kwargs)
        except:
            log.debug(message)
    return clickEchoForExecutable


print(8)
click.echo = getEchoFunction(originalEcho)
print(9)
click.secho = getEchoFunction(originalSEcho)

def clickConfirm(message):
    print message
    return True

print(10)
print(10)
click.confirm = clickConfirm


def runSconsScript():
    pprint.pprint(sys.path)
    platformioPath = sys.argv.pop(-1)
    pathDiff = os.path.relpath(os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH), platformioPath)
    os.chdir(platformioPath)
    sys.path.extend([pathDiff + os.sep + 'sconsFiles'])
    execfile(pathDiff + os.sep + "sconsFiles" + os.sep + "scons.py")

if "-Q" in sys.argv:
    runSconsScript()

if __name__ == "__main__":
    print(11)
    qtApp = None
    try:
        print(12)
        importlib.import_module("libs.WSCommunication.Hubs")
        print(13)
        HubsInspector.inspectImplementedHubs()
        print(14)
        from libs.MainApp import getMainApp, forceQuit
        print(15)
        app = getMainApp()

        print(16)
        def closeSigHandler(signal, frame):
            try:
                log.warning("closing server")
                getMainApp().w2bServer.server_close()
                log.warning("server closed")
            except:
                log.warning("unable to close server")
            forceQuit()
            os._exit(1)


        print(17)
        signal.signal(signal.SIGINT, closeSigHandler)
        print(18)
        qtApp = app.startMain()
        print(19)
        sys.exit(qtApp.exec_())
    except SystemExit:
        pass
    except Exception as e:
        if log is None:
            print(20)
            raise e
        else:
            print(21)
            log.critical("critical exception", exc_info=1)
    print(22)
    if qtApp is not None:
        print(23)
        qtApp.quit()
    print(24)
    os._exit(1)
