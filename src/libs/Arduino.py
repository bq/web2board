#!/usr/bin/python
import serial
import os
from subprocess import call
import platform
import glob
from time import sleep
import binascii
import math
from collections import defaultdict
import subprocess
import re
import json

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")
import unicodedata

import subprocess

def callAvrdude(args):
	cmd = "avrdude "+args
	p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
	output = p.stdout.read()
	err = p.stderr.read()
	return output, err


class BoardConfig :
	def __init__ (self, args):
		for arg in args:
			if 'build.mcu' in arg[0]:
				self.build_mcu= arg[1]
			if 'upload.speed' in arg[0]:
				self.upload_speed= arg[1]
	def getBaudRate(self):
		return self.upload_speed
	def getMaxSize (self):
		return self.upload_maximum_size
	def getMCU (self):
		return self.build_mcu


class ArduinoCompilerUploader:

	def __init__(self, pathToMain):
		self.pathToMain = pathToMain
		self.pathToSketchbook = ''
		self.pathToArduinoDir = pathToMain+'/res/arduino/'
		self.uploader = Uploader(pathToMain)
		self.compiler = Compiler(pathToMain)
		self.boardSettings = defaultdict(BoardConfig)
		self.parseBoardSettings(self.pathToMain+"/src/res/boards.txt")
		self.board = 'uno'
		self.port = None

	def setBoard (self, board):
		self.board = board
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

	def compile (self, code):
		return self.compiler.compile( code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook)

	def upload (self, code):
		self.compiler.compile( code, self.getBoard() or 'uno', self.pathToArduinoDir, self.pathToSketchbook)
		self.uploader.upload( code, self.getPort(), self.getBoard(), self.getBoardMCU(), self.getBoardBaudRate(), self.pathToMain, self.pathToSketchbook)

	def searchPort (self):
		availablePorts = self.getAvailablePorts()
		if len(availablePorts) <=0:
			return None
		for port in availablePorts:
			args = "-P "+port+" -p "+ self.getBoardMCU() +" -b "+ self.getBoardBaudRate()+" -c arduino"
			output, err = callAvrdude(args);
			if 'Device signature =' in output or 'Device signature =' in err:
				self.setPort(port)
				return port
		return None

class Compiler:

	def __init__(self, pathToMain):
		self.pathToMain = pathToMain
		self.userLibs = ''
		self.arduinoLibs = ['EEPROM', 'Esplora', 'Ethernet', 'Firmata', 'GSM', 'LiquidCrystal', 'Robot_Control', 'RobotIRremote', 'Robot_Motor', 'SD', 'Servo', 'SoftwareSerial', 'SPI', 'Stepper', 'TFT', 'WiFi', 'Wire'];

	def createMakefile(self, board,  arduinoDir, sketchbookDir):
		if not os.path.exists("tmp"):
			os.makedirs("tmp")
		fo = open(self.pathToMain+"/res/Makefile", "r")
		makefile = fo.read()
		# print 'makefile', makefile
		fo.close()
		fo = open(self.pathToMain+"/tmp/Makefile", "w")
		fo.write("MODEL = "+board+"\n")
		fo.write("ARDLIBS = "+self.getArduinoLibs()+"\n")
		fo.write("USERLIBS = "+self.getUserLibs()+"\n")
		fo.write("ARDUINO_DIR = "+arduinoDir+"\n")
		fo.write("HOME_LIB = "+sketchbookDir+"\n")
		fo.write(makefile)
		fo.close()

	def createSketchFile (self, code):
		fo = open(self.pathToMain+"/tmp/tmp.ino", "w")
		fo.write(code)
		fo.close()

	def getArduinoLibs(self):
		return self.arduinoLibs

	def getUserLibs (self):
		return self.userLibs

	def setArduinoLibs(self, arduinoLibs):
		self.arduinoLibs = arduinoLibs

	def setUserLibs (self, userLibs):
		self.userLibs = userLibs

	def find_all(self,a_str, sub):
		start = 0
		while True:
			start = a_str.find(sub, start)
			if start == -1: return
			yield start
			start += len(sub) # use start += 1 to find overlapping matches

	def parseLibs(self, code):
		arduinoLibs = []
		userLibs = []
		initIndexes= list(self.find_all(code,'#include'))
		finalIndexes= list(self.find_all(code,'\n'))
		for i in range(len(initIndexes)):
			lib = code[initIndexes[i]: finalIndexes[i]]
			#remove all spaces, #include ,< & >,",.h
			lib = lib.replace(' ','').replace('#include','').replace('<','').replace('>','').replace('"','').replace('.h','')
			if lib in self.arduinoLibs:
				arduinoLibs.append(lib)
			else:
				userLibs.append(lib)

		#remove duplicates from lists of libs
		arduinoLibs = sorted(set(arduinoLibs))
		userLibs = sorted(set(userLibs))
		#join lists into strings
		self.setArduinoLibs(' '.join(arduinoLibs))
		self.setUserLibs(' '.join(userLibs))

	def compile(self, code, board,  arduinoDir, sketchbookDir):
		self.parseLibs(code)
		self.createMakefile(board,  arduinoDir, sketchbookDir)
		self.createSketchFile(code)
		p = subprocess.Popen('make', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, cwd=self.pathToMain+'/tmp')
		stdOut = p.stdout.read()
		stdErr = p.stderr.read()
		errorReport =  {'stdOut':stdOut,'stdErr':stdErr, 'errorReport':self.compilerStderr(stdErr)}
		if len(errorReport['errorReport'])>0:
			errorReport['status'] = 'KO'
		else:
			errorReport['status'] = 'OK'
		return errorReport


	def removeTmp(self):
		print 'path:', self.pathToMain
		call(["cd", self.pathToMain+"/"])
		call(["ls"])
		call(["rm", "-rf", "tmp"])

	def createUnicodeString(self, input_str):
		return  unicodedata.normalize('NFKD', unicode(input_str)).encode('ASCII','ignore')

	def compilerStderr (self, stdErr):
		#split the stdErr with each line ending
		stdErrSplitted = stdErr.split('\n')
		errorReport = []
		errorNum = -1
		for error in stdErrSplitted:
			error = self.createUnicodeString(error)
			#These characters are the report of in which function the error is happening 
			if 'In function' in error:
				errorNum +=1
				error = re.sub('^(.*?): In function ', '',error)
				error = error.replace(':', '')
				errorReport.append({'function': error, 'error':[]})
			else:
				#Remove non important parts of the string
				error = re.sub('^(.*?)applet/tmp.cpp', '', error)
				error = re.sub(r'error', '', error)
				#Find the line number in the error report
				line = re.findall(':\d*:', error)
				#If there is a line, there is an error to report
				if len(line)>0:
					line = line[0]
					line = line.replace(':','')
					#Replace everything but the error info
					error = re.sub(':\d*:', '',error)
					#If there appears this characters, there is no error, is the final line of the error report
					if 'make: *** [applet/tmp.o]' in error:
						error = ''
					#Append the error report
					errorReport[errorNum]['error'].append({'line':line, 'error':error})

		return errorReport

class Uploader :
	def __init__(self, pathToMain):
		self.pathToMain = pathToMain

	def upload (self, code, port, board, boardMCU, boardBaudRate, pathToMain, pathToSketchbook):
		if port != None:
			args = "-v -F "+"-P "+ port +" -p "+ boardMCU +" -b "+ boardBaudRate+" -c arduino " + "-U flash:w:"+ self.pathToMain+'/tmp/applet/tmp.hex'
			stdOut, stdErr = callAvrdude(args)
			return {'stdOut':stdOut,'stdErr':stdErr, 'errorReport':self.avrdudeStderr(stdErr)}
		else:
			return {'status':'KO','error':'no port'}

	def avrdudeStderr (self, stdErr):
		errorReport = {}
		#Extract the device signature 
		error = re.sub('((.|\n)*)Device signature =', '', stdErr)
		errorReport['signature'] = re.sub('\n((.|\n)*)', '', error)
		writingCompleted = re.search('Writing \| ################################################## \| 100%', stdErr)
		readingCompleted = re.search('Reading \| ################################################## \| 100%', stdErr)
		if (writingCompleted != None and readingCompleted!= None):
			errorReport['status'] = 'OK'
		else:
			errorReport['status'] = 'KO'
			errorReport['error'] = ''
		return errorReport

