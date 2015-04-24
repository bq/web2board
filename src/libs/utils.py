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

STK_ENTER_PROGMODE= 	0x50  # 'P'
CRC_EOP=				0x20  # 'SPACE'

class BoardConfig :
	def __init__ (self, args):
		for arg in args:
			if 'build.mcu' in arg[0]:
				self.build_mcu= arg[1]
			if 'upload.speed' in arg[0]:
				self.upload_speed= arg[1]
		# self.name=args[0]
		# self.upload_protocol=args[1]
		# self.upload_maximum_size=args[2]
		# self.upload_speed=args[3]
		# self.bootloader_low_fuses=args[4]
		# self.bootloader_high_fuses=args[5]
		# self.bootloader_extended_fuses=args[6]
		# self.bootloader_path=args[7]
		# self.bootloader_file=args[8]
		# self.bootloader_unlock_bits=args[9]
		# self.bootloader_lock_bits=args[10]
		# self.build_mcu=args[11]
		# self.build_f_cpu=args[12]
		# self.build_core=args[13]
		# self.build_variant=args[14]

	def getBaudRate(self):
		return self.upload_speed
	def getMaxSize (self):
		return self.upload_maximum_size
	def getMCU (self):
		return self.build_mcu

class SerialMonitor:
	def __init__(self):
		self.boardSettings = defaultdict(BoardConfig)
		self.parseBoardSettings('/home/irene-sanz/repos/web2board/res/boards.txt')

	def setBoard (self, board):
		self.board = board
		self.searchPort()

	def setPort (self,port=''):
		self.port = port

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

	def searchPort (self):
		availablePorts = self.getAvailablePorts()
		for port in availablePorts:
			print 'trying to open port:',port, 'with baudRate', self.getBoardBaudRate()
			# call(["avrdude", "-P","/dev/ttyACM0", "-p","atmega328p", "-c","arduino"])
			cmd = "avrdude -P "+port+" -p "+self.getBoardMCU() +" -b "+ self.getBoardBaudRate()+" -c arduino"
			print cmd
			p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
			output = p.stdout.read()
			print 'AVRDUDE OUTPUT :',output
			if 'Device signature =' in output:
				print 'PORT FOUND'
				self.setPort(port)
				break

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
			print 'windows'
			availablePorts = glob.glob('COM*')
		if platform.system() =='Darwin':
			print 'Darwin'
			if self.board == 'uno':
				availablePorts = glob.glob('/dev/tty.usbmodem*')
			elif self.board == 'bt328':
				availablePorts = glob.glob('/dev/tty.usbserial-*')
			else:
				availablePorts = glob.glob('/dev/tty*')

		if platform.system() =='Linux':
			print 'Linux'
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

class Compiler:
	def __init__(self, board='bt328',port='/dev/ttyUSB0', baudRate=19200):
		self.board = board
		self.port = port
		self.baudRate = baudRate
		self.pathToMain = os.path.dirname(os.path.realpath("main.py"))
		self.createMakefile()


	def createMakefile(self):
		if not os.path.exists("tmp"):
			os.makedirs("tmp")
		fo = open("tmp/Makefile", "w")
		fo.write("BOARD_TAG = "+self.board+"\n")
		fo.write("ARDUINO_LIBS = \n")
		fo.write("ARDUINO_PORT = "+self.port+"\n")
		fo.write("include /usr/share/arduino/Arduino.mk")
		fo.close()

	def compile(self):
		os.chdir("tmp")
		call(["make"])

	def upload(self):
		os.chdir("tmp")
		call(["make", "upload"])	#avrdude -P /dev/ttyACM0 -p atmega328p -c arduino -U flash:w:sketches/1.hex -vvvv
		self.removeTmp()

	def removeTmp(self):
		print 'path:', self.pathToMain
		call(["cd", self.pathToMain+"/"])
		call(["ls"])
		call(["rm", "-rf", "tmp"])
