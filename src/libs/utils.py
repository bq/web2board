#!/usr/bin/python
import time
import serial
import os
from subprocess import call


class SerialMonitor:
	def __init__(self, port='/dev/ttyACM0', baudRate=9600):
		self.port = port
		self.baudRate = baudRate
		self.serial = serial.Serial(
			port=self.port,
			baudrate=self.baudRate,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS
		)
		self.serial.close()

	def close (self):
		self.serial.close()
	def open(self):
		self.serial.open()
		self.serial.isOpen()


	def write (self, data):
		self.serial.write(data)
	def read (self):
		out = ''
		while self.serial.inWaiting() > 0:
			out += self.serial.read(1)
		if out != '':
			return out


		# print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

		# input=1
		# while 1 :
			# get keyboard input
			# input = raw_input(">> ")
			# if input == 'exit':
			# 	self.serial.close()
			# 	exit()
			# else:
				# self.serial.write(input)
				# out = ''
				# time.sleep(1)
				# while self.serial.inWaiting() > 0:
				# 	out += self.serial.read(1)
					
				# if out != '':
				# 	print ">>" + out

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
		call(["make", "upload"])
		self.removeTmp()

	def removeTmp(self):
		print 'path:', self.pathToMain
		call(["cd", self.pathToMain+"/"])
		call(["ls"])
		call(["rm", "-rf", "tmp"])
