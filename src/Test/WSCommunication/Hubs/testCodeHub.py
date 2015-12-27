import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.ConnectedClientsGroup import ConnectedClientsGroup
from wshubsapi.Hub import UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from libs.CompilerUploader import CompilerUploader
from libs.WSCommunication.Hubs.CodeHub import CodeHub

# do not remove
import libs.WSCommunication.Hubs

try:
    from unittest.mock import MagicMock
except:
    from mock import MagicMock


class TestCommProtocol(unittest.TestCase):
    def setUp(self):
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.codeHub = HubsInspector.getHubInstance(CodeHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x, lambda x=0: x)
        self.sender = ConnectedClientsGroup([client], "hub")
        self.sender.isCompiling = MagicMock()
        self.sender.isUploading = MagicMock()
        self.codeHub.compilerUploader.compile = MagicMock()

    def tearDown(self):
        removeHubsSubclasses()

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.codeHub.compilerUploader, CompilerUploader)

    def test_compile_senderIsAdvisedCompilingIsOngoing(self):
        self.codeHub.compilerUploader.compile = MagicMock()

        self.codeHub.compile("myCode", self.sender)

        self.assertTrue(self.sender.isCompiling.called)

    def test_compile_callsCompilerCompile(self):
        code = "myCode"

        self.codeHub.compile(code, self.sender)

        self.assertEqual(self.codeHub.compilerUploader.compile.call_args[0][0], code)

    def test_upload_senderIsAdvisedCodeIsUploadingWithPort(self):
        port = "PORT"
        self.codeHub.compilerUploader.getPort = MagicMock(return_value=port)
        self.codeHub.compilerUploader.upload = MagicMock(return_value={"status": "OK"})

        self.codeHub.upload("myCode", self.sender)

        self.assertEqual(self.sender.isUploading.call_args[0][0], port)

    def test_upload_successfulUploadReturnsTrue(self):
        self.codeHub.compilerUploader.getPort = MagicMock()
        self.codeHub.compilerUploader.upload = MagicMock(return_value={"status": "OK"})

        result = self.codeHub.upload("myCode", self.sender)

        self.assertEqual(result, True)

    def test_upload_unsuccessfulUploadReturnsErrorString(self):
        uploadReturn = {"status": "KO", "error": "errorMessage"}
        self.codeHub.compilerUploader.getPort = MagicMock()
        self.codeHub.compilerUploader.upload = MagicMock(return_value=uploadReturn)

        result = self.codeHub.upload("myCode", self.sender)

        self.assertIsInstance(result, UnsuccessfulReplay)
        self.assertEqual(result.replay, uploadReturn["error"])

    # todo: test serialMonitor open in upload
