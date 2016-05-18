import os
import sys
import unittest
from pprint import pprint

import click
from PySide.QtGui import QApplication
from flexmock import flexmock, flexmock_teardown

from Test.testingUtils import restore_test_resources
from libs.CompilerUploader import CompilerUploader, CompilerException
from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager as pm
from libs.utils import is_windows, is_linux, is_mac

log = initLogging(__name__)
try:
    QApplication(sys.argv)
except:
    pass


class TestCompilerUploader(unittest.TestCase):
    platformToUse = None
    portToUse = None

    @classmethod
    def setUpClass(cls):
        if cls.portToUse is None:
            try:
                cls.portToUse = CompilerUploader.construct(cls.__getPlatformToUse()).get_port()
            except:
                cls.portToUse = -1
        cls.platformToUse = cls.__getPlatformToUse()
        log.info("""\n\n
        #######################################
        Remember to connect a {} board
        #######################################\n""".format(cls.platformToUse))

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm

    @classmethod
    def __getPlatformToUse(cls):
        board = os.environ.get("platformioBoard", None)
        if board is None:
            raise Exception("No board defined")
        return board

    def setUp(self):
        self.platformioPath = pm.PLATFORMIO_WORKSPACE_SKELETON
        self.hexFilePath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.srcCopyPath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "srcCopy")
        self.workingCppPath = os.path.join(self.srcCopyPath, "working.ino")
        self.notWorkingCppPath = os.path.join(self.srcCopyPath, "notWorking.ino")
        self.withLibrariesCppPath = os.path.join(self.srcCopyPath, "withLibraries.ino")
        self.connectedBoard = self.platformToUse
        self.compiler = CompilerUploader.construct(self.__getPlatformToUse())

        restore_test_resources()

    def tearDown(self):
        flexmock_teardown()

    def test_getPort_raisesExceptionIfBoardNotSet(self):
        self.compiler.board = None
        self.assertRaises(CompilerException, self.compiler.get_port)

    def test_getPort_raiseExceptionIfNotReturningPort(self):
        self.compiler = flexmock(self.compiler, _search_board_port=lambda: None)

        self.compiler.set_board('uno')

        self.assertRaises(CompilerException, self.compiler.get_port)

    def test_getPort_raiseExceptionIfNotAvailablePort(self):
        self.compiler = flexmock(self.compiler, get_available_ports=lambda: [])

        self.compiler.set_board('uno')

        self.assertRaises(CompilerException, self.compiler.get_port)

    def test_getPort_returnPortIfSearchPortsReturnsOnePort(self):
        self.compiler = flexmock(self.compiler, _search_board_port=lambda: 1)
        self.compiler.set_board('uno')

        port = self.compiler.get_port()

        self.assertEqual(port, 1)

    def __assertRightPortName(self, port):
        if is_windows():
            self.assertTrue(port.startswith("COM"))
        elif is_linux():
            self.assertTrue(port.startswith("/dev/tty"))
        elif is_mac():
            self.assertTrue(port.startswith("/dev/"))

    def test_getPort_returnsBoardConnectedBoard(self):
        self.compiler.set_board(self.connectedBoard)

        port = self.compiler.get_port()

        self.__assertRightPortName(port)

    def test_compile_raisesExceptionIfBoardIsNotSet(self):
        self.compiler.board = None
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        self.assertRaises(CompilerException, self.compiler.compile, workingCpp)

    def test_compile_compilesSuccessfullyWithWorkingCpp(self):
        self.compiler.set_board(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        compileResult = self.compiler.compile(workingCpp)

        self.assertTrue(compileResult[0])

    def test_compile_compilesSuccessfullyWithLibraries(self):
        self.compiler.set_board(self.connectedBoard)
        with open(self.withLibrariesCppPath) as f:
            withLibrariesCpp = f.read()

        compileResult = self.compiler.compile(withLibrariesCpp)
        pprint(compileResult)
        self.assertTrue(compileResult[0])

    def test_compile_resultErrorIsFalseUsingNotWorkingCpp(self):
        self.compiler.set_board(self.connectedBoard)
        with open(self.notWorkingCppPath) as f:
            notWorkingCpp = f.read()

        compileResult = self.compiler.compile(notWorkingCpp)
        pprint(compileResult)
        self.assertFalse(compileResult[0])

    def __assertPortFount(self):
        if self.portToUse == -1:
            self.assertFalse(True, "port not found, check board: {} is connected".format(self.connectedBoard))

    def test_upload_raisesExceptionIfBoardIsNotSet(self):
        self.__assertPortFount()
        self.compiler.board = None
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        self.assertRaises(CompilerException, self.compiler.upload, workingCpp, upload_port=self.portToUse)

    def test_upload_compilesSuccessfullyWithWorkingCpp(self):
        self.__assertPortFount()
        self.compiler.set_board(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        uploadResult = self.compiler.upload(workingCpp, upload_port=self.portToUse)

        pprint(uploadResult)
        self.assertTrue(uploadResult[0])

    def test_upload_resultErrorIsFalseUsingNotWorkingCpp(self):
        self.__assertPortFount()
        self.compiler.set_board(self.connectedBoard)
        with open(self.notWorkingCppPath) as f:
            notWorkingCpp = f.read()

        uploadResult = self.compiler.upload(notWorkingCpp, upload_port=self.portToUse)

        pprint(uploadResult)
        self.assertFalse(uploadResult[0])

    def test_uploadAvrHex_returnsOkResultWithWorkingHexFile(self):
        self.__assertPortFount()
        self.compiler.set_board(self.connectedBoard)
        path = os.path.relpath(self.hexFilePath, os.getcwd())
        result = self.compiler.upload_avr_hex(path, upload_port=self.portToUse)
        print(result[1])
        self.assertTrue(result[0])

    def test_uploadAvrHex_returnsBadResultWithNonExistingFile(self):
        self.__assertPortFount()
        self.compiler.set_board(self.connectedBoard)

        result = self.compiler.upload_avr_hex("notExistingFile", upload_port=self.portToUse)

        self.assertFalse(result[0])

