import json
import os
import unittest

import shutil
from flexmock import flexmock

from Test.testingUtils import restoreAllTestResources
from libs.PathsManager import PathsManager as pm
from libs.Updaters.Updater import Updater, VersionInfo
from libs import utils

versionTestData = {
    "version": "9.9.9",
    "file2DownloadUrl": "file2DownloadUrl",
    "librariesNames": ["l1"]
}

onlineVersionTestData = {
    "version": "90.90.90",
    "file2DownloadUrl": "file2DownloadUrl",
}


class TestUpdater(unittest.TestCase):
    ORIGINAL_DOWNLOAD_ZIP_PATH = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "bitbloqLibsV1.zip")
    COPY_DOWNLOAD_ZIP_PATH = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "copy_000.zip")

    def setUp(self):
        self.updater = Updater()
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")
        self.updater.onlineVersionUrl = "onlineVersionUrl"
        self.updater.destinationPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "destinationPath")

        self.original_getDataFromUrl = utils.getDataFromUrl
        self.original_downloadFile = utils.downloadFile
        self.original_extractZip = utils.extractZip
        self.original_listDirsInPath = utils.listDirectoriesInPath
        self.original_json_dump = json.dump

        restoreAllTestResources()

        self.zipToClearPath = None

    def tearDown(self):
        utils.getDataFromUrl = self.original_getDataFromUrl
        utils.downloadFile = self.original_downloadFile
        utils.extractZip = self.original_extractZip
        utils.listDirectoriesInPath = self.original_listDirsInPath
        json.dump = self.original_json_dump

        for libraryName in versionTestData["librariesNames"]:
            if os.path.exists(self.updater.destinationPath + os.sep + libraryName):
                shutil.rmtree(self.updater.destinationPath + os.sep + libraryName)
        if os.path.exists(self.COPY_DOWNLOAD_ZIP_PATH):
            os.remove(self.COPY_DOWNLOAD_ZIP_PATH)

        if os.path.exists(self.updater.destinationPath):
            shutil.rmtree(self.updater.destinationPath)

    def __getMockForGetDataFromUrl(self, returnValue=json.dumps(versionTestData)):
        return flexmock(utils).should_receive("getDataFromUrl").and_return(returnValue)

    def __getMockForDownloadFile(self):
        shutil.copy2(self.ORIGINAL_DOWNLOAD_ZIP_PATH, self.COPY_DOWNLOAD_ZIP_PATH)
        return flexmock(utils).should_receive("downloadFile").and_return(self.COPY_DOWNLOAD_ZIP_PATH)

    def __getMockForExtractZip(self):
        return flexmock(utils).should_receive("extractZip")

    def test_downloadOnlineVersionInfo_setsOnlineVersionInfoValues(self):
        self.__getMockForGetDataFromUrl().once()

        onlineVersionInfo = self.updater.downloadOnlineVersionInfo()

        self.assertEqual(onlineVersionInfo.version, "9.9.9")
        self.assertEqual(onlineVersionInfo.librariesNames, ["l1"])

    def test_isNecessaryToUpdate_raiseExceptionIfCurrentVersionIsNone(self):
        self.updater.onlineVersionInfo = VersionInfo(**onlineVersionTestData)

        with self.assertRaises(Exception):
            self.updater.isNecessaryToUpdate()

    def test_isNecessaryToUpdate_returnsTrueIfVersionsAreDifferent(self):
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.updater.onlineVersionInfo = VersionInfo(**onlineVersionTestData)
        self.updater.currentVersionInfo.version = "0.1.1"

        self.assertTrue(self.updater.isNecessaryToUpdate())

    def test_isNecessaryToUpdate_returnsTrueIfDestinationPathDoesNotExist(self):
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.updater.onlineVersionInfo = VersionInfo(**versionTestData)
        if os.path.exists(self.updater.destinationPath):
            shutil.rmtree(self.updater.destinationPath)

        self.assertTrue(self.updater.isNecessaryToUpdate())

    def test_isNecessaryToUpdate_returnsTrueIfVersionsAreEqualButNoLibrariesInDestinationPath(self):
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.updater.onlineVersionInfo = VersionInfo(**versionTestData)
        os.makedirs(self.updater.destinationPath)

        self.assertTrue(self.updater.isNecessaryToUpdate())

    def test_isNecessaryToUpdate_returnsTrueIfVersionsAreEqualAndLibrariesInDestinationPath(self):
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.updater.onlineVersionInfo = VersionInfo(**versionTestData)
        for libraryName in versionTestData["librariesNames"]:
            if not os.path.exists(self.updater.destinationPath + os.sep + libraryName):
                os.makedirs(self.updater.destinationPath + os.sep + libraryName)

        self.assertFalse(self.updater.isNecessaryToUpdate())

    def test_update_raiseExceptionIfOnlineVersionIsNone(self):
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.__getMockForDownloadFile().never()
        self.__getMockForExtractZip().never()
        flexmock(json).should_receive("dump").never()

        with self.assertRaises(Exception):
            self.updater.update(self.updater.currentVersionInfo)

    def test_update_updatesCurrentVersionInfo(self):
        self.__getMockForGetDataFromUrl()
        self.__getMockForDownloadFile().once()
        self.__getMockForExtractZip().once()
        os.makedirs(self.updater.destinationPath)
        flexmock(utils).should_receive("listDirectoriesInPath").and_return(["l1", "l2"])
        self.updater.currentVersionInfo = VersionInfo(**versionTestData)
        self.updater._moveDownloadedToDestinationPath = lambda x: x
        onlineVersionInfo = VersionInfo(**onlineVersionTestData)

        self.updater.update(onlineVersionInfo)

        self.assertEqual(self.updater.currentVersionInfo.librariesNames, ["l1", "l2"])
        self.assertEqual(self.updater.currentVersionInfo.version, onlineVersionInfo.version)
        self.assertEqual(self.updater.currentVersionInfo.version, onlineVersionInfo.version)
        self.assertFalse(self.updater._areWeMissingLibraries())
        self.assertFalse(self.updater._isVersionDifferentToCurrent(onlineVersionInfo))
        self.assertFalse(self.updater.isNecessaryToUpdate())

    @unittest.skip("_moveDownloadedToDestinationPath is not implemented in Updater")
    def test_update_MoveExtractedFolderToDestinationFolder(self):
        try:
            self.__getMockForGetDataFromUrl()
            self.__getMockForDownloadFile().once()

            self.updater.update(reloadVersions=True)

            self.assertTrue(len(os.listdir(self.updater.destinationPath)) > 0)
        finally:
            if os.path.exists(self.updater.destinationPath):
                shutil.rmtree(self.updater.destinationPath)
