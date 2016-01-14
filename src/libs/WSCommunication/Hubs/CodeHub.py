import logging
import os
import tempfile
from wshubsapi.Hub import Hub
from wshubsapi.HubsInspector import HubsInspector

from libs.PathsManager import PathsManager
from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.CompilerUploader import getCompilerUploader
from libs import utils

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class CodeHub(Hub):
    def __init__(self):
        super(CodeHub, self).__init__()
        self.compilerUploader = getCompilerUploader()

    def compile(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        _sender.isCompiling()
        return self.compilerUploader.compile(code)

    def upload(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        self.tryToTerminateSerialCommProcess()
        uploadPort = self.compilerUploader.getPort()
        _sender.isUploading(uploadPort)
        compileReport = self.compilerUploader.upload(code, uploadPort=uploadPort)
        if compileReport[0]:
            return True
        else:
            return self._constructUnsuccessfulReplay(compileReport[1]["err"])

    def uploadHex(self, hexText, _sender):
        """
        :type hexText: str
        :type _sender: ConnectedClientsGroup
        """
        self.tryToTerminateSerialCommProcess()
        with open(PathsManager.SETTINGS_PATH + os.sep + "factory.hex", 'w+b') as tmpHexFile:
            tmpHexFile.write(hexText)
        uploadPort = self.compilerUploader.getPort()
        _sender.isUploading(uploadPort)
        compileReport = self.compilerUploader.uploadAvrHex(tmpHexFile.name, uploadPort=uploadPort)
        if compileReport[0]:
            return True
        else:
            return self._constructUnsuccessfulReplay(compileReport[1]["err"])

    def __getSerialCommProcess(self):
        """
        :rtype: subprocess.Popen|None
        """
        return HubsInspector.getHubInstance(SerialMonitorHub).serialCommunicationProcess

    @staticmethod
    def tryToTerminateSerialCommProcess():
        from libs.Web2boardApp import getWebBoardApp

        if getWebBoardApp().isSerialMonitorRunning():
            try:
                getWebBoardApp().w2bGui.closeSerialMonitorApp()
            except:
                log.exception("unable to terminate process")
