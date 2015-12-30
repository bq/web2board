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

import glob
import os
import platform
from collections import defaultdict
from os.path import expanduser

from Compiler import Compiler
from Uploader import Uploader
from libs.PathConstants import *
from utils import BoardConfig, callAvrdude
from . import base


class ArduinoCompilerUploader:
    ALLOWED_BOARDS = ["uno", "bt328"]

    def __init__(self, pathToMain):

        self.pathToMain = MAIN_PATH
        self.pathToSketchbook = SKETCHBOOK_PATH

        self.pathToArduinoDir = os.path.join(pathToMain, 'res', 'arduino')
        self.uploader = Uploader(pathToMain)
        self.compiler = Compiler(pathToMain)
        self.boardSettings = defaultdict(BoardConfig)
        self.parseBoardSettings(RES_BOARDS_PATH)
        self.board = self.ALLOWED_BOARDS[1]
        self.port = None

    def setBoard(self, board):
        self.board = board
        return self.searchPort()

    def setPort(self, port=''):
        self.port = port

    def getPort(self):
        return self.port

    def getBoard(self):
        return self.board

    def getBoardBaudRate(self):
        return self.boardSettings[self.board].getBaudRate()

    def getBoardMCU(self):
        return self.boardSettings[self.board].getMCU()

    def getBoardFCPU(self):
        return self.boardSettings[self.board].getFCPU()

    def parseBoardSettings(self, path):
        file = open(path, 'r')
        # Split the file using the separator in boards.txt to separate the config of the different boards
        a = file.read().split('\n\n##############################################################\n\n')
        a.pop(0)  # Remove first element which is only a url
        for line in a:
            boardName = line.split('.')[0]
            boardConfig = line.split('\n')
            boardConfig = [i.split('=') for i in boardConfig]
            boardConfig.pop(0)  # Remove empty first element
            self.boardSettings[boardName] = BoardConfig(boardConfig)

    def getAvailablePorts(self):
        ports = utils.listSerialPorts(lambda x: "Bluetooth" not in x[0])
        return map(lambda x: x[0], ports)

    def searchPort(self):
        availablePorts = self.getAvailablePorts()
        if len(availablePorts) <= 0:
            return []
        ports = []
        for port in availablePorts:
            args = "-P " + port + " -p " + self.getBoardMCU() + " -b " + self.getBoardBaudRate() + " -c arduino"
            output, err = callAvrdude(args)
            if 'Device signature =' in output or 'Device signature =' in err:
                ports.append(port)
        if len(ports) == 1:
            self.setPort(ports[0])
        return ports

    def compile(self, code):
        return self.compiler.compile(code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook,
                                     self.getBoardMCU(), self.getBoardFCPU())

    def upload(self, code):
        compilationErrorReport = self.compile(code)
        if compilationErrorReport['status'] == 'OK':
            uploadErrorReport = self.uploader.upload(code, self.getPort(), self.getBoard(), self.getBoardMCU(),
                                                     self.getBoardBaudRate(), self.pathToMain, self.pathToSketchbook)
            return uploadErrorReport
        else:
            return compilationErrorReport
