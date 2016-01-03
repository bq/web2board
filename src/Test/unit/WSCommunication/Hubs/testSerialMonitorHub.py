import os
import subprocess
import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.Hub import UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from libs.CompilerUploader import CompilerUploader

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.utils import areWeFrozen


class TestSerialMonitorHub(unittest.TestCase):
    def setUp(self):
        global subprocess
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.serialMonitorHub = HubsInspector.getHubInstance(SerialMonitorHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x, lambda x=0: x)
        self.sender = flexmock(isCompiling=lambda: None, isUploading=lambda x: None)
        self.serialMonitorHub.compilerUploader = flexmock(self.serialMonitorHub.compilerUploader,
                                                          compile=None,
                                                          getPort=None)
        self.originalSubprocessPopen = subprocess.Popen

        subprocess.Popen = self.__PopenChecker

    def __PopenChecker(self, args, **kwargs):
        if not areWeFrozen():
            self.assertEqual(args.pop(0), "python")
        self.assertTrue(os.path.exists(args[0]))
        self.assertIn("SerialMonitor", args[0])
        return "Popen"

    def tearDown(self):
        global subprocess
        removeHubsSubclasses()
        subprocess.Popen = self.originalSubprocessPopen

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.serialMonitorHub.compilerUploader, CompilerUploader)
        self.assertIsNone(self.serialMonitorHub.serialCommunicationProcess)

    def test_startApp_callsPopenWithRightSerialMonitorPath(self):
        self.serialMonitorHub.startApp()

        self.assertEqual(self.serialMonitorHub.serialCommunicationProcess, "Popen")
