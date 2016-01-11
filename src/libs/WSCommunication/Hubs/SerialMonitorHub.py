import logging
import os

from wshubsapi.Hub import Hub

from libs.CompilerUploader import getCompilerUploader
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class SerialMonitorHub(Hub):
    SERIAL_MONITOR_PATH = os.path.join(PathsManager.EXECUTABLE_PATH, "SerialMonitor")

    def __init__(self):
        super(SerialMonitorHub, self).__init__()
        self.compilerUploader = getCompilerUploader()
        self.serialCommunicationProcess = None
        """:type : subprocess.Popen """

    def startApp(self, port=None):
        from libs.Web2boardApp import getMainApp
        mainApp = getMainApp()
        mainApp.w2bGui.startSerialMonitorApp(port)
        return True