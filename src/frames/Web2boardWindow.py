import threading

import sys
import wx

from SerialMonitor import SerialMonitorUI
from frames.Web2boardgui import Web2boardGui
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.wxAsynchronous import WX_Utils


class RedirectText(object):
    def __init__(self, parent, originalStdout):
        self.parent = parent
        self.originalStdout = originalStdout
        self.out = ""

    def write(self, string):
        self.out += string
        self.originalStdout(string)

    def flush(self, *args):
        pass

    def get(self):
        aux = self.out
        self.out = ""
        return aux


class Web2boardWindow(Web2boardGui):
    def __init__(self, parent, eventsRefreshTime=100):
        super(Web2boardWindow, self).__init__(parent)
        self.compileUpdater = getCompilerUploader()
        self.availablePorts = ["AUTO"]
        self.autoPort = None
        self.portCombo.SetSelection(0)

        self.timer = wx.Timer(self, 123456)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.htmlBuffer = ""
        self.actions = []

        if eventsRefreshTime > 0:
            self.timer.Start(100)  # 1 second interval

        # redirect text here
        originalStdout = sys.stdout.write
        self.redir = RedirectText(self, originalStdout)
        sys.stdout = self.redir
        sys.stderr = self.redir
        self.serialMonitor = None
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        WX_Utils.initDecorators(self)

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
            self.consoleLog.Scroll(0, self.consoleLog.GetScrollRange(wx.VERTICAL))

        self.handlePendingActions()

    def handlePendingActions(self):
        actions = self.actions
        for action in actions:
            if action[0] == "startSerialMonitor":
                self.serialMonitor = SerialMonitorUI(None, action[1])
                self.serialMonitor.Show()
            elif action[0] == "closeSerialMonitor":
                self.serialMonitor.Close()
            elif action[0] == "showApp":
                self.Show()
                self.Raise()
        self.actions = []

    def startSerialMonitorApp(self, port):
        self.actions.append(["startSerialMonitor", port])

    def closeSerialMonitorApp(self):
        self.actions.append(["startSerialMonitor"])

    def showApp(self):
        self.actions.append(["showApp"])

    def isSerialMonitorRunning(self):
        return self.serialMonitor is not None and not self.serialMonitor.isClosed

    def OnClose(self, event):
        # if event.CanVeto():
        #     self.Hide()
        #     return

        self.Destroy()  # you may also do:  event.Skip()
        # since the default event handler does call Destroy(), too


if __name__ == '__main__':
    app = wx.App(False)
    w2bgui = Web2boardWindow(None)
    w2bgui.Show()
    w2bgui.Raise()
    app.MainLoop()
