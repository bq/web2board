#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: April - May 2015                                                #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
# -----------------------------------------------------------------------#
import logging
import os
import subprocess

from datetime import timedelta, datetime

from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager as pm
from platformio.platformioUtils import run as platformioRun
from platformio import exception, util
from platformio.util import get_boards
from libs import utils

log = logging.getLogger(__name__)
__globalCompilerUploader = None

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
    def __init__(self):
        self.board = 'uno'  # we use the board name as the environment (check platformio.ini)

    def _getIniConfig(self, environment):
        """
        :type environment: str
            """
        with util.cd(pm.SETTINGS_PLATFORMIO_PATH):
            config = util.get_project_config()

            if not config.sections():
                raise exception.ProjectEnvsNotAvailable()

            known = set([s[4:] for s in config.sections()
                         if s.startswith("env:")])
            unknown = set((environment,)) - known
            if unknown:
                return None

            for section in config.sections():
                envName = section[4:]
                if environment and envName and envName == environment:
                    iniConfig = {k: v for k, v in config.items(section)}
                    iniConfig["boardData"] = get_boards(iniConfig["board"])
                    return iniConfig

    def _callAvrdude(self, args):
        if utils.isWindows():
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude.exe ')
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf ')
        elif utils.isMac():
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude ')
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf ')
        elif utils.isLinux():
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude64 ' if utils.is64bits() else "avrdude")
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf ')
        else:
            raise Exception("Platform not supported")

        cmd = avrExePath + "-C " + avrConfigPath + args
        log.debug("Command executed: {}".format(cmd))
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=(not utils.isWindows()))
        output = p.stdout.read()
        err = p.stderr.read()
        log.debug(output)
        log.debug(err)
        return output, err

    @asynchronous()
    def _checkPort(self, port, mcu, baudRate):
        log.debug("Checking port: {}".format(port))
        args = "-P " + port + " -p " + mcu + " -b " + str(baudRate) + " -c arduino"
        output, err = self._callAvrdude(args)
        return 'Device signature =' in output or 'Device signature =' in err

    def _run(self, code, upload=False, uploadPort=None):
        self._checkBoardConfiguration()
        target = ("upload",) if upload else ()
        uploadPort = self.getPort() if upload and uploadPort is None else uploadPort

        code = '#include "Arduino.h"\n' + code  # todo do this only in Arduino frameworks

        with open(os.path.join(pm.SETTINGS_PLATFORMIO_PATH, "src", "main.cpp"), 'w') as mainCppFile:
            mainCppFile.write(code)

        return platformioRun(target=target, environment=(self.board,), project_dir=pm.SETTINGS_PLATFORMIO_PATH,
                             upload_port=uploadPort)[0]

    def _checkBoardConfiguration(self):
        if self.board is None:
            raise CompilerException(ERROR_BOARD_NOT_SET)
        if self._getIniConfig(self.board) is None:
            raise CompilerException(ERROR_BOARD_NOT_SUPPORTED, self.board)

    def _searchBoardPort(self):
        self._checkBoardConfiguration()
        options = self._getIniConfig(self.board)
        mcu = options["boardData"]["build"]["mcu"]
        baudRate = options["boardData"]["upload"]["speed"]
        availablePorts = self.getAvailablePorts()
        if len(availablePorts) <= 0:
            return []
        log.info("Found available ports: {}".format(availablePorts))
        portResultHashMap = {}
        for port in availablePorts:
            portResultHashMap[port] = self._checkPort(port, mcu, baudRate)

        watchdog = datetime.now()
        while datetime.now() - watchdog < timedelta(seconds=4):
            for port, resultObject in portResultHashMap.items():
                if resultObject.isDone() and resultObject.get():
                    log.info("Found board port: {}".format(port))
                    return port

    def getAvailablePorts(self):
        portsToUpload = utils.listSerialPorts(lambda x: "Bluetooth" not in x[0])
        availablePorts = map(lambda x: x[0], portsToUpload)
        return availablePorts

    def getPort(self):
        self._checkBoardConfiguration()
        portToUpload = self._searchBoardPort()
        if portToUpload is None:
            raise CompilerException(ERROR_NO_PORT_FOUND, self.board)

        return portToUpload

    def setBoard(self, board):
        self.board = board
        self._checkBoardConfiguration()

    def compile(self, code):
        return self._run(code, upload=False)

    def upload(self, code, uploadPort=None):
        return self._run(code, upload=True, uploadPort=uploadPort)

    def uploadAvrHex(self, hexFilePath, uploadPort=None):
        self._checkBoardConfiguration()
        options = self._getIniConfig(self.board)
        port = uploadPort if uploadPort is not None else self.getPort()
        mcu = options["boardData"]["build"]["mcu"]
        baudRate = str(options["boardData"]["upload"]["speed"])
        args = "-V " + " -P " + port + " -p " + mcu + " -b " + baudRate + " -c arduino -D -U flash:w:" + hexFilePath + ":i"
        output, err = self._callAvrdude(args)
        okText = "bytes of flash written"
        resultOk = okText in output or okText in err
        return resultOk, {"out": output, "err": err}


def getCompilerUploader():
    """
    :rtype: CompilerUploader
    """
    global __globalCompilerUploader
    if __globalCompilerUploader is None:
        __globalCompilerUploader = CompilerUploader()
    return __globalCompilerUploader
