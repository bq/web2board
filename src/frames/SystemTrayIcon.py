import os
import wx

from libs.PathsManager import PathsManager
from libs.Web2boardApp import getWebBoardApp
from libs import utils

TRAY_TOOLTIP = 'Web2board app'



class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(PathsManager.RES_ICO_PATH)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.showApp)
        self.ShowMessage("Web2boar", "Web2board is running in background", 1000)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, 'Show app', self.showApp)
        menu.AppendSeparator()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def showApp(self, *args):
        w2bGui = getWebBoardApp().w2bGui
        if not w2bGui.IsShown():
            w2bGui.Show()
        w2bGui.Raise()


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

    def ShowMessage(self, *args, **kwargs):
        if not utils.isLinux():
            self.ShowBalloon(*args, **kwargs)

    def RemoveIcon(*args, **kwargs):
        super(TaskBarIcon, args).RemoveIcon(**kwargs)
