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
import re

from utils import callAvrdude
from libs.base import sys_path

class Uploader :
	def __init__(self, pathToMain):

		self.pathToMain = pathToMain

		self.tmpPath = sys_path.get_tmp_path() + '/Stino_build/.web2board/.web2board.hex'

	def uploadFromWeb2boardFolder (self, code, port, board, boardMCU, boardBaudRate, pathToMain, pathToSketchbook):
		if port != None:
			args = "-v -F "+"-P "+ port +" -p "+ boardMCU +" -b "+ boardBaudRate+" -c arduino " + "-U flash:w:"+ self.tmpPath+'applet/tmp.hex'
			stdOut, stdErr = callAvrdude(args)
			errorReport = self.avrdudeStderr(stdErr)
			return {'status':errorReport['status'],'errorReport':errorReport,'stdOut':stdOut,'stdErr':stdErr}
		else:
			return {'status':'KO','error':'no port'}

	def upload (self, code, port, board, boardMCU, boardBaudRate, pathToMain, pathToSketchbook):
		if port != None:
			args = "-v -F "+"-P "+ port +" -p "+ boardMCU +" -b "+ boardBaudRate+" -c arduino " + "-U flash:w:"+ self.tmpPath+":i"
			stdOut, stdErr = callAvrdude(args)
			errorReport = self.avrdudeStderr(stdErr)
			return {'status':errorReport['status'],'errorReport':errorReport,'stdOut':stdOut,'stdErr':stdErr}
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
