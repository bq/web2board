import logging
import os
import platform
import subprocess
import sys
from wshubsapi.Hub import Hub

from libs.CompilerUploader import getCompilerUploader
from libs.PathConstants import MAIN_PATH

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class SerialMonitorHub(Hub):
    def __init__(self):
        super(SerialMonitorHub, self).__init__()
        self.compilerUploader = getCompilerUploader()
        self.serialCommunicationProcess = None
        """:type : subprocess.Popen """

    def startApp(self, args):
        # todo: could we just run serialMonitor in a thread?
        if platform.system() == 'Darwin':
            processArgs = ['/Applications/SerialMonitor.app/Contents/MacOS/SerialMonitor', args]
        else:
            processArgs = ['python', MAIN_PATH + os.sep + 'SerialMonitor.py', args]
        self.serialCommunicationProcess = subprocess.Popen(processArgs, shell=False)
        return True