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

import serial


class SerialCommunication:
    def __init__(self, board=None, port=None):
        self.board = board
        self.port = port

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

    def initializeSerial(self, port, baudRate):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudRate,
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
