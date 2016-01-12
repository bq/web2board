#!/usr/bin/env python
import os

import signal

from libs.Decorators.Asynchronous import asynchronous
from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager
from libs.SysTrayIcon.winSysTryIcon import SysTrayIcon
from libs.Web2boardApp import getMainApp

log = initLogging(__name__)  # initialized in main


@asynchronous()
def startsTrayIcon():
    iconPath = PathsManager.RES_PATH + os.sep + "Web2board.ico"
    hover_text = "Web2board application"
    def showWeb2board(sysTrayIcon):
        w2bApp = getMainApp()
        w2bApp.w2bGui.showApp()
    menu_options = (('Show app', iconPath, showWeb2board),)
    SysTrayIcon(iconPath, hover_text, menu_options, default_menu_index=1)


# Minimal self test. You'll need a bunch of ICO files in the current working
# directory in order for this to work...
if __name__ == '__main__':
    try:
        def closeSigHandler(signal, frame):
            log.warning("closing server")
            getMainApp().w2bServer.server_close()
            log.warning("server closed")
            os._exit(1)


        startsTrayIcon()
        app = getMainApp()

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
