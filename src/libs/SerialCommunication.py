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
from BoardConfig import BoardConfig

class SerialCommunication:
	def __init__(self, pathToMain):
		self.boardSettings = defaultdict(BoardConfig)
		self.pathToMain = pathToMain;
		rel_path = "/src/res/boards.txt"
		self.parseBoardSettings(self.pathToMain+rel_path)
		self.board = None
		self.port = None

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
			# print boardConfig
			boardConfig.pop(0) #Remove empty first element
			self.boardSettings[boardName]=BoardConfig(boardConfig)

	def getAvailablePorts (self):
		if platform.system() =='Windows':
			# print 'Windows'
			availablePorts = glob.glob('COM*')
		if platform.system() =='Darwin':
			# print 'Darwin'
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/tty.usbmodem*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/tty.usbserial-*')
			else:
				availablePorts = glob.glob('/dev/tty*')

		if platform.system() =='Linux':
			# print 'Linux'
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/ttyACM*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/ttyUSB*')
			else:
				availablePorts = glob.glob('/dev/tty*')
		return availablePorts

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
