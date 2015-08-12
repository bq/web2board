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

from Arduino.CompilerUploader import ArduinoCompilerUploader

import sys
import json
import os
import logging
import platform
##
# Class CompilerUploader, created to support different compilers & uploaders
#
class CompilerUploader:
	def __init__(self):
		# self.pathToMain = os.path.dirname(os.path.realpath("web2board.py"))
		
		if platform.system() == 'Darwin':
			# logging.debug('sys.path[0]');
			# logging.debug(sys.path[0]);
			# logging.debug('PWD=');
			# logging.debug(os.environ.get('PWD'));
			# logging.debug('PYTHONPATH=');
			# logging.debug(os.environ.get('PYTHONPATH'));
			# logging.debug('ENVIRON=');
			# logging.debug(os.environ);
			if os.environ.get('PYTHONPATH') != None:
				self.pathToMain = os.environ.get('PYTHONPATH')
			else:
				self.pathToMain = sys.path[0]
		elif platform.system() == 'Windows' or platform.system() == 'Linux':
			self.pathToMain = sys.path[0]
		self.arduino = ArduinoCompilerUploader(self.pathToMain)
		self.readConfigFile()

	def readConfigFile(self):
		with open(self.pathToMain+'/res/config.json') as json_data_file:
			data = json.load(json_data_file)
			self.version = str(data['version'])

	def getVersion (self):
		return self.version
	def setBoard (self, board):
		return self.arduino.setBoard(board)
	def setPort (self,port=''):
		self.arduino.setPort(port)
	def getPort (self):
		return self.arduino.getPort()
	def getBoard(self):
		return self.arduino.getBoard()
	def searchPort (self):
		return self.arduino.searchPort()
	def compile (self, code):
		return self.arduino.compile(code)
	def upload (self, code):
		return self.arduino.upload(code)
