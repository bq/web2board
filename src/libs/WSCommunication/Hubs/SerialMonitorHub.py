import logging
import os
import platform
import subprocess
from wshubsapi.Hub import Hub

from libs import utils
from libs.CompilerUploader import getCompilerUploader
from libs.Packagers.Packager import Packager
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

    def startApp(self, port = None):
        processArgs = self.__getProcessArgsToStartSerialMonitor()
        if port is not None:
            processArgs.append(port)
        self.serialCommunicationProcess = subprocess.Popen(processArgs, shell=False)
        return True

    def __findSerialMonitorPath(self):
        if utils.areWeFrozen():
            packager = Packager.constructCurrentPlatformPackager()
            return os.path.join(PathsManager.EXECUTABLE_PATH, packager.serialMonitorExecutableName)
        else:
            return os.path.join(PathsManager.EXECUTABLE_PATH, "SerialMonitor.py")

    def __getProcessArgsToStartSerialMonitor(self):
        if utils.areWeFrozen():
            return [self.__findSerialMonitorPath()]
        else:
            return ["python", self.__findSerialMonitorPath()]