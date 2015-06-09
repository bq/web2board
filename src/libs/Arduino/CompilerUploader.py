#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: April - May 2015                                                #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
#-----------------------------------------------------------------------#

import os
import platform
import glob
from collections import defaultdict
import serial.tools.list_ports
from os.path import expanduser

from Compiler import Compiler
from Uploader import Uploader
from utils import BoardConfig, callAvrdude

class ArduinoCompilerUploader:

	def __init__(self, pathToMain):
		self.pathToMain = pathToMain
		self.pathToSketchbook = expanduser("~")+'/sketchbook'
		self.pathToArduinoDir = pathToMain+'/res/arduino/'
		self.uploader = Uploader(pathToMain)
		self.compiler = Compiler(pathToMain)
		self.boardSettings = defaultdict(BoardConfig)
		self.parseBoardSettings(self.pathToMain+"/res/boards.txt")
		self.board = 'uno'
		self.port = None

	def setBoard (self, board):
		self.board = board
		return self.searchPort()
	def setPort (self,port=''):
		self.port = port
	def getPort (self):
		return self.port
	def getBoard(self):
		return self.board

	def getBoardBaudRate(self):
		return self.boardSettings[self.board].getBaudRate()

	def getBoardMCU(self):
		return self.boardSettings[self.board].getMCU()


	def parseBoardSettings (self, path):
		file=open(path,'r')
		#Split the file using the separator in boards.txt to separate the config of the different boards
		a = file.read().split('\n\n##############################################################\n\n');
		a.pop(0) #Remove first element which is only a url
		for line in a:
			boardName = line.split('.')[0]
			boardConfig = line.split('\n')
			boardConfig= [i.split('=')for i in boardConfig]
			boardConfig.pop(0) #Remove empty first element
			self.boardSettings[boardName]=BoardConfig(boardConfig)

	def getAvailablePorts (self):
		if platform.system() =='Windows':
			comPorts = list(serial.tools.list_ports.comPorts())
			availablePorts = []
			for port in comPorts:
				availablePorts.append(port[0])

		elif platform.system() =='Darwin':
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/tty.usbmodem*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/tty.usbserial-*')
			else:
				availablePorts = glob.glob('/dev/tty*')

		elif platform.system() =='Linux':
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/ttyACM*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/ttyUSB*')
			else:
				availablePorts = glob.glob('/dev/tty*')
		return availablePorts


	def searchPort (self):
		availablePorts = self.getAvailablePorts()
		if len(availablePorts) <=0:
			return None
		ports = []
		for port in availablePorts:
			args = "-P "+port+" -p "+ self.getBoardMCU() +" -b "+ self.getBoardBaudRate()+" -c arduino"
			output, err = callAvrdude(args);
			if 'Device signature =' in output or 'Device signature =' in err:
				ports.append(port)
		if len(ports)==1:
			self.setPort(ports[0])
			return port
		else:
			return ports



	def compile (self, code):
		return self.compiler.compile( code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook)

	def upload (self, code):
		compilationErrorReport = self.compiler.compile( code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook)
		if compilationErrorReport['status'] == 'OK':
			print 'compilation OK'
			uploadErrorReport = self.uploader.upload( code, self.getPort(), self.getBoard(), self.getBoardMCU(), self.getBoardBaudRate(), self.pathToMain, self.pathToSketchbook)
			print uploadErrorReport
			return uploadErrorReport
		else:
			return compilationErrorReport