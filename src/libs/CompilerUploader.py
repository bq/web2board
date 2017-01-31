#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import subprocess
from datetime import timedelta, datetime
from UserList import UserList as _UserList
from UserString import UserString as _UserString
import UserList
import UserString

from libs import utils
from libs.Decorators.Asynchronous import asynchronous
from libs.ErrorParser import format_compile_result
from libs.PathsManager import PathsManager as pm
from platformio import exception, util
from platformio.platformioUtils import run as platformio_run
from platformio.util import get_boards
import re

log = logging.getLogger(__name__)

ERROR_BOARD_NOT_SET = {"code": 0, "message": "Necessary to define board before to run/compile"}
ERROR_BOARD_NOT_SUPPORTED = {"code": 1, "message": "Board: {0} not Supported"}
ERROR_NO_PORT_FOUND = {"code": 2, "message": "No port found, check the board: \"{0}\" is connected"}
ERROR_MULTIPLE_BOARDS_CONNECTED = {"code": 3,
                                   "message": "More than one connected board was found. You should only have one board connected"}


class CompilerException(Exception):
    def __init__(self, error, *args):
        self.code = error["code"]
        self.message = error["message"].format(*args)
        super(CompilerException, self).__init__(self.message)


##
# Class CompilerUploader, created to support different compilers & uploaders
#
class CompilerUploader:
    __global_compiler_uploader_holder = {}
    DEFAULT_BOARD = "bt328"

    def __init__(self, board=DEFAULT_BOARD):
        self.lastPortUsed = None
        self.board = board  # we use the board name as the environment (check platformio.ini)
        self.build_options = self._get_build_options(self.board)

    @staticmethod
    def _get_build_options(board):
        """
        :type board: str
            """
        with util.cd(pm.PLATFORMIO_WORKSPACE_PATH):
            config = util.get_project_config()

            if not config.sections():
                raise exception.ProjectEnvsNotAvailable()

            known = set([s[4:] for s in config.sections()
                         if s.startswith("env:")])
            unknown = set((board,)) - known
            if unknown:
                return None

            for section in config.sections():
                envName = section[4:]
                if board and envName and envName == board:
                    build_options = {k: v for k, v in config.items(section)}
                    build_options["boardData"] = get_boards(build_options["board"])
                    return build_options

            raise CompilerException(ERROR_BOARD_NOT_SUPPORTED, board)

    @staticmethod
    def _call_avrdude(args):
        if utils.is_windows():
            avr_exe_path = os.path.join(pm.RES_PATH, 'avrdude.exe')
            avr_config_path = os.path.join(pm.RES_PATH, 'avrdude.conf')
        elif utils.is_mac():
            avr_exe_path = os.path.join(pm.RES_PATH, 'avrdude')
            avr_config_path = os.path.join(pm.RES_PATH, 'avrdude.conf')
        elif utils.is_linux():
            avr_exe_path = os.path.join(pm.RES_PATH, 'avrdude64' if utils.is64bits() else "avrdude")
            avr_config_path = os.path.join(pm.RES_PATH, 'avrdude.conf' if utils.is64bits() else "avrdude32.conf")
        else:
            raise Exception("Platform not supported")

        os.chmod(avr_exe_path, int("755", 8))  # force to have executable rights in avrdude

        avr_exe_path = os.path.normpath(os.path.relpath(avr_exe_path, os.getcwd()))
        avr_config_path = os.path.normpath(os.path.relpath(avr_config_path, os.getcwd()))

        cmd = [avr_exe_path] + ["-C"] + [avr_config_path] + args.split(" ")
        log.debug("Command executed: {}".format(cmd))
        p = subprocess.Popen(cmd, shell=utils.is_windows(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=(not utils.is_windows()))
        output = p.stdout.read()
        err = p.stderr.read()
        log.debug(output)
        log.debug(err)
        return output, err

    @asynchronous()
    def _check_port(self, port, mcu, baud_rate, protocol="arduino"):
        try:
            log.debug("Checking port: {}".format(port))
            args = "-P " + port + " -p " + mcu + " -b " + str(baud_rate) + " -c " + protocol
            output, err = self._call_avrdude(args)
            log.debug("{2}: {0}, {1}".format(output, err, port))
            return 'Device signature =' in output or 'Device signature =' in err
        except:
            log.debug("Error searching port: {}".format(port), exc_info=1)
            return False

    def _run(self, code, upload=False, upload_port=None, get_hex_string=False):
        target = ("upload",) if upload else ()
        upload_port = self.get_port() if upload and upload_port is None else upload_port

        if isinstance(code, unicode):
            code = code.encode("utf-8")

        main_ino_path = os.path.join(pm.PLATFORMIO_WORKSPACE_PATH, "src")
        if not os.path.exists(main_ino_path):
            os.makedirs(main_ino_path)
        with open(os.path.join(main_ino_path, "main.ino"), 'w') as mainCppFile:
            mainCppFile.write(code)

        run_result = platformio_run(target=target, environment=(self.board,),
                                    project_dir=pm.PLATFORMIO_WORKSPACE_PATH, upload_port=upload_port)[0]
        if get_hex_string:
            raise NotImplementedError()
            # hexResult = self.__getHexString(pm.PLATFORMIO_WORKSPACE_PATH, self.board) if runResult[0] else None
            # return runResult, hexResult
        return format_compile_result(run_result)

    def _search_board_port(self):
        mcu = self.build_options["boardData"]["build"]["mcu"]
        protocol = self.build_options["boardData"]["upload"]["protocol"]
        baud_rate = self.build_options["boardData"]["upload"]["speed"]
        available_ports = self.get_available_ports()
        if len(available_ports) <= 0:
            return None
        log.info("Found available ports: {}".format(available_ports))
        port_futures_dict = {}
        for port in available_ports:
            port_futures_dict[port] = self._check_port(port, mcu, baud_rate, protocol)

        watchdog = datetime.now()
        while datetime.now() - watchdog < timedelta(seconds=30) and len(port_futures_dict) > 0:
            for port, future in port_futures_dict.items():
                if future.done():
                    port_futures_dict.pop(port)
                    if future.result():
                        log.info("Found board port: {}".format(port))
                        self.lastPortUsed = port
                        return port
        return None

    def get_available_ports(self):
        ports_to_upload = utils.list_serial_ports(lambda x: x[2] != "n/a")
        available_ports = map(lambda x: x[0], ports_to_upload)
        return sorted(available_ports, cmp=lambda x, y: -1 if x == self.lastPortUsed else 1)

    def get_port(self):
        port_to_upload = self._search_board_port()
        if port_to_upload is None:
            raise CompilerException(ERROR_NO_PORT_FOUND, self.board)

        return port_to_upload

    def set_board(self, board):
        self.board = board
        self._get_build_options(board)

    def compile(self, code):
        return self._run(code, upload=False)

    def get_hex_data(self, code):
        return self._run(code, upload=False, get_hex_string=True)

    def upload(self, code, upload_port=None):
        return self._run(code, upload=True, upload_port=upload_port)

    def upload_avr_hex(self, hex_file_path, upload_port=None):
        port = upload_port if upload_port is not None else self.get_port()
        mcu = self.build_options["boardData"]["build"]["mcu"]
        protocol = self.build_options["boardData"]["upload"]["protocol"]
        baud_rate = str(self.build_options["boardData"]["upload"]["speed"])
        args = "-V -P " + port + " -p " + mcu + " -b " + baud_rate + " -c " + protocol + " -D -U flash:w:" + hex_file_path + ":i"
        output, err = self._call_avrdude(args)
        ok_text = "bytes of flash written"
        result_ok = ok_text in output or ok_text in err
        return result_ok, {"out": output, "err": err}

    @classmethod
    def construct(cls, board=DEFAULT_BOARD):
        """
        :param board: board mcu string
        :rtype: CompilerUploader
        """
        if board not in cls.__global_compiler_uploader_holder:
            cls.__global_compiler_uploader_holder[board] = CompilerUploader(board)
        return cls.__global_compiler_uploader_holder[board]
