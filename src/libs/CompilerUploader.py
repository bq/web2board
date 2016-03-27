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
import random
import subprocess
from datetime import timedelta, datetime

import sys
from threading import Lock

import time

from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.Synchronized import synchronized
from libs.PathsManager import PathsManager as pm
from platformio.platformioUtils import run as platformioRun
from platformio import exception, util
from platformio.util import get_boards
from libs import utils

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
    __globalCompilerUploaderHolder = {}
    workSpaceTokens = []
    DEFAULT_BOARD = "bt328"
    threadLock = Lock()

    def __init__(self, board=DEFAULT_BOARD):
        self.lastPortUsed = None
        self.board = board  # we use the board name as the environment (check platformio.ini)
        self._checkBoardConfiguration()

    def __constructWorkSpace(self, code, token):
        if isinstance(code, unicode):
            code = code.encode("utf-8")
        workSpacePath = pm.PLATFORMIO_WORKSPACE_PATH.format(token)
        if not os.path.exists(workSpacePath):
            utils.copytree(pm.PLATFORMIO_WORKSPACE_SKELETON, workSpacePath)
        mainInoPath = os.path.join(workSpacePath, "src")
        if not os.path.exists(mainInoPath):
            os.makedirs(mainInoPath)
        with open(os.path.join(mainInoPath, "main.ino"), 'w') as mainCppFile:
            mainCppFile.write(code)
        return workSpacePath

    def __getHexString(self, workSpacePath, board):
        hexPath = os.path.join(workSpacePath, ".pioenvs", board, "firmware.hex")
        if os.path.exists(hexPath):
            with open(hexPath) as hexFile:
                return hexFile.read()
        else:
            return None

    def _getIniConfig(self, environment):
        """
        :type environment: str
            """
        with util.cd(pm.PLATFORMIO_WORKSPACE_SKELETON):
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
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude.exe')
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf')
        elif utils.isMac():
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude')
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf')
        elif utils.isLinux():
            avrExePath = os.path.join(pm.RES_PATH, 'avrdude64' if utils.is64bits() else "avrdude")
            avrConfigPath = os.path.join(pm.RES_PATH, 'avrdude.conf' if utils.is64bits() else "avrdude32.conf")
        else:
            raise Exception("Platform not supported")

        os.chmod(avrExePath, int("755", 8)) # force to have executable rights in avrdude

        avrExePath = os.path.normpath(os.path.relpath(avrExePath, os.getcwd()))
        avrConfigPath = os.path.normpath(os.path.relpath(avrConfigPath, os.getcwd()))

        cmd = [avrExePath] + ["-C"] + [avrConfigPath] + args.split(" ")
        log.debug("Command executed: {}".format(cmd))
        p = subprocess.Popen(cmd, shell=utils.isWindows(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=(not utils.isWindows()))
        output = p.stdout.read()
        err = p.stderr.read()
        log.debug(output)
        log.debug(err)
        return output, err

    @asynchronous()
    def _checkPort(self, port, mcu, baudRate):
        try:
            log.debug("Checking port: {}".format(port))
            args = "-P " + port + " -p " + mcu + " -b " + str(baudRate) + " -c arduino"
            output, err = self._callAvrdude(args)
            log.debug("{2}: {0}, {1}".format(output, err, port))
            return 'Device signature =' in output or 'Device signature =' in err
        except:
            log.debug("Error searching port: {}".format(port), exc_info=1)
            return False

    def _run(self, code, upload=False, uploadPort=None, getHexString=False):
        token = self._getAvailableToken()
        try:
            self._checkBoardConfiguration()
            target = ("upload",) if upload else ()
            uploadPort = self.getPort() if upload and uploadPort is None else uploadPort

            workSpacePath = self.__constructWorkSpace(code, token)

            runResult = platformioRun(target=target, environment=(self.board,),
                                 project_dir=workSpacePath, upload_port=uploadPort)[0]
            if getHexString:
                hexResult = self.__getHexString(workSpacePath, self.board) if runResult[0] else None
                return runResult, hexResult
            return runResult
        finally:
            self._removeToken(token)

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
            return None
        log.info("Found available ports: {}".format(availablePorts))
        portResultHashMap = {}
        for port in availablePorts:
            portResultHashMap[port] = self._checkPort(port, mcu, baudRate)

        watchdog = datetime.now()
        while datetime.now() - watchdog < timedelta(seconds=30) and len(portResultHashMap) > 0:
            for port, resultObject in portResultHashMap.items():
                if resultObject.isDone():
                    portResultHashMap.pop(port)
                if resultObject.isDone() and resultObject.get():
                    log.info("Found board port: {}".format(port))
                    self.lastPortUsed = port
                    return port
        return None

    def _getAvailableToken(self):
        with self.threadLock:
            for i in range(5):
                if i not in self.workSpaceTokens:
                    self.workSpaceTokens.append(i)
                    return i
        time.sleep(0.2)
        return self._getAvailableToken()

    def _removeToken(self, token):
        self.workSpaceTokens.remove(token)

    def getAvailablePorts(self):
        portsToUpload = utils.listSerialPorts(lambda x: x[2] != "n/a")
        availablePorts = map(lambda x: x[0], portsToUpload)
        return sorted(availablePorts, cmp=lambda x, y: -1 if x == self.lastPortUsed else 1)

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

    def getHexData(self, code):
        return self._run(code, upload=False, getHexString=True)

    def upload(self, code, uploadPort=None):
        return self._run(code, upload=True, uploadPort=uploadPort)

    def uploadAvrHex(self, hexFilePath, uploadPort=None):
        self._checkBoardConfiguration()
        options = self._getIniConfig(self.board)
        port = uploadPort if uploadPort is not None else self.getPort()
        mcu = options["boardData"]["build"]["mcu"]
        baudRate = str(options["boardData"]["upload"]["speed"])
        args = "-V -P " + port + " -p " + mcu + " -b " + baudRate + " -c arduino -D -U flash:w:" + hexFilePath + ":i"
        output, err = self._callAvrdude(args)
        okText = "bytes of flash written"
        resultOk = okText in output or okText in err
        return resultOk, {"out": output, "err": err}

    @classmethod
    def construct(cls, board=DEFAULT_BOARD):
        """
        :param board: board mcu string
        :rtype: CompilerUploader
        """
        if board not in cls.__globalCompilerUploaderHolder:
            cls.__globalCompilerUploaderHolder[board] = CompilerUploader(board)
        return cls.__globalCompilerUploaderHolder[board]

