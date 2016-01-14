import os
import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.Hub import UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from libs.CompilerUploader import CompilerUploader
from libs.WSCommunication.Hubs.CodeHub import CodeHub
# do not remove
import libs.WSCommunication.Hubs
from libs.PathsManager import PathsManager as pm
from flexmock import flexmock


class TestCodeHub(unittest.TestCase):
    def setUp(self):
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.hexFilePath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.codeHub = HubsInspector.getHubInstance(CodeHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x, lambda x=0: x)
        self.sender = flexmock(isCompiling=lambda: None, isUploading=lambda x: None)

        self.original_compile = self.codeHub.compilerUploader.compile
        self.original_getPort = self.codeHub.compilerUploader.getPort

        self.codeHub.compilerUploader = flexmock(self.codeHub.compilerUploader,
                                                 compile=None,
                                                 getPort=None)

    def tearDown(self):
        self.codeHub.compilerUploader.compile = self.original_compile
        self.codeHub.compilerUploader.getPort = self.original_compile
        removeHubsSubclasses()

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.codeHub.compilerUploader, CompilerUploader)

    def test_compile_senderIsAdvisedCompilingIsOngoing(self):
        self.sender.should_receive("isCompiling").once()

        self.codeHub.compile("myCode", self.sender)

    def test_compile_callsCompilerCompile(self):
        code = "myCode"
        (self.codeHub.compilerUploader
         .should_receive("compile")
         .once()
         .with_args(code))

        self.codeHub.compile(code, self.sender)

    def test_upload_senderIsAdvisedCodeIsUploadingWithPort(self):
        port = "PORT"
        self.codeHub.compilerUploader.should_receive("getPort").and_return(port).once()
        self.codeHub.compilerUploader.should_receive("upload").and_return((True,{})).once()

        self.codeHub.upload("myCode", self.sender)

    def test_upload_successfulUploadReturnsTrue(self):
        self.codeHub.compilerUploader.should_receive("upload").and_return((True,{})).once()

        result = self.codeHub.upload("myCode", self.sender)

        self.assertEqual(result, True)

    def test_upload_unsuccessfulUploadReturnsErrorString(self):
        uploadReturn = (False,{"err": "errorMessage"},)
        self.codeHub.compilerUploader.should_receive("upload").and_return(uploadReturn).once()

        result = self.codeHub.upload("myCode", self.sender)

        self.assertIsInstance(result, UnsuccessfulReplay)
        self.assertEqual(result.replay, uploadReturn[1]["err"])

    def test_uploadHexUrl_successfulHexUploadCallsUploadAvrHexAndReturnsTrue(self):
        self.codeHub.compilerUploader.should_receive("uploadAvrHex").and_return((True,{})).once()

        result = self.codeHub.uploadHex("hexText", self.sender)

        self.assertTrue(result)

    def test_upload_unsuccessfulHexUploadReturnsErrorString(self):
        uploadReturn = (False,{"err": "errorMessage"},)
        self.codeHub.compilerUploader.should_receive("uploadAvrHex").and_return(uploadReturn).once()

        result = self.codeHub.uploadHex("hexText", self.sender)

        self.assertIsInstance(result, UnsuccessfulReplay)
        self.assertEqual(result.replay, uploadReturn[1]["err"])

