import logging
import os

from wshubsapi.hub import Hub, UnsuccessfulReplay
from wshubsapi.hubs_inspector import HubsInspector

from libs.CompilerUploader import CompilerException, CompilerUploader
from libs.PathsManager import PathsManager
from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class CodeHub(Hub):
    def __init__(self):
        super(CodeHub, self).__init__()
        self.serial_hub = HubsInspector.get_hub_instance(SerialMonitorHub)
        """ :type : SerialMonitorHub"""

    def __handle_compile_report(self, report, port=True):
        # second check to prevent problem with bluetooth
        if report[0] or "Writing | #" in report[1]["err"]:
            return port
        else:
            return self._construct_unsuccessful_replay(report[1]["err"])

    def __prepare_upload(self, board, _sender, upload_port=None):
        if upload_port is not None:
            _sender.is_uploading(upload_port)
            return upload_port
        compile_uploader = CompilerUploader.construct(board)
        self.serial_hub.close_all_connections()
        try:
            upload_port = compile_uploader.get_port()
        except CompilerException as e:
            return self._construct_unsuccessful_replay(dict(title="BOARD_NOT_READY", stdErr=e.message))
        _sender.is_uploading(upload_port)
        return upload_port

    def compile(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("Compiling from {}".format(_sender.ID))
        log.debug("Compiling code: {}".format(code.encode("utf-8")))
        _sender.is_compiling()
        compile_report = CompilerUploader.construct().compile(code)
        return self.__handle_compile_report(compile_report)

    def get_hex_data(self, code, _sender):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("getting hexData from {}".format(_sender.ID))
        log.debug("Compiling code: {}".format(code.encode("utf-8")))
        _sender.is_compiling()
        compileReport, hexData = CompilerUploader.construct().get_hex_data(code)
        return self.__handle_compile_report(compileReport), hexData

    def upload(self, code, board, _sender, port=None):
        """
        :type code: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("Uploading for board {} from {}".format(board, _sender.ID))
        log.debug("Uploading code: {}".format(code.encode("utf-8")))
        upload_port = self.__prepare_upload(board, _sender, port)
        if isinstance(upload_port, UnsuccessfulReplay):
            return upload_port

        compile_report = CompilerUploader.construct(board).upload(code, upload_port=upload_port)

        return self.__handle_compile_report(compile_report, upload_port)

    def upload_hex(self, hex_text, board, _sender, port=None):
        """
        :type hex_text: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("upload Hex text for board {} from {}".format(board, _sender.ID))
        upload_port = self.__prepare_upload(board, _sender, port)
        if isinstance(upload_port, UnsuccessfulReplay):
            return upload_port

        with open(PathsManager.RES_PATH + os.sep + "factory.hex", 'w+b') as tmpHexFile:
            tmpHexFile.write(hex_text)

        rel_path = os.path.relpath(tmpHexFile.name, os.getcwd())
        compileReport = CompilerUploader.construct(board).upload_avr_hex(rel_path, upload_port=upload_port)
        return self.__handle_compile_report(compileReport, upload_port)

    def upload_hex_file(self, hex_file_path, board, _sender, port=None):
        """
        :type hex_file_path: str
        :type _sender: ConnectedClientsGroup
        """
        log.info("upload HexFile for board {} from {}".format(board, _sender[0].ID))
        with open(hex_file_path) as hexFile:
            hex_text = hexFile.read()
        return self.upload_hex(hex_text, board, _sender, port)
