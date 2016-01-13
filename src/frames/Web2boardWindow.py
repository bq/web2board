import threading

import sys
import wx
from wx._core import PyDeadObjectError

from SerialMonitor import SerialMonitorUI
from frames.Web2boardgui import Web2boardGui
from libs.CompilerUploader import getCompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.Decorators.wxAsynchronous import WX_Utils


class RedirectText(object):
    def __init__(self, parent, originalStdout):
        self.parent = parent
        self.originalStdout = originalStdout
        self.outs = []

    def write(self, string):
        self.outs.append(string)
        self.originalStdout(string)

    def flush(self, *args):
        pass

    def get(self):
        aux = self.outs
        self.outs = []
        return aux


class Web2boardWindow(Web2boardGui):
    def __init__(self, parent, eventsRefreshTime=100):
        super(Web2boardWindow, self).__init__(parent)
        self.compileUpdater = getCompilerUploader()
        self.availablePorts = ["AUTO"]
        self.autoPort = None
        self.portCombo.SetSelection(0)
        self.consoleLog.BeginFontSize(10)

        self.timer = wx.Timer(self, 123456)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.htmlBuffer = ""
        self.actions = []

        if eventsRefreshTime > 0:
            self.timer.Start(300)  # 1 second interval

        # redirect text here
        originalStdout = sys.stdout.write
        self.redir = RedirectText(self, originalStdout)
        sys.stdout = self.redir
        sys.stderr = self.redir
        self.serialMonitor = None
        self.Bind(wx.EVT_CLOSE, self.OnClose)

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
        messages = self.redir.get()
        for message in messages:
            messages = [m.replace("\r", "").replace("\n\n", "") for m in messages if m.strip() != ""]
            self.consoleLog.SetInsertionPoint(self.consoleLog.GetLastPosition())
            if message.startswith("&&&"):
                self.consoleLog.BeginBold()
                message = message.replace("&&&", "")
                fg = message[:3]
                message = message[3:]
                if fg == "red":
                    self.consoleLog.BeginTextColour((255, 0, 0))
                elif fg == "whi":
                    self.consoleLog.BeginTextColour((255, 255, 255))
                elif fg == "mag":
                    self.consoleLog.BeginTextColour((180, 40, 205))
                elif fg == "gre":
                    self.consoleLog.BeginTextColour((0, 180, 0))
                elif fg == "cya":
                    self.consoleLog.BeginTextColour((50, 50, 255))
            self.consoleLog.WriteText(message)
            self.consoleLog.EndTextColour()
            self.consoleLog.EndBold()
        if len(messages) > 0:
            # self.SetStatusText(message)
            wx.CallAfter(self.consoleLog.Scroll, 0, self.consoleLog.GetScrollRange(wx.VERTICAL))
            wx.CallAfter(self.consoleLog.Refresh)

        self.handlePendingActions()

    def handlePendingActions(self):
        actions = self.actions
        while len(actions)>0:
            action = actions.pop(-1)
            if action[0] == "startSerialMonitor":
                self.serialMonitor = SerialMonitorUI(None, action[1])
                self.serialMonitor.Show()
            elif action[0] == "closeSerialMonitor":
                self.serialMonitor.Close()
            elif action[0] == "showApp":
                self.Show()
                self.Raise()

    def startSerialMonitorApp(self, port):
        self.actions.append(["startSerialMonitor", port])

    def closeSerialMonitorApp(self):
        self.actions.append(["closeSerialMonitor"])

    def showApp(self):
        self.actions.append(["showApp"])

    def isSerialMonitorRunning(self):
        try:
            return self.serialMonitor is not None and not self.serialMonitor.isClosed
        except PyDeadObjectError:
            return False

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
