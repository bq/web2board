import logging
import multiprocessing
import threading
import wx

import time
from wshubsapi.Hub import Hub
from SerialMonitor import SerialMonitorUI

from libs.CompilerUploader import getCompilerUploader

log = logging.getLogger(__name__)


class SerialMonitorHubException(Exception):
    pass


class RunAppThread(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        super(RunAppThread, self).__init__(*args, **kwargs)
        self.app = None
        self.serialMonitor = None
        self.isRunning = False
        self.stopChecker = threading.Thread(target=self)
        self.event = multiprocessing.Event()

    def run(self):
        self.stopChecker.start()
        self.app = wx.App()
        self.serialMonitor = SerialMonitorUI(None, '/dev/ttyACM0')
        self.isRunning = True
        self.serialMonitor.Show()
        self.app.MainLoop()

    def stop(self):
        self.event.set()
        # self.app.ExitMainLoop()
        # wx.WakeUpMainThread()

    def checkStop(self):
        while not self.event.is_set():
            time.sleep(0.1)
        self.isRunning = False
        self.serialMonitor.close()


class SerialMonitorHub(Hub):
    def __init__(self):
        super(SerialMonitorHub, self).__init__()
        self.compilerUploader = getCompilerUploader()
        self.serialCommunicationThread = RunAppThread()

    def startApp(self, args):
        if not self.__isGuiRunning():
            self.serialCommunicationThread = RunAppThread()
            self.serialCommunicationThread.start()
        else:
            raise SerialMonitorHubException("Monitor already running")
        return True

    def __isGuiRunning(self):
        return self.serialCommunicationThread.isRunning
