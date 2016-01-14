import os
import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from wshubsapi.utils import WSMessagesReceivedQueue

from frames.Web2boardWindow import Web2boardWindow
from libs.CompilerUploader import CompilerUploader

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.Web2boardApp import getWebBoardApp
from libs.utils import areWeFrozen


class TestSerialMonitorHub(unittest.TestCase):
    def setUp(self):
        global subprocess
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.serialMonitorHub = HubsInspector.getHubInstance(SerialMonitorHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x, lambda x=0: x)
        self.sender = flexmock(isCompiling=lambda: None, isUploading=lambda x: None)

        self.original_compile = self.serialMonitorHub.compilerUploader.compile
        self.original_getPort = self.serialMonitorHub.compilerUploader.getPort


        self.serialMonitorHub.compilerUploader = flexmock(self.serialMonitorHub.compilerUploader,
                                                          compile=None,
                                                          getPort=None)

    def tearDown(self):
        self.serialMonitorHub.compilerUploader.compile = self.original_compile
        self.serialMonitorHub.compilerUploader.getPort = self.original_compile
        removeHubsSubclasses()


    def __PopenChecker(self, args, **kwargs):
        if not areWeFrozen():
            self.assertEqual(args.pop(0), "python")
        self.assertTrue(os.path.exists(args[0]))
        self.assertIn("SerialMonitor", args[0])
        return "Popen"

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.serialMonitorHub.compilerUploader, CompilerUploader)
        self.assertIsNone(self.serialMonitorHub.serialCommunicationProcess)

    def test_startApp_callsStartsSerialMonitorApp(self):
        import wx
        mainApp = getWebBoardApp()
        app = wx.App(False)
        wx = flexmock(wx, BitmapButton=lambda *args, **kwargs: wx.Button)
        mainApp.w2bGui = Web2boardWindow(None, 0)
        original_startSerialMonitorApp = mainApp.w2bGui.startSerialMonitorApp
        try:
            flexmock(mainApp.w2bGui).should_receive("startSerialMonitorApp").once()

            self.serialMonitorHub.startApp()
            wx.CallAfter(app.Exit)
            app.MainLoop()
        finally:
            mainApp.w2bGui.startSerialMonitorApp = original_startSerialMonitorApp
