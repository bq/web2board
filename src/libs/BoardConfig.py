#!/usr/bin/python

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


