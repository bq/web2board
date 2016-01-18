import logging
import os
import tempfile
from wshubsapi.Hub import Hub, UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector

from libs.PathsManager import PathsManager
from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.CompilerUploader import getCompilerUploader, CompilerException
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
        compileReport = self.compilerUploader.compile(code)
        return self.__handleCompileReport(compileReport)


    def upload(self, code, board, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        uploadPort = self.__prepareUpload(board, _sender)
        if isinstance(uploadPort, UnsuccessfulReplay):
            return uploadPort

        compileReport = self.compilerUploader.upload(code, uploadPort=uploadPort)

        return self.__handleCompileReport(compileReport)

    def uploadHex(self, hexText, board, _sender):
        """
        :type hexText: str
        :type _sender: ConnectedClientsGroup
        """
        uploadPort = self.__prepareUpload(board, _sender)
        if isinstance(uploadPort, UnsuccessfulReplay):
            return uploadPort

        with open(PathsManager.SETTINGS_PATH + os.sep + "factory.hex", 'w+b') as tmpHexFile:
            tmpHexFile.write(hexText)

        compileReport = self.compilerUploader.uploadAvrHex(tmpHexFile.name, uploadPort=uploadPort)
        return self.__handleCompileReport(compileReport)

    @staticmethod
    def tryToTerminateSerialCommProcess():
        from libs.MainApp import getMainApp

        if getMainApp().isSerialMonitorRunning():
            try:
                getMainApp().w2bGui.closeSerialMonitorApp()
            except:
                log.exception("unable to terminate process")

    def __handleCompileReport(self, compileReport):
        if compileReport[0]:
            return True
        else:
            return self._constructUnsuccessfulReplay(compileReport[1]["err"])

    def __prepareUpload(self, board, _sender):
        self.compilerUploader.setBoard(board)
        self.tryToTerminateSerialCommProcess()
        try:
            uploadPort = self.compilerUploader.getPort()
        except CompilerException as e:
            return self._constructUnsuccessfulReplay(dict(title="BOARD_NOT_READY", stdErr=e.message))
        _sender.isUploading(uploadPort)

        return uploadPort

    def __getSerialCommProcess(self):
        """
        :rtype: subprocess.Popen|None
        """
        return HubsInspector.getHubInstance(SerialMonitorHub).serialCommunicationProcess
