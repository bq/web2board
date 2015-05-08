#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: April - May 2015                                                #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
#-----------------------------------------------------------------------#

import serial
import os
from subprocess import call
import platform
import glob
import time
import binascii
import math
import sys
from collections import defaultdict
import subprocess
import wx._core
import threading
from Queue import Queue
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import unicodedata

qBoard = Queue()
qMonitor = Queue()
qBaudRate = Queue()


class SerialMonitor:
	def __init__(self, port, baudRate = 9600):
		self.port = port
		self.baudRate = baudRate
		self.serial = serial.Serial(
			port=self.port,
			baudrate=self.baudRate,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS
		)
		self.t2 = threading.Thread(target=self.ui)
		self.t2.start()

		self.t1 = threading.Thread(target=self.readQmonitor)
		self.t1.start()

		self.t3 = threading.Thread(target=self.readBoard)
		self.t3.start()

		self.t4 = threading.Thread(target=self.readBaudRate)
		self.t4.start()

	def readQmonitor(self):
		while 1:
			if not qMonitor.empty():
				message = qMonitor.get()
				if message == 'exitWeb2boardPythonProgram':
					self.serial.close()
					time.sleep(0.5)
					os._exit(1)
					return
				else:
					self.serial.write(message)
				qMonitor.task_done()


	def readBoard (self):
		while 1 :
			out = ''
			try:
				while self.serial.inWaiting() > 0:
					out += self.serial.read(1)
					time.sleep(0.01)
				if out != '':
					qBoard.put(out)
			except:
				pass

	def ui (self):
		ex = wx.App()
		ex.MainLoop()
		self.ui = SerialMonitorUI(None)

	def readBaudRate (self):
		while 1:
			if not qBaudRate.empty():
				self.serial.setBaudrate(qBaudRate.get())


class SerialMonitorUI(wx.Dialog):

	def __init__(self, parent):
		super(SerialMonitorUI, self).__init__(parent, title='bitbloq\'s Serial Monitor', size=(500,500), style=wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
)
		#Timer
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		self.timer.Start(10)
		self.newLine = '\n'


		# Elements
		self.inputTextBox = wx.TextCtrl(self, size=(300,10))
		self.response = wx.TextCtrl(self, size=(10,250), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
		self.sendButton = wx.Button(self, label='Send',style = wx.ALIGN_RIGHT)
		
		self.checkBox = wx.CheckBox(self, -1, 'NewLine', (10, 10))
		self.checkBox.SetValue(True)

		baudRates = ['300', '1200', '2400', '4800', '9600', '14400','19200', '28800', '38400', '57600', '115200']
		self.dropdown = wx.ComboBox(self, 0, '9600', (0, 0), wx.DefaultSize ,baudRates, wx.CB_DROPDOWN)

		# Events
		self.sendButton.Bind(wx.EVT_BUTTON, self.onSend)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.checkBox.Bind(wx.EVT_CHECKBOX, self.onBoxChanged)
		self.dropdown.Bind(wx.EVT_COMBOBOX, self.onBaudRateChanged)

		# Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.inputTextBox, 1,wx.ALL^wx.CENTER|wx.EXPAND, 12)
		hbox.Add(self.sendButton, 0, wx.ALL^wx.ALIGN_RIGHT, 12)
		vbox.Add(hbox, 0, wx.EXPAND, 12)
		# vbox.Add(self.inputTextBox, 1, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		vbox.Add(self.response, 1, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.checkBox, 0, wx.ALL^wx.ALIGN_LEFT, 12)
		hbox1.Add((0, 0), 1, wx.EXPAND)

		hbox1.Add(self.dropdown, 0, wx.ALL^wx.ALIGN_RIGHT, 12)
		vbox.Add(hbox1, 0, wx.EXPAND, 12)
		self.SetSizer(vbox)
		self.ShowModal()

	def update(self, event):
		if not qBoard.empty():
			message = qBoard.get()
			self.response.AppendText('\t'+message+self.newLine)

	def onSend(self, event):
		message = self.inputTextBox.GetValue()
		self.response.AppendText(message+self.newLine)
		qMonitor.put(unicode(message))
		self.inputTextBox.SetValue('')

	def onBoxChanged (self, event):
		if self.newLine =='\n':
			self.newLine=''
		else:
			self.newLine='\n'

	def onBaudRateChanged (self, event):
		qBaudRate.put(self.dropdown.GetValue())

	def onClose(self, event):
		qMonitor.put('exitWeb2boardPythonProgram')
		self.Destroy()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'USAGE: SerialMonitor << port >>'
		sys.exit(1)
	else:
		serialMonitor = SerialMonitor(sys.argv[1])