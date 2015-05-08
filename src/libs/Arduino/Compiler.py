#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: May 2015                                                        #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
#-----------------------------------------------------------------------#
import os
import subprocess
import re

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import unicodedata

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
