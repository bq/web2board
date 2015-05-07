#!/usr/bin/python
import serial
import os
import platform
import glob
from time import sleep
import binascii
import math
import sys
from collections import defaultdict
import json


from Arduino import ArduinoCompilerUploader
from SerialCommunication import SerialCommunication


class CompilerUploader:
	def __init__(self):
		self.pathToMain = os.path.dirname(os.path.realpath("web2board.py"))
		self.arduino = ArduinoCompilerUploader(self.pathToMain)
		self.serialCom = SerialCommunication()
		self.readConfigFile()

	def readConfigFile(self):
		with open(self.pathToMain+'/src/res/config.json') as json_data_file:
			data = json.load(json_data_file)
			self.version = str(data['version'])

	def getVersion (self):
		return self.version
	def setBoard (self, board):
		self.serialCom.setBoard(board)
		return 	self.searchPort()
	def setPort (self,port=''):
		self.serialCom.setPort(port)
	def getPort (self):
		return self.serialCom.getPort()
	def getBoard(self):
		return self.serialCom.getBoard()

	def searchPort (self):
		port = self.arduino.searchPort()

	def openSerialPort(self):
		self.serialCom.open()

	def closeSerialPort (self):
		self.serialCom.close()

	def writeSerialPort (self, data):
		self.serialCom.write(data)

	def readSerialPort (self):
		return self.serialCom.read()

	def compile (self, code):
		return self.arduino.compile(code)

	def upload (self, code):
		return self.arduino.upload(code)
