import os
import shutil
import unittest

from datetime import datetime, timedelta

import time

from libs.Arduino import base

from libs import utils

# do not remove

try:
    from unittest.mock import MagicMock
except:
    from mock import MagicMock


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.myResFolder = os.path.join("Test", "resources", "testUtils")
        self.copyTreeOld = os.path.join(self.myResFolder, "copyTree_old")
        self.copyTreeNew = os.path.join(self.myResFolder, "copyTree_new")
        self.zipPath = os.path.join(self.myResFolder, "zip.zip")
        self.zipFolder = os.path.join(self.myResFolder, "zip")

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

    def test_downloadFile_savesDataInTmpFileWithUrlBaseName(self):
        url = "https://raw.githubusercontent.com/bq/web2board/master/README.md"

        tempFile = utils.downloadFile(url)

        lastModificationFile = os.stat(tempFile).st_mtime
        lastModificationDiff = time.time() - lastModificationFile
        self.assertTrue(abs(lastModificationDiff) < 0.5)
        self.assertIn(base.sys_path.get_tmp_path(), tempFile)

    def test_listDirectoriesInPath(self):
        directories = utils.listDirectoriesInPath(self.myResFolder)

        self.assertEqual(directories, ["copytree_old", "otherDir"])

    def test_extractZip(self):
        utils.extractZip(self.zipPath, self.myResFolder)

        self.assertTrue(os.path.exists(self.zipFolder))
        self.assertTrue(os.path.exists(self.zipFolder + os.sep + "zip.txt"))

