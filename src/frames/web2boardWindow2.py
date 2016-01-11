import threading

import sys
import wx

from frames.Web2boardgui import Web2boardGui
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.wxAsynchronous import WX_Utils

class RedirectText(object):
    def __init__(self, parent):
        self.parent = parent
        self.out = ""

    def write(self, string):
        self.out += string

    def flush(self, *args):
        pass

    def get(self):
        aux = self.out
        self.out = ""
        return aux


class Web2boardWindow(Web2boardGui):
    def __init__(self, parent):
        super(Web2boardWindow, self).__init__(parent)
        self.compileUpdater = getCompilerUploader()
        self.availablePorts = ["AUTO"]
        self.autoPort = None
        self.portCombo.SetSelection(0)

        self.timer = wx.Timer(self, 123456)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.htmlBuffer = ""

        # self.timer.Start(100)  # 1 second interval

        # redirect text here
        self.redir = RedirectText(self)
        sys.stdout = self.redir

        WX_Utils.initDecorators(self)
        wx.CallAfter(self.consoleLog.LoadPage, "http://www.java2s.com/Tutorial/Python/0380__wxPython/LoadwebpagetoHtmlWindow.htm")

    @asynchronous()
    def __getPorts(self):
        self.availablePorts = self.compileUpdater.searchPorts()
        self.onRefreshFinished("como molo")
        self.autoPort = self.compileUpdater.getPort()

    def onRefreshPorts(self, event):
        self.compileUpdater.setBoard("diemilanove")
        self.resfreshPortsButton.Disable()
        self.SetStatusText("Finding ports...")
        self.__getPorts()

    @WX_Utils.onGuiThread()
    def onRefreshFinished(self, test):
        lastPortSelection = self.portCombo.GetStringSelection()
        self.SetStatusText("")
        self.portCombo.Clear()
        portsInCombo = ["AUTO"] + self.availablePorts
        for i, port in enumerate(portsInCombo):
            if port == self.autoPort:
                portsInCombo[i] = self.autoPort + " (auto)"
        self.portCombo.AppendItems(portsInCombo)
        try:
            selectionIndex = portsInCombo.index(lastPortSelection)
        except:
            selectionIndex = 0
        self.portCombo.SetSelection(selectionIndex)

        self.resfreshPortsButton.Enable()

    def onTimer(self, event):
        message = self.redir.get()
        if message != "":
            message = message.replace("\n", "<br/>")
            message = "<b>{}</b>".format(message)
            self.htmlBuffer += message
            self.consoleLog.SetPage(self.htmlBuffer)
            self.consoleLog.Scroll(0,self.consoleLog.GetScrollRange(wx.VERTICAL))

if __name__ == '__main__':
    app = wx.App(False)
    w2bgui = Web2boardWindow(None)
    w2bgui.Show()
    w2bgui.Raise()
    app.MainLoop()
