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

import serial

log = logging.getLogger(__name__)


class SerialCommunication:
    def __init__(self, board=None, port=None):
        self.board = board
        self.port = port
        self.serial = None
        self.baudRate = None

    def setBoard(self, board):
        self.board = board

    def setPort(self, port=''):
        self.port = port

    def getPort(self):
        return self.port

    def getBoard(self):
        return self.board

    def setBaudrate(self, baudRate):
        self.baudRate = baudRate

    def initializeSerial(self, port=None, baudRate=None):
        self.port = port if port is not None else self.port
        self.baudRate = baudRate if baudRate is not None else self.baudRate

        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudRate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )

    # self.close()

    def open(self):
        self.serial.open()
        self.serial.isOpen()

    def close(self):
        self.serial.close()

    def write(self, data):
        self.serial.write(data)

    def read(self):
        out = ''
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)
        if out != '':
            return out
