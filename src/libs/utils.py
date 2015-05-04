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

from Compiler import Compiler
from SerialCommunication import SerialCommunication
import json



class Web2board:
	def __init__(self):
		self.pathToMain = os.path.dirname(os.path.realpath("web2board.py"))
		self.compiler = Compiler(self.pathToMain)
		self.serialCom = SerialCommunication(self.pathToMain)
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
		availablePorts = self.serialCom.getAvailablePorts()
		if len(availablePorts) <=0:
			return None
		for port in availablePorts:
			args = "-P "+port+" -p "+self.serialCom.getBoardMCU() +" -b "+ self.serialCom.getBoardBaudRate()+" -c arduino"
			output, err = self.callAvrdude(args);
			if 'Device signature =' in output or 'Device signature =' in err:
				self.serialCom.setPort(port)
				return port

	def callAvrdude(self, args):
		cmd = "avrdude "+args
		p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
		output = p.stdout.read()
		err = p.stderr.read()
		print 'AVRDUDE OUTPUT :',output
		print 'AVRDUDE stderr :',err

		return output, err

	def openSerialPort(self):
		self.serialCom.open()

	def closeSerialPort (self):
		self.serialCom.close()

	def writeSerialPort (self, data):
		self.serialCom.write(data)

	def readSerialPort (self):
		return self.serialCom.read()

	def compile (self, code):
		return self.compiler.compile(code,self.getBoard(), self.pathToMain+'/res/arduino','')

	def upload (self, code):
		self.compiler.compile(code,self.getBoard(), self.pathToMain+'/res/arduino','')
		args = "-v -F "+"-P "+self.getPort()+" -p "+self.serialCom.getBoardMCU() +" -b "+ self.serialCom.getBoardBaudRate()+" -c arduino " + "-U flash:w:"+ self.pathToMain+'/tmp/applet/tmp.hex'
		print 'AVRDUDE ARGS UPLOAD', args
		return self.callAvrdude(args)
