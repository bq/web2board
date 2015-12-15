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
from os.path import expanduser
import platform
import shutil
import time 
import logging
from . import base

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import unicodedata

import arduino_compiler


class Compiler:
	def __init__(self, pathToMain):
		self.pathToMain = pathToMain
		self.userLibs = ''
		
		if platform.system() == 'Windows':
			self.tmpPath = os.path.dirname(os.path.dirname(os.path.dirname(base.sys_path.get_tmp_path())))+'/.web2board/'
		else:	
			self.tmpPath = expanduser("~").decode('latin1')+'/.web2board/'

		self.oficialArduinoLibs = ['EEPROM', 'Esplora', 'Ethernet', 'Firmata', 'GSM', 'LiquidCrystal', 'Robot_Control', 'RobotIRremote', 'Robot_Motor', 'SD', 'Servo', 'SoftwareSerial', 'SPI', 'Stepper', 'TFT', 'WiFi', 'Wire'];
		self.bitbloqLibs = ['bqLiquidCrystal', 'bqSoftwareSerial', 'ButtonPad', 'Joystick', 'LineFollower', 'MCP23008', 'Oscillator', 'US']
		self.ide_path = os.path.realpath(__file__)
		if self.ide_path[len(self.ide_path)-1] == 'c':
			self.ide_path = self.ide_path[:-25]
		else:
			self.ide_path = self.ide_path[:-24]
		arduino_name = 'arduinoLinux'
		if platform.system() == 'Windows':
			arduino_name = 'arduinoWin'
		if platform.system() == 'Darwin':
			arduino_name = 'arduinoDarwin'


		if platform.system() == 'Darwin':
			if os.environ.get('PYTHONPATH') != None:
				self.ide_path = os.environ.get('PYTHONPATH')

		self.ide_path = os.path.join(self.ide_path ,'res',arduino_name)
		self.core_path = self.ide_path+'/hardware/arduino/cores/arduino'


	def removePreviousFiles (self):
		shutil.rmtree(self.tmpPath)

	def createMakefile(self, board,  arduinoDir, sketchbookDir):
		if not os.path.exists(self.tmpPath):
			os.makedirs(self.tmpPath)
		fo = open(self.pathToMain+"/res/Makefile", "r")
		makefile = fo.read()
		fo.close()
		fo = open(self.tmpPath+"Makefile", "w")
		fo.write("MODEL = "+board+"\n")
		fo.write("ARDLIBS = "+self.getArduinoLibs()+"\n")
		fo.write("USERLIBS = "+self.getUserLibs()+"\n")
		fo.write("ARDUINO_DIR = "+arduinoDir+"\n")
		fo.write("HOME_LIB = "+sketchbookDir+"\n")
		fo.write("TARGET = tmp\n")
		fo.write(makefile)
		fo.close()

	def createSketchFile (self, code):
		if not os.path.exists(self.tmpPath):
			os.makedirs(self.tmpPath)
		fo = open(self.tmpPath+"tmp.ino", "w")
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
		lib = ''
		initIndexes= list(self.find_all(code,'#include'))
		if len(initIndexes) >= 1:
			for i in range(len(initIndexes)):
				finalIndex = code.find('\n', initIndexes[i])
				lib = code[initIndexes[i]: finalIndex]
				#remove all spaces, #include ,< & >,",.h
				lib = lib.replace(' ','').replace('#include','').replace('<','').replace('>','').replace('"','').replace('.h','')
				if lib in self.oficialArduinoLibs:
					arduinoLibs.append(lib)
				else:
					# if (lib == 'bqLiquidCrystal'):
					# 	userLibs.append('MCP23008')
					userLibs.append(lib)
		#remove duplicates from lists of libs
		arduinoLibs = sorted(set(arduinoLibs))
		userLibs = sorted(set(userLibs))
		print (arduinoLibs)
		print (userLibs)
		#join lists into strings
		self.setArduinoLibs(' '.join(arduinoLibs))
		self.setUserLibs(' '.join(userLibs))
		return arduinoLibs+userLibs


	def createUnicodeString(self, input_str):
		return  unicodedata.normalize('NFKD', unicode(input_str)).encode('ASCII','ignore')


	def parseError(self, error):
		returnObject = []
		if 'too few arguments to function' in error or 'expected ; before { token' in error or 'expected primary-expression before' in error or 'expected unqualified-id before' in error or 'no matching function for call to' in error:
			returnObject.append('input-empty')
		if 'expected } before else' in error:
			returnObject.append('else-inside-if')
		if 'break statement not within loop or switch' in error:
			returnObject.append('break-outside-loop')
		if 'continue statement not within a loop' in error:
			returnObject.append('coutinue-outside-loop')
		if 'case label' in error and 'not within a switch statement' in error:
			returnObject.append('case-outside-switch')
		if 'else without a previous if' in error: 
			returnObject.append('else-without-if')
		if 'function-definition is not allowed here' in error:
			returnObject.append('function-definition-not-allowed')
		if 'invalid conversion from' in error:
			returnObject.append('invalid-conversion')
		if 'was not declared in this scope' in error:
			returnObject.append('not-declared-in-scope')
		if 'does not name a type' in error: 
			returnObject.append('not-name-a-type')

		return returnObject

	def compilerStderr (self, stdErr):
		#split the stdErr with each line ending
		stdErrSplitted = stdErr.split('\n')
		errorReport = []
		errorNum = -1
		parsingError = False
		try:
			for error in stdErrSplitted:
				error = self.createUnicodeString(error)
				#These characters are the report of in which function the error is happening 
				if 'In function' in error:
					errorNum +=1
					error = re.sub('^(.*?): In function ', '',error)
					error = error.replace(':', '')
					errorReport.append({'function': error, 'error':[]})
				elif 'error: expected initializer before' in error:
					error = re.sub('^(.*?)error: expected initializer before ', '', error)
					errorReport.append({'function': error, 'error':'expected initializer before function'})
				elif 'No such file or directory' in error:
					error = re.sub('No such file: No such file or directory', '', error)
					errorReport.append({'function': error, 'error':'No such file or directory'})
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
						if 'warning:' not in error:
							#Append the error report
							bloqsError = self.parseError(error)
							if errorNum < 0 :
								errorNum +=1
								errorReport.append({'function': error, 'error':[]})
							errorReport[errorNum]['error'].append({'line':line, 'error':error, 'bloqsError':bloqsError})
		except :
			print 'Compiler parsing exception'
			parsingError = True
		print errorReport
		return parsingError, errorReport

	def compileWithMakefile(self, code, board,  arduinoDir, sketchbookDir):
		self.removePreviousFiles();
		self.parseLibs(code)
		self.createMakefile(board,  arduinoDir, sketchbookDir)
		self.createSketchFile(code)
		p = subprocess.Popen('make', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=(platform.system() != 'Windows'), cwd=self.tmpPath)
		stdOut = p.stdout.read()
		stdErr = p.stderr.read()
		parsingError, compilerStderr = self.compilerStderr(stdErr)
		errorReport =  {'stdOut':stdOut,'stdErr':stdErr, 'errorReport':compilerStderr}
		if len(errorReport['errorReport'])>= 1 or parsingError:#or len(stdErr)>0:
			errorReport['status'] = 'KO'
		else:
			errorReport['status'] = 'OK'
		return errorReport


	def compile(self, code, board, arduinoDir, sketchbookDir, target_board_mcu, build_f_cpu):
		self.parseLibs(code)
		self.createSketchFile(code)

		bitbloqLibsInclude = False
		self.libs = []
		for lib in self.getArduinoLibs().split(' '):
			if lib != '':
				self.libs.append(self.ide_path+'/libraries/'+lib)
		for lib in self.getUserLibs().split(' '):
			if lib != '':
				if lib in self.bitbloqLibs: 
					bitbloqLibsInclude = True
				self.libs.append(sketchbookDir+'/libraries/'+lib)
				self.libs.append(sketchbookDir+'/libraries/bitbloqLibs/'+lib)

		self.libs.append(self.ide_path+'/hardware/arduino/variants/standard')
		if bitbloqLibsInclude:
			self.libs.append(sketchbookDir+'/libraries/bitbloqLibs')
		


		if platform.system() == 'Windows':
		 	self.ide_path = self.ide_path.replace('/', '\\')
		 	self.core_path = self.core_path.replace('/', '\\')
			for i in range(len(self.libs)):
		 		self.libs[i] = self.libs[i].replace('/', '\\')
		compiler = arduino_compiler.Compiler(self.tmpPath, self.libs, self.core_path, self.ide_path, build_f_cpu, target_board_mcu)
		stdErr = compiler.build()
		parsingError, compilerStderr = self.compilerStderr(stdErr)
		errorReport =  {'stdOut':'','stdErr':stdErr, 'errorReport':compilerStderr}
		if len(errorReport['errorReport'])>= 1 or parsingError:#or len(stdErr)>0:
			errorReport['status'] = 'KO'
		else:
			errorReport['status'] = 'OK'
		return errorReport

