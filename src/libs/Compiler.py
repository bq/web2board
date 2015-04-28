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

class Compiler:
	def __init__(self, pathToMain):
		self.pathToMain = pathToMain
		self.arduinoLibs = ''
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
		output = p.stdout.read()
		outputErr = p.stderr.read()
		# print output, outputErr
		print 'outputErr',outputErr
		print 'output',output
		return output


	def removeTmp(self):
		print 'path:', self.pathToMain
		call(["cd", self.pathToMain+"/"])
		call(["ls"])
		call(["rm", "-rf", "tmp"])



	# function parseError(error, stdout, stderr) {
	#     var error = {
	#         compilation: [],
	#         uploading: ''
	#     };
	#     //Parse errors comming from stderr regarding the compilation:
	#     var compileStderr = stderr.substr(0, stderr.indexOf("make:"));
	#     compileStderr = compileStderr.split("applet/tmp.cpp:");
	#     for (var i in compileStderr) {
	#         var line, func, err;
	#         var index = compileStderr[i].indexOf(":");
	#         if (index > 0) {
	#             if (!isNaN(parseInt(compileStderr[i].substr(0, index), 10))) {
	#                 line = parseInt(compileStderr[i].substr(0, index));
	#                 err = compileStderr[i].substr(compileStderr[i].indexOf("error:") + 6, compileStderr[i].length);
	#             } else {
	#                 func = compileStderr[i];
	#             }
	#         }
	#         if (line && func && index) {
	#             error.compilation.push({
	#                 line: line,
	#                 func: func,
	#                 error: err
	#             });
	#             line = undefined;
	#             err = undefined;
	#             index = undefined;
	#             console.log('---------------------------------------------------');
	#         }
	#     }
	#     //Parse errors comming from stderr regarding the uploading (AVRDUDE):
	#     var uploadStderr = stderr.split("avrdude:");
	#     if (uploadStderr[uploadStderr.length - 1].search('bytes of flash written') > 0) {
	#         console.log('UPLOADED CORRECTLY');
	#     } else {
	#         error.uploading = uploadStderr.join('');
	#     }
	#     console.log('error', error);
	#     // if (error.compilation.length === 0) {
	#     //     console.log('NO ERRORS, COMPILATION SUCCESSFUL');
	#     // }
	#     return error;
	# }

	# function compile(data, callback) {
	#     createEnvironment(data, function() {
	#         // Finally, execute the "make" command on the given directory
	#         exec(makeCommand, {
	#             cwd: 'tmp',
	#         }, function(error, stdout, stderr) {
	#             console.log('compiling...\n');
	#             // console.log('stderr', stderr);
	#             // console.log('stdout', stdout);
	#             // return parseError(error, stdout, stderr);
	#             callback({
	#                 stdout: stdout,
	#                 stderr: stderr
	#             });
	#         });
	#     });
	# };	




