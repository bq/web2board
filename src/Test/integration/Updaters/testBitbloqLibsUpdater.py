import json
import os
import unittest

import shutil
from flexmock import flexmock

from libs.PathsManager import PathsManager as pm
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Updater import Updater, VersionInfo
from libs import utils

class TestBitbloqUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = BitbloqLibsUpdater()

    def test_construct_setsAllNecessaryAttributes(self):
        self.assertIsNotNone(os.path.exists(self.updater.currentVersionInfoPath))
        self.assertIsNotNone(self.updater.currentVersionInfo)
        self.assertIsNotNone(self.updater.onlineVersionUrl)
        self.assertIsNotNone(self.updater.onlineVersionInfo)
        self.assertIsNotNone(self.updater.destinationPath)
        self.assertNotEqual(self.updater.name, Updater().name)

    def test_reloadVersions_constructVersionsInfo(self):
        self.updater.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/onlineBitbloqLibsVersionV5.version"
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")

        self.updater._reloadVersions()

        self.assertEqual(self.updater.currentVersionInfo.version, "0.0.1")
        self.assertEqual(self.updater.currentVersionInfo.file2DownloadUrl, 'file2DownloadUrl')
        self.assertEqual(self.updater.onlineVersionInfo.version, "0.0.5")
        self.assertEqual(self.updater.onlineVersionInfo.file2DownloadUrl, 'https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/bitbloqLibsV5.zip')

    def test_upload_writesLibrariesInDestinationPath(self):
        self.updater.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/src/Test/resources/Updater/onlineBitbloqLibsVersionV5.version"
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")
        self.updater.destinationPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "newLibrariesPath")
        try:
            self.updater.update(reloadVersions=True)
            downloadedLibraries = utils.listDirectoriesInPath(self.updater.destinationPath)
            self.assertGreater(len(downloadedLibraries), 0)
        finally:
            if os.path.exists(self.updater.destinationPath):
                shutil.rmtree(self.updater.destinationPath)


