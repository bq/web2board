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


