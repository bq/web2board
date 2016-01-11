import os
import shutil
import time
import unittest

import serial.tools.list_ports
from flexmock import flexmock

from libs import utils
import libs.base
from libs.PathsManager import PathsManager


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.myTestFolder = os.path.join(PathsManager.TEST_SETTINGS_PATH, "testUtils")
        self.copyTreeOld = os.path.join(self.myTestFolder, "copytree_old")
        self.copyTreeNew = os.path.join(self.myTestFolder, "copytree_new")
        self.zipPath = os.path.join(self.myTestFolder, "zip.zip")
        self.zipFolder = os.path.join(self.myTestFolder, "zip")

    def tearDown(self):
        if os.path.exists(self.copyTreeNew):
            shutil.rmtree(self.copyTreeNew)
        if os.path.exists(self.zipFolder):
            shutil.rmtree(self.zipFolder)

    def test_getModulePath_returnsThisModulePath(self):
        modulePath = utils.getModulePath()

        self.assertIn(os.path.join("src", "Test"), modulePath)

    def test_getModulePath_getsUnittestPathWithPreviousFrame(self):
        import inspect
        modulePath = utils.getModulePath(inspect.currentframe().f_back)

        self.assertIn("unittest", modulePath)

    def __assertCopyTreeNewHasAllFiles(self):
        self.assertTrue(os.path.exists(self.copyTreeNew))
        self.assertTrue(os.path.exists(self.copyTreeNew + os.path.sep + "01.txt"))
        self.assertTrue(os.path.exists(self.copyTreeNew + os.path.sep + "02.txt"))

    def test_copytree_createsNewFolderIfNotExists(self):
        utils.copytree(self.copyTreeOld, self.copyTreeNew)

        self.__assertCopyTreeNewHasAllFiles()

    def test_copytree_worksEvenWithExistingFolder(self):
        os.mkdir(self.copyTreeNew)

        utils.copytree(self.copyTreeOld, self.copyTreeNew)

        self.__assertCopyTreeNewHasAllFiles()

    def test_copytree_doNotOverwriteExistingFiles(self):
        os.mkdir(self.copyTreeNew)
        txtFilePath = self.copyTreeNew + os.path.sep + "01.txt"
        with open(txtFilePath, "w") as f:
            f.write("01")

        utils.copytree(self.copyTreeOld, self.copyTreeNew)
        with open(txtFilePath, "r") as f:
            fileData = f.read()

        self.__assertCopyTreeNewHasAllFiles()
        self.assertEqual(fileData, "01")

    def test_listDirectoriesInPath(self):
        directories = utils.listDirectoriesInPath(self.myTestFolder)
        directories = map(lambda x: x.lower(), directories)
        self.assertEqual(directories, ["copytree_old", "otherdir"])

    def test_extractZip(self):
        utils.extractZip(self.zipPath, self.myTestFolder)

        self.assertTrue(os.path.exists(self.zipFolder))
        self.assertTrue(os.path.exists(self.zipFolder + os.sep + "zip.txt"))

    def test_listSerialPorts_useSerialLib(self):
        ports = [(1,2,3), (4,5,6)]
        flexmock(serial.tools.list_ports).should_receive("comports").and_return(ports).once()

        self.assertEqual(utils.listSerialPorts(), ports)

    def test_listSerialPorts_filterWithFunction(self):
        portsFilter = lambda x: x[0] == 1
        ports = [(1,2,3), (4,5,6)]
        flexmock(serial.tools.list_ports).should_receive("comports").and_return(ports).once()

        self.assertEqual(utils.listSerialPorts(portsFilter), ports[0:1])