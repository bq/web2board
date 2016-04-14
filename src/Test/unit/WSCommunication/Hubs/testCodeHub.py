import os
import unittest

from wshubsapi.Hub import UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses

from Test.testingUtils import createCompilerUploaderMock, createSenderMock
from libs.CompilerUploader import CompilerUploader
from libs.MainApp import getMainApp
from libs.WSCommunication.Hubs.CodeHub import CodeHub
from libs.PathsManager import PathsManager as pm
from flexmock import flexmock, flexmock_teardown
# do not remove
import libs.WSCommunication.Hubs


class TestCodeHub(unittest.TestCase):
    def setUp(self):
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.hexFilePath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.codeHub = HubsInspector.getHubInstance(CodeHub)
        """:type : CodeHub"""

        self.sender = createSenderMock()
        getMainApp().w2bGui = flexmock(Web2boardWindow(),
                                       getSelectedPort=lambda *args: None,
                                       isSerialMonitorRunning=lambda: False)

        self.originalConstruct = CompilerUploader.construct
        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()
        self.board = CompilerUploader.DEFAULT_BOARD

    def tearDown(self):
        flexmock_teardown()
        removeHubsSubclasses()

    def test_construct_getsCompilerUploader(self):
        self.assertIsInstance(self.originalConstruct(), CompilerUploader)

    def test_construct_getsCompilerUploaderWithRightBoard(self):
        compiler1 = self.originalConstruct("uno")
        compiler2 = self.originalConstruct("diemilanove")

        self.assertEqual(compiler1.board, "uno")
        self.assertEqual(compiler2.board, "diemilanove")

    def test_construct_getsSameObjectIfPassedSameBoard(self):
        compiler1 = self.originalConstruct("uno")
        compiler2 = self.originalConstruct("uno")

        self.assertIs(compiler1, compiler2)

    def test_compile_senderIsAdvisedCompilingIsOngoing(self):
        self.sender.should_receive("isCompiling").once()

        self.codeHub.compile("myCode", self.sender)

    def test_compile_callsCompilerCompile(self):
        code = "myCode"
        (self.compileUploaderMock
         .should_receive("compile")
         .once()
         .with_args(code)
         .and_return([True, None]))

        self.codeHub.compile(code, self.sender)

    def test_upload_senderIsAdvisedCodeIsUploadingWithPort(self):
        port = "PORT"
        self.compileUploaderMock.should_receive("getPort").and_return(port).once()
        self.compileUploaderMock.should_receive("upload").and_return((True, {})).once()

        self.codeHub.upload("myCode", self.board, self.sender)

    def test_upload_successfulUploadReturnsTrue(self):
        self.compileUploaderMock.should_receive("upload").and_return((True, {})).once()

        result = self.codeHub.upload("myCode", self.board, self.sender)

        self.assertEqual(result, "PORT")

    def test_upload_unsuccessfulUploadReturnsErrorString(self):
        uploadReturn = (False, {"err": "errorMessage"},)
        self.compileUploaderMock.should_receive("upload").and_return(uploadReturn).once()

        result = self.codeHub.upload("myCode", self.board, self.sender)

        self.assertIsInstance(result, UnsuccessfulReplay)
        self.assertEqual(result.replay, uploadReturn[1]["err"])

    def test_uploadHexUrl_successfulHexUploadCallsUploadAvrHexAndReturnsTrue(self):
        self.compileUploaderMock.should_receive("uploadAvrHex").and_return((True, {})).once()

        result = self.codeHub.uploadHex("hexText", self.board, self.sender)

        self.assertEqual(result, "PORT")

    def test_upload_unsuccessfulHexUploadReturnsErrorString(self):
        uploadReturn = (False, {"err": "errorMessage"},)
        self.compileUploaderMock.should_receive("uploadAvrHex").and_return(uploadReturn).once()

        result = self.codeHub.uploadHex("hexText", self.compileUploaderMock.board, self.sender)

        self.assertIsInstance(result, UnsuccessfulReplay)
        self.assertEqual(result.replay, uploadReturn[1]["err"])
