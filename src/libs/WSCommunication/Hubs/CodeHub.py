import logging
import os

from wshubsapi.Hub import Hub, UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector

from libs.CompilerUploader import CompilerException, CompilerUploader
from libs.MainApp import getMainApp
from libs.PathsManager import PathsManager
from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class CodeHub(Hub):
    def __init__(self):
        super(CodeHub, self).__init__()

    def compile(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("Compiling from {}".format(_sender.ID))
        log.debug("Compiling code: {}".format(code.encode("utf-8")))
        _sender.isCompiling()
        compileReport = CompilerUploader.construct().compile(code)
        return self.__handleCompileReport(compileReport)

    def getHexData(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("getting hexData from {}".format(_sender.ID))
        log.debug("Compiling code: {}".format(code.encode("utf-8")))
        _sender.isCompiling()
        compileReport, hexData = CompilerUploader.construct().getHexData(code)
        return self.__handleCompileReport(compileReport), hexData

    def upload(self, code, board, _sender, port=None):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("Uploading for board {} from {}".format(board, _sender.ID))
        log.debug("Uploading code: {}".format(code.encode("utf-8")))
        uploadPort = self.__prepareUpload(board, _sender, port)
        if isinstance(uploadPort, UnsuccessfulReplay):
            return uploadPort

        compileReport = CompilerUploader.construct(board).upload(code, uploadPort=uploadPort)

        return self.__handleCompileReport(compileReport, uploadPort)

    def uploadHex(self, hexText, board, _sender, port=None):
        """
        :type hexText: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("upload Hex text for board {} from {}".format(board, _sender.ID))
        uploadPort = self.__prepareUpload(board, _sender, port)
        if isinstance(uploadPort, UnsuccessfulReplay):
            return uploadPort

        with open(PathsManager.RES_PATH + os.sep + "factory.hex", 'w+b') as tmpHexFile:
            tmpHexFile.write(hexText)

        relPath = os.path.relpath(tmpHexFile.name, os.getcwd())
        compileReport = CompilerUploader.construct(board).uploadAvrHex(relPath, uploadPort=uploadPort)
        return self.__handleCompileReport(compileReport, uploadPort)

    def uploadHexFile(self, hexFilePath, board, _sender, port=None):
        """
        :type hexFilePath: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("upload HexFile for board {} from {}".format(board, _sender[0].ID))
        with open(hexFilePath) as hexFile:
            hexText = hexFile.read()
        return self.uploadHex(hexText, board, _sender, port)

    @staticmethod
    def tryToTerminateSerialCommProcess():
        from libs.MainApp import getMainApp

        if getMainApp().isSerialMonitorRunning():
            try:
                log.info("Terminating serial monitor app")
                getMainApp().w2bGui.closeSerialMonitorApp()
            except:
                log.exception("unable to terminate process")

    def __handleCompileReport(self, compileReport, port=True):
        # second check to prevent problem with bluetooth
        if compileReport[0] or "Writing | #" in compileReport[1]["err"]:
            return port
        else:
            return self._constructUnsuccessfulReplay(compileReport[1]["err"])

    def __prepareUpload(self, board, _sender, uploadPort=None):
        if uploadPort is not None:
            _sender.isUploading(uploadPort)
            return uploadPort
        compileUploader = CompilerUploader.construct(board)
        serialHub = HubsInspector.getHubInstance(SerialMonitorHub)
        serialHub.closeAllConnections()
        self.tryToTerminateSerialCommProcess()
        uploadPort = getMainApp().w2bGui.getSelectedPort()
        if uploadPort is None:
            try:
                uploadPort = compileUploader.getPort()
            except CompilerException as e:
                return self._constructUnsuccessfulReplay(dict(title="BOARD_NOT_READY", stdErr=e.message))
        _sender.isUploading(uploadPort)
        return uploadPort
