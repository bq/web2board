import os

from libs.PathsManager import PathsManager
from libs.Web2boardApp import getWebBoardApp

TRAY_TOOLTIP = 'Web2board app'

import wx
class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(PathsManager.RES_ICO_PATH)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, lambda *args:getWebBoardApp().w2bGui.Show())
        self.ShowBalloon("Web2boar", "Web2board is running in background", 1000)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, 'Ahow app', lambda *args:getWebBoardApp().w2bGui.Show())
        menu.AppendSeparator()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        os._exit(1)

    def create_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item
