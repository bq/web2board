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

serial = serial.Serial()

class SerialMonitorUI(wx.Dialog):

	def __init__(self, parent):
		super(SerialMonitorUI, self).__init__(parent, title='bitbloq\'s Serial Monitor', size=(500,500), style=wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
)
		#Timer
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		self.timer.Start(100)
		self.newLine = ''
		self.Pause = False
		self.charCounter = 0

		# Elements
		self.inputTextBox = wx.TextCtrl(self, size=(300,10))
		self.response = wx.TextCtrl(self, size=(10,250), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
		self.response.SetMaxLength(3)
		self.sendButton = wx.Button(self, label='Send',style = wx.ALIGN_RIGHT)
		self.pauseButton = wx.Button(self, label='Pause',style = wx.ALIGN_RIGHT)
		self.clearButton = wx.Button(self, label='Clear',style = wx.ALIGN_RIGHT)

		baudRates = ['300', '1200', '2400', '4800', '9600', '14400','19200', '28800', '38400', '57600', '115200']
		self.dropdown = wx.ComboBox(self, 0, '9600', (0, 0), wx.DefaultSize ,baudRates, wx.CB_DROPDOWN)

		# Events
		self.sendButton.Bind(wx.EVT_BUTTON, self.onSend)
		self.pauseButton.Bind(wx.EVT_BUTTON, self.onPause)
		self.clearButton.Bind(wx.EVT_BUTTON, self.onClear)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.dropdown.Bind(wx.EVT_COMBOBOX, self.onBaudRateChanged)

		# Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.inputTextBox, 1,wx.ALL^wx.CENTER|wx.EXPAND, 12)
		hbox.Add(self.sendButton, 0, wx.ALL^wx.ALIGN_RIGHT, 12)
		vbox.Add(hbox, 0, wx.EXPAND, 12)
		vbox.Add(self.response, 1, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.pauseButton, 0, wx.ALL^wx.ALIGN_LEFT, 12)
		hbox1.Add(self.clearButton, 0, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		hbox1.Add((0, 0), 1, wx.EXPAND)
		hbox1.Add(self.dropdown, 0, wx.ALL^wx.ALIGN_RIGHT, 12)
		vbox.Add(hbox1, 0, wx.EXPAND, 12)
		self.SetSizer(vbox)
		self.ShowModal()



	def logText (self, message):
		if '\n' in message:
			self.charCounter = 0
		else:
			self.charCounter+=1

		if self.response.GetNumberOfLines() >= 800 or self.charCounter > 300:
			self.response.SetValue(message)
			self.charCounter = 0
		else:
			self.response.AppendText(message)

	def update(self, event):
		if serial.isOpen():
			out = ''
			try:
				while serial.inWaiting() > 0:
					out += serial.read(1)
				if out != '' and self.Pause == False:
					self.logText(out)
			except:
				pass

	def onSend(self, event):
		message = self.inputTextBox.GetValue()
		self.logText(message)
		serial.write(message)
		self.inputTextBox.SetValue('')

	def onPause (self, event):
		if self.pauseButton.GetLabel() == 'Pause':
			self.pauseButton.SetLabel('Continue')
			self.Pause = True
		else:
			self.pauseButton.SetLabel('Pause')
			self.Pause = False

	def onClear (self, event):
		self.response.SetValue('')
		self.inputTextBox.SetValue('')
		self.charCounter = 0

	def onBaudRateChanged (self, event):
		qBaudRate.put(self.dropdown.GetValue())

	def onClose(self, event):
		serial.close()
		time.sleep(0.5)
		os._exit(1)
		self.Destroy()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'USAGE: SerialMonitor << port >>'
		sys.exit(1)
	else:
		serial.port = sys.argv[1]
		serial.baudrate = 9600
		serial.open()

		# app = wx.App(redirect=True)
		app = wx.App()
		serialMonitor = SerialMonitorUI(None)
		serialMonitor.Show()
		app.MainLoop()