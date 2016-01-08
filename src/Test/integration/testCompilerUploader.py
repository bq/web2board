import os
import unittest

import click
from flexmock import flexmock

from libs.CompilerUploader import CompilerUploader, CompilerException
from libs.PathsManager import TEST_RES_PATH, SETTINGS_PLATFORMIO_PATH, TEST_SETTINGS_PATH
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
        global SETTINGS_PLATFORMIO_PATH
        self.originalSettingsPlatformioPath = SETTINGS_PLATFORMIO_PATH
        self.compiler = CompilerUploader()
        self.platformioPath = os.path.join(TEST_SETTINGS_PATH, "platformio")
        self.hexFilePath = os.path.join(TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        SETTINGS_PLATFORMIO_PATH = self.platformioPath
        self.workingCppPath = os.path.join(self.platformioPath, "src", "working.cpp")
        self.notWorkingCppPath = os.path.join(self.platformioPath, "src", "notWorking.cpp")
        self.connectedBoard = 'diemilanove'

    def tearDown(self):
        global SETTINGS_PLATFORMIO_PATH
        SETTINGS_PLATFORMIO_PATH = self.originalSettingsPlatformioPath

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
        self.assertEqual(compileResult[1]["err"], "")

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
        self.compiler = flexmock(self.compiler, getPort="COM3") #todo: remove this line
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
