import logging

from wshubsapi.Hub import Hub
from wshubsapi.HubsInspector import HubsInspector

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
        self.__tryToTerminateSerialCommProcess()

        _sender.isUploading(self.compilerUploader.getPort())
        compileReport = self.compilerUploader.upload(code)
        if compileReport["status"] == "OK":
            return True
        else:
            return self._constructUnsuccessfulReplay(compileReport["error"])

    def uploadHexUrl(self, hexFileUrl, _sender):
        """
        :type hexFileUrl: str
        :type _sender: ConnectedClientsGroup
        """
        self.__tryToTerminateSerialCommProcess()

        _sender.isUploading(self.compilerUploader.getPort())
        hexFilePath = utils.downloadFile(hexFileUrl)
        compileReport = self.compilerUploader.upload(code)
        if compileReport["status"] == "OK":
            return True
        else:
            return self._constructUnsuccessfulReplay(compileReport["error"])

    def __getSerialCommProcess(self):
        """
        :rtype: subprocess.Popen|None
        """
        return HubsInspector.getHubInstance(SerialMonitorHub).serialCommunicationProcess

    def __tryToTerminateSerialCommProcess(self):
        from libs.Web2boardApp import getMainApp

        if getMainApp().isSerialMonitorRunning():
            try:
                getMainApp().w2bGui.closeSerialMonitorApp()
            except:
                log.exception("unable to terminate process")
