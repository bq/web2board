# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html

###########################################################################
## Class Web2boardGui
###########################################################################

class Web2boardGui ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Web2board", pos = wx.DefaultPosition, size = wx.Size( 726,375 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL, name = u"Web2boardMain" )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.mainPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.portsLabel = wx.StaticText( self.mainPanel, wx.ID_ANY, u"ports", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.portsLabel.Wrap( -1 )
		bSizer2.Add( self.portsLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		portComboChoices = [ u"AUTO" ]
		self.portCombo = wx.ComboBox( self.mainPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), portComboChoices, wx.CB_DROPDOWN|wx.CB_SORT )
		bSizer2.Add( self.portCombo, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.resfreshPortsButton = wx.BitmapButton( self.mainPanel, wx.ID_ANY, wx.Bitmap( u"res/icons/refresh-icon.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizer2.Add( self.resfreshPortsButton, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer2, 0, wx.ALIGN_RIGHT, 5 )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.consoleLog = wx.html.HtmlWindow( self.mainPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		bSizer6.Add( self.consoleLog, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer7.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		
		self.mainPanel.SetSizer( bSizer7 )
		self.mainPanel.Layout()
		bSizer7.Fit( self.mainPanel )
		bSizer1.Add( self.mainPanel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.portCombo.Bind( wx.EVT_COMBOBOX, self.onPortChanged )
		self.resfreshPortsButton.Bind( wx.EVT_BUTTON, self.onRefreshPorts )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onPortChanged( self, event ):
		event.Skip()
	
	def onRefreshPorts( self, event ):
		event.Skip()
	

