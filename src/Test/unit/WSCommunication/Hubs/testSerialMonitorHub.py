import os
import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from wshubsapi.utils import WSMessagesReceivedQueue

from Test.testingUtils import createCompilerUploaderMock, createSenderMock
from frames.Web2boardWindow import Web2boardWindow
from libs.CompilerUploader import CompilerUploader

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock, flexmock_teardown

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.MainApp import getMainApp
from libs.utils import areWeFrozen


class TestSerialMonitorHub(unittest.TestCase):
    def setUp(self):
        global subprocess
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.serialMonitorHub = HubsInspector.getHubInstance(SerialMonitorHub)
        """:type : SerialMonitorHub"""
        self.serialMonitorHub.compilerUploader = CompilerUploader.construct()
        self.sender = createSenderMock()

        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()

    def tearDown(self):
        flexmock_teardown()
        removeHubsSubclasses()

    def __PopenChecker(self, args, **kwargs):
        if not areWeFrozen():
            self.assertEqual(args.pop(0), "python")
        self.assertTrue(os.path.exists(args[0]))
        self.assertIn("SerialMonitor", args[0])
        return "Popen"

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.serialMonitorHub.compilerUploader, CompilerUploader)

    def test_startApp_callsStartsSerialMonitorApp(self):
        mainApp = getMainApp()
        mainApp.w2bGui = Web2boardWindow(None, 0)
        original_startSerialMonitorApp = mainApp.w2bGui.startSerialMonitorApp
        try:
            flexmock(mainApp.w2bGui).should_receive("startSerialMonitorApp").once()
            self.serialMonitorHub.startApp("COM1", CompilerUploader.DEFAULT_BOARD)
        finally:
            mainApp.w2bGui.startSerialMonitorApp = original_startSerialMonitorApp
