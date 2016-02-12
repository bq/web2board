import os
import sys
import unittest
from pprint import pprint

import click
from PySide.QtGui import QApplication
from flexmock import flexmock

from Test.testingUtils import restoreAllTestResources
from libs.CompilerUploader import CompilerUploader, CompilerException
from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager as pm
from libs.utils import isWindows, isLinux, isMac

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
        if cls is None:
            try:
                cls.portToUse = CompilerUploader.construct(cls.__getPlatformToUse()).getPort()
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
        self.platformioPath = pm.PLATFORMIO_WORKSPACE_PATH
        self.hexFilePath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "hex.hex")
        self.srcCopyPath = os.path.join(pm.TEST_SETTINGS_PATH, "CompilerUploader", "srcCopy")
        self.workingCppPath = os.path.join(self.srcCopyPath, "working.cpp")
        self.notWorkingCppPath = os.path.join(self.srcCopyPath, "notWorking.cpp")
        self.withLibrariesCppPath = os.path.join(self.srcCopyPath, "withLibraries.cpp")
        self.connectedBoard = self.platformToUse
        self.compiler = CompilerUploader.construct(self.__getPlatformToUse())

        self.original_searchPorts = self.compiler._searchBoardPort
        restoreAllTestResources()

    def tearDown(self):
        self.compiler._searchBoardPort = self.original_searchPorts

    def test_getPort_raisesExceptionIfBoardNotSet(self):
        self.compiler.board = None
        self.assertRaises(CompilerException, self.compiler.getPort)

    def test_getPort_raiseExceptionIfNotReturningPort(self):
        self.compiler = flexmock(self.compiler, _searchBoardPort=lambda: None)

        self.compiler.setBoard('uno')

        self.assertRaises(CompilerException, self.compiler.getPort)

    def test_getPort_returnPortIfSearchPortsReturnsOnePort(self):
        self.compiler = flexmock(self.compiler, _searchBoardPort=lambda: 1)
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

    def test_compile_raisesExceptionIfBoardIsNotSet(self):
        self.compiler.board = None
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        self.assertRaises(CompilerException, self.compiler.compile, workingCpp)

    def test_compile_compilesSuccessfullyWithWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        compileResult = self.compiler.compile(workingCpp)

        self.assertTrue(compileResult[0])

    def test_compile_compilesSuccessfullyWithLibraries(self):
        self.compiler.setBoard(self.connectedBoard)
        with open(self.withLibrariesCppPath) as f:
            withLibrariesCpp = f.read()

        compileResult = self.compiler.compile(withLibrariesCpp)
        pprint(compileResult)
        self.assertTrue(compileResult[0])

    def test_compile_resultErrorIsFalseUsingNotWorkingCpp(self):
        self.compiler.setBoard(self.connectedBoard)
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

        self.assertRaises(CompilerException, self.compiler.upload, workingCpp, uploadPort=self.portToUse)

    def test_upload_compilesSuccessfullyWithWorkingCpp(self):
        self.__assertPortFount()
        self.compiler.setBoard(self.connectedBoard)
        with open(self.workingCppPath) as f:
            workingCpp = f.read()

        uploadResult = self.compiler.upload(workingCpp, uploadPort=self.portToUse)

        pprint(uploadResult)
        self.assertTrue(uploadResult[0])

    def test_upload_resultErrorIsFalseUsingNotWorkingCpp(self):
        self.__assertPortFount()
        self.compiler.setBoard(self.connectedBoard)
        with open(self.notWorkingCppPath) as f:
            notWorkingCpp = f.read()

        uploadResult = self.compiler.upload(notWorkingCpp, uploadPort=self.portToUse)

        pprint(uploadResult)
        self.assertFalse(uploadResult[0])

    def test_uploadAvrHex_returnsOkResultWithWorkingHexFile(self):
        self.__assertPortFount()
        self.compiler.setBoard(self.connectedBoard)
        result = self.compiler.uploadAvrHex(self.hexFilePath, uploadPort=self.portToUse)

        self.assertTrue(result[0])

    def test_uploadAvrHex_returnsBadResultWithNonExistingFile(self):
        self.__assertPortFount()
        self.compiler.setBoard(self.connectedBoard)

        result = self.compiler.uploadAvrHex("notExistingFile", uploadPort=self.portToUse)

        self.assertFalse(result[0])

