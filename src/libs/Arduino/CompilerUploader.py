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
import logging

from . import base

from collections import defaultdict
from os.path import expanduser

from Compiler import Compiler
from Uploader import Uploader
from utils import BoardConfig, callAvrdude

class ArduinoCompilerUploader:

	def __init__(self, pathToMain):
		#Get path on mac
		if platform.system() == 'Darwin':
			# logging.debug('self.pathToMain');
			# logging.debug(self.pathToMain);
			# logging.debug('PWD=');
			# logging.debug(os.environ.get('PWD'));
			#logging.debug('PYTHONPATH=');
			#logging.debug(os.environ.get('PYTHONPATH'));
			# logging.debug('ENVIRON=');
			# logging.debug(os.environ);
			if os.environ.get('PYTHONPATH') != None:
				self.pathToMain = os.environ.get('PYTHONPATH')
			else:
				self.pathToMain = pathToMain
		elif platform.system() == 'Windows' or platform.system() == 'Linux':
			self.pathToMain = pathToMain

		if platform.system() == 'Linux':
			self.pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino'
		elif platform.system() == 'Windows' or platform.system() == 'Darwin':
			# self.pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino'
			self.pathToSketchbook = base.sys_path.get_document_path()+'/Arduino'

		self.pathToSketchbook = self.pathToSketchbook.decode('latin1')

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

	def getBoardFCPU(self):
		return self.boardSettings[self.board].getFCPU()

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
		availablePorts = []

		if platform.system() =='Windows':
			from serial.tools.list_ports import comports
			comPorts = list(comports())
			for port in comPorts:
				if not 'Bluetooth' in port[1]: #discard bluetooth ports
					availablePorts.append(port[0])
		elif platform.system() =='Darwin':
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/tty.usbmodem*')
				if len(availablePorts) < 1: # This is only for Arduino UNO compatible boards such as DCCDuino ( CH340/341 )
					availablePorts = glob.glob('/dev/tty.usbserial-*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/tty.usbserial-*')
			else:
				darwinPorts = glob.glob('/dev/tty.*')
				for port in darwinPorts:
					if not 'Bluetooth' in port: #discard bluetooth ports
						availablePorts.append(port)

			if len(availablePorts) < 1: 
				darwinPorts = glob.glob('/dev/tty.*')
				for port in darwinPorts:
					if not 'Bluetooth' in port: #discard bluetooth ports
						availablePorts.append(port)

		elif platform.system() =='Linux':
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/ttyACM*')
				if len(availablePorts) < 1: # This is only for Arduino UNO compatible boards such as DCCDuino ( CH340/341 )
					availablePorts = glob.glob('/dev/ttyUSB*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/ttyUSB*')
			else:
				availablePorts = glob.glob('/dev/tty*')

		return availablePorts


	def searchPort (self):
		availablePorts = self.getAvailablePorts()
		if len(availablePorts) <=0:
			return []
		ports = []
		for port in availablePorts:
			args = "-P "+port+" -p "+ self.getBoardMCU() +" -b "+ self.getBoardBaudRate()+" -c arduino"
			output, err = callAvrdude(args);
			if 'Device signature =' in output or 'Device signature =' in err:
				ports.append(port)
		if len(ports)==1:
			self.setPort(ports[0])
		return ports



	def compile (self, code):
		return self.compiler.compile( code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook, self.getBoardMCU(), self.getBoardFCPU())

	def upload (self, code):
		compilationErrorReport = self.compile(code)
		if compilationErrorReport['status'] == 'OK':
			uploadErrorReport = self.uploader.upload(code, self.getPort(), self.getBoard(), self.getBoardMCU(), self.getBoardBaudRate(), self.pathToMain, self.pathToSketchbook)
			return uploadErrorReport
		else:
			return compilationErrorReport