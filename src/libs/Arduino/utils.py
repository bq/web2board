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
import subprocess
import platform
import os

def find_all(a_str, sub):
	start = 0
	while True:
		start = a_str.find(sub, start)
		if start == -1: return
		yield start
		start += len(sub)

def callAvrdude(args):
	if platform.system() =='Windows':
		avrdude_path = os.path.join(os.path.realpath(__file__))

		indexes = list(find_all(avrdude_path,'\\'))
		index = indexes[len(indexes)-3]
		avrdude_path = avrdude_path[:index]

		cmd ='"'+avrdude_path+'\\res\\avrdude.exe" '+args
	elif platform.system() == 'Darwin':
		if os.environ.get('PYTHONPATH') != None:
			avrdude_path = os.environ.get('PYTHONPATH')
		else:
			avrdude_path = os.path.join(os.path.realpath(__file__))
			print avrdude_path
			indexes = list(find_all(avrdude_path,'/'))
			print indexes
			index = indexes[len(indexes)-3]
			avrdude_path = avrdude_path[:index]

		cmd = avrdude_path + "/res/arduinoDarwin/hardware/tools/avr/bin/avrdude -C "+ avrdude_path + "/res/arduinoDarwin/hardware/tools/avr/etc/avrdude.conf "+args
	else:
		cmd = "avrdude "+args
	print cmd
	p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=(platform.system() != 'Windows'))
	output = p.stdout.read()
	err = p.stderr.read()
	print output
	print err
	return output, err


class BoardConfig :
	def __init__ (self, args):
		for arg in args:
			if 'build.mcu' in arg[0]:
				self.build_mcu= arg[1]
			if 'upload.speed' in arg[0]:
				self.upload_speed= arg[1]
			if 'f_cpu' in arg[0]:
				self.f_cpu = arg[1]
	def getBaudRate(self):
		return self.upload_speed
	def getMaxSize (self):
		return self.upload_maximum_size
	def getMCU (self):
		return self.build_mcu
	def getFCPU (self):
		return self.f_cpu