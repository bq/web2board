import os
import shutil
import unittest

from Test.testingUtils import restoreAllTestResources
from libs.PathsManager import PathsManager as pm
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Updater import Updater


class TestBitbloqLibsUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = BitbloqLibsUpdater()
        self.updater.destinationPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "newLibrariesPath")
        restoreAllTestResources()

    def test_construct_setsAllNecessaryAttributes(self):
        self.assertIsNotNone(os.path.exists(self.updater.currentVersionInfoPath))
        self.assertIsNotNone(self.updater.currentVersionInfo)
        self.assertIsNotNone(self.updater.onlineVersionUrl)
        self.assertIsNotNone(self.updater.destinationPath)
        self.assertNotEqual(self.updater.name, Updater().name)

    def test_reloadVersions_constructVersionsInfo(self):
        self.updater.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/onlineBitbloqLibsVersionV5.version"
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")

        currentVersionInfo = self.updater.readCurrentVersionInfo()
        onlineVersionInfo = self.updater.downloadOnlineVersionInfo()

        self.assertEqual(currentVersionInfo.version, "0.0.1")
        self.assertEqual(currentVersionInfo.file2DownloadUrl, 'file2DownloadUrl')
        self.assertEqual(onlineVersionInfo.version, "0.0.5")
        self.assertEqual(onlineVersionInfo.file2DownloadUrl,
                         'https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/bitbloqLibsV5.zip')

    def __testUploadProcess(self):
        try:
            onlineVersion = self.updater.downloadOnlineVersionInfo()
            self.updater.update(onlineVersion)
            self.assertTrue(self.updater.currentVersionInfo.version, onlineVersion.version)
            self.assertGreater(len(self.updater.currentVersionInfo.librariesNames), 0)
            self.assertFalse(self.updater._areWeMissingLibraries())
            self.assertFalse(self.updater._isVersionDifferentToCurrent(onlineVersion))
            self.assertFalse(self.updater.isNecessaryToUpdate(onlineVersion))
        finally:
            if os.path.exists(self.updater.destinationPath):
                shutil.rmtree(self.updater.destinationPath)
            self.assertFalse(os.path.exists(self.updater.destinationPath))

    def test_upload_writesLibrariesInDestinationPathWithControlledData(self):
        self.updater.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/onlineBitbloqLibsVersionV5.version"
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")
        self.__testUploadProcess()

    @unittest.skip("skip until we have good urls")
    def test_upload_withRealValues(self):
        self.__testUploadProcess()
