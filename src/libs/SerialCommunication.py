#!/usr/bin/python

import serial
import os
from subprocess import call
import platform
import glob
from time import sleep
import binascii
import math
import sys
from collections import defaultdict
import subprocess


class SerialCommunication:
	def __init__(self, board=None, port=None):
		self.board = board
		self.port = port

	def setBoard (self, board):
		self.board = board
	def setPort (self,port=''):
		self.port = port
	def getPort (self):
		return self.port
	def getBoard(self):
		return self.board
	def setBaudrate (self, baudRate):
		self.baudRate = baudRate

	def initializeSerial (self, port, baudRate):
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

	def close (self):
		self.serial.close()

	def write (self, data):
		self.serial.write(data)

	def read (self):
		out = ''
		while self.serial.inWaiting() > 0:
			out += self.serial.read(1)
		if out != '':
			return out


class SerialMonitor:
	def __init__(self, board, port, baudRate):
		self.serialCom = SerialCommunication()
