import os
import unittest

import click
import sys
import os
from flexmock import flexmock

from libs.CompilerUploader import CompilerUploader, CompilerException
from libs.PathsManager import PathsManager as pm
from libs.utils import isWindows, isLinux, isMac


class TestCompilerUploader(unittest.TestCase):
    platformToUse = None

    @classmethod
    def setUpClass(cls):
        cls.platformToUse = cls.__getPlatformToUse()
        print """\n\n
        #######################################
        Remember to connect a {} board
        #######################################\n""".format(cls.platformToUse)

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm

    @classmethod
    def __getPlatformToUse(cls):
        board = os.environ.get("platformioBoard", None)
        if board is None:
            board = filter(lambda x: x.startswith("platformioBoard="), sys.argv)
            if board is None:
                return "uno"
            else:
                return board[0].split("=")[1]
        return board

    def setUp(self):
        self.platformioPath = pm.SETTINGS_PLATFORMIO_PATH
        self.hexFilePath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.srcCopyPath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "srcCopy")
        self.workingCppPath = os.path.join(self.srcCopyPath, "working.cpp")
        self.notWorkingCppPath = os.path.join(self.srcCopyPath, "notWorking.cpp")
        self.withLibrariesCppPath = os.path.join(self.srcCopyPath, "withLibraries.cpp")
        self.connectedBoard = self.platformToUse
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

    def test_compile_CompilesSuccessfullyWithLibraries(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.withLibrariesCppPath) as f:
            withLibrariesCpp = f.read()

        compileResult = self.compiler.compile(withLibrariesCpp)

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
