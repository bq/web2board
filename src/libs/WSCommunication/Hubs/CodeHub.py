import logging

from wshubsapi.Hub import Hub
from wshubsapi.HubsInspector import HubsInspector

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.CompilerUploader import getCompilerUploader

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
        if self.__getSerialCommProcess() is not None:
            try:
                self.__getSerialCommProcess().terminate()
            except:
                log.exception("unable to terminate process")
        _sender.isUploading(self.compilerUploader.getPort())
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
