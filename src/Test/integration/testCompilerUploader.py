import os
import unittest

import click
from flexmock import flexmock

from libs.CompilerUploader import CompilerUploader, CompilerException
from libs.PathsManager import PathsManager
from libs.utils import isWindows, isLinux, isMac


class TestCompilerUploader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print """\n\n\n
        #######################################
        Remember to connect a arduino uno board
        #######################################\n"""

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm

    def setUp(self):
        self.platformioPath = PathsManager.SETTINGS_PLATFORMIO_PATH
        self.hexFilePath = os.path.join(PathsManager.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.workingCppPath = os.path.join(PathsManager.TEST_SETTINGS_PATH, "CompilerUploader", "srcCopy", "working.cpp")
        self.notWorkingCppPath = os.path.join(PathsManager.TEST_SETTINGS_PATH, "CompilerUploader", "srcCopy", "notWorking.cpp")
        self.connectedBoard = 'diemilanove'
        self.compiler = CompilerUploader()

    def test_getPort_raisesExceptionIfBoardNotSet(self):
        self.assertIsNone(self.compiler.board)
        self.assertRaises(CompilerException, self.compiler.getPort)

    def test_getPort_raiseExceptionIfNotReturningPort(self):
        self.compiler = flexmock(CompilerUploader(), _searchPorts=lambda x, y: [])

        self.compiler.setBoard('uno')

        self.assertRaises(CompilerException, self.compiler.getPort)

    def test_getPort_raiseExceptionIfReturnsMoreThanOnePort(self):
        self.compiler = flexmock(CompilerUploader(), _searchPorts=lambda x, y: [1, 2])
        self.compiler.setBoard('uno')

        self.assertRaises(CompilerException, self.compiler.getPort)

    def test_getPort_returnPortIfSearchPortsReturnsOnePort(self):
        self.compiler = flexmock(CompilerUploader(), _searchPorts=lambda x, y: [1])
        self.compiler.setBoard('uno')

        port = self.compiler.getPort()

        self.assertEqual(port, 1)

    def __assertRightPortName(self, port):
        if isWindows():
            self.assertTrue(port.startswith("COM"))
        elif isLinux():
            self.assertTrue(port.startswith("/dev/tty"))
        elif isMac():
            self.assertTrue(port.startswith("/dev/"))

    def test_getPort_returnsBoardConnectedBoard(self):
        self.compiler.setBoard(self.connectedBoard)

        port = self.compiler.getPort()

        self.__assertRightPortName(port)

    def test_compile_RaisesExceptionIfBoardIsNotSet(self):
        self.assertIsNone(self.compiler.board)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        self.assertRaises(CompilerException, self.compiler.compile, workingCpp)

    def test_compile_CompilesSuccessfullyWithWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        compileResult = self.compiler.compile(workingCpp)

        self.assertTrue(compileResult[0])

    def test_compile_ResultErrorIsFalseUsingNotWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.notWorkingCppPath) as f:
            notWorkingCpp = f.read()

        compileResult = self.compiler.compile(notWorkingCpp)

        self.assertFalse(compileResult[0])
        self.assertNotEqual(compileResult[1]["err"], "")

    def test_upload_RaisesExceptionIfBoardIsNotSet(self):
        self.assertIsNone(self.compiler.board)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        self.assertRaises(CompilerException, self.compiler.upload, workingCpp)

    def test_upload_CompilesSuccessfullyWithWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        compileResult = self.compiler.upload(workingCpp)

        self.assertTrue(compileResult[0])

    def test_upload_ResultErrorIsFalseUsingNotWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.notWorkingCppPath) as f:
            notWorkingCpp = f.read()

        compileResult = self.compiler.upload(notWorkingCpp)

        self.assertFalse(compileResult[0])

    def test_uploadAvrHex_CompilesSuccessfullyWithWorkingHexFile(self):
        self.compiler.setBoard(self.connectedBoard)
        output, err = self.compiler.uploadAvrHex(self.hexFilePath)

        self.assertTrue("done.  Thank you" in output or "done.  Thank you" in err)
