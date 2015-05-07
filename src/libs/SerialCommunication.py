#!/usr/bin/python

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
from wx.lib.newevent import NewEvent


class SerialCommunication:
	def __init__(self, board=None, port=None):
		self.board = board
		self.port = port

	def setBoard (self, board):
		self.board = board
	def setPort (self,port=''):
		self.port = port
	def getPort (self):
		return self.port
	def getBoard(self):
		return self.board
	def setBaudrate (self, baudRate):
		self.baudRate = baudRate

	def initializeSerial (self, port, baudRate):
		self.serial = serial.Serial(
			port=port,
			baudrate=baudRate,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS
		)
		# self.close()

	def open(self):
		self.serial.open()
		self.serial.isOpen()

	def close (self):
		self.serial.close()

	def write (self, data):
		self.serial.write(data)

	def read (self):
		out = ''
		while self.serial.inWaiting() > 0:
			out += self.serial.read(1)
		if out != '':
			return out




qBoard = Queue()
qMonitor = Queue()


class SerialMonitor:
	def __init__(self, board, port, baudRate = 9600):
		self.serialCom = SerialCommunication()
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


	def readQmonitor(self):
		print 'Enter your commands below.\r\nInsert "exit" to leave the application.'
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




class SerialMonitorUI(wx.Dialog):

	def __init__(self, parent):
		super(SerialMonitorUI, self).__init__(parent, title='Pattern distance', size=(500,500), style=wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
)
		#Timer
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		self.timer.Start(10)
		self.newLine = '\n'


		# Elements
		self.inputTextBox = wx.TextCtrl(self, size=(300,20), style = wx.EXPAND)
		self.response = wx.TextCtrl(self, size=(10,250), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
		self.sendButton = wx.Button(self, label='Send')
		self.checkBox = wx.CheckBox(self, -1, 'NewLine', (10, 10))
		self.checkBox.SetValue(True)

		# Events
		self.sendButton.Bind(wx.EVT_BUTTON, self.onSend)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.checkBox.Bind(wx.EVT_CHECKBOX, self.onBoxChanged)
		# Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.inputTextBox, 1, wx.ALL^wx.LEFT|wx.EXPAND, 12)
		hbox.Add(self.sendButton, 0, wx.ALL^wx.RIGHT, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 10)
		vbox.Add(self.response, 1, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		vbox.Add(self.checkBox, 0, wx.ALL^wx.CENTER|wx.EXPAND, 12)
		self.SetSizer(vbox)
		self.ShowModal()

	def update(self, event):
		if not qBoard.empty():
			message = qBoard.get()
			self.response.AppendText(message+self.newLine)

	def onSend(self, event):
		message = self.inputTextBox.GetValue()
		self.response.AppendText(message+self.newLine)
		qMonitor.put(message)
		self.inputTextBox.SetValue('')

	def onBoxChanged (self, event):
		if self.newLine =='\n':
			self.newLine=''
		else:
			self.newLine='\n'

	def onClose(self, event):
		print 'onClose'
		qMonitor.put('exitWeb2boardPythonProgram')
		self.Destroy()