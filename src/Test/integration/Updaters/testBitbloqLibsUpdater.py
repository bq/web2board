import json
import os
import shutil
import unittest

from flexmock import flexmock, flexmock_teardown

from Test.testingUtils import restore_test_resources
from libs.PathsManager import PathsManager as pm
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Updater import Updater, VersionInfo
from libs.Version import Version


class TestBitbloqLibsUpdater(unittest.TestCase):
    def setUp(self):
        self.res_path = os.path.join(pm.TEST_SETTINGS_PATH, "Updater")
        self.updater = BitbloqLibsUpdater()
        self.updater.destinationPath = os.path.join(self.res_path, "newLibrariesPath")
        restore_test_resources()
        self.original_pathManagerDict = {x: y for x, y in pm.__dict__.items()}

        pm.CONFIG_PATH = pm.TEST_SETTINGS_PATH + os.sep + "config.json"

    def tearDown(self):
        flexmock_teardown()
        pm.__dict__ = {x: y for x, y in self.original_pathManagerDict.items()}

    def test_construct_setsAllNecessaryAttributes(self):
        self.assertIsNotNone(self.updater.current_version_info)
        self.assertEqual(self.updater.current_version_info.version, Version.bitbloq_libs)
        self.assertEqual(self.updater.current_version_info.libraries_names, Version.bitbloq_libs_libraries)
        self.assertIsNotNone(self.updater.destinationPath)
        self.assertNotEqual(self.updater.name, Updater().name)

    def __testUploadProcess(self, online_version):
        try:
            self.updater.update(online_version)
            self.assertEqual(self.updater.current_version_info.version, online_version.version)
            self.assertGreater(len(self.updater.current_version_info.libraries_names), 0)
            self.assertFalse(self.updater._are_we_missing_libraries())
            self.assertFalse(self.updater.current_version_info != online_version)
            self.assertFalse(self.updater.isNecessaryToUpdate(online_version))
            self.assertEqual(self.updater.current_version_info.version, Version.bitbloq_libs)
            self.assertEqual(self.updater.current_version_info.libraries_names, Version.bitbloq_libs_libraries)
        finally:
            if os.path.exists(self.updater.destinationPath):
                shutil.rmtree(self.updater.destinationPath)
            self.assertFalse(os.path.exists(self.updater.destinationPath))

    def test_upload_writesLibrariesInDestinationPathWithControlledData(self):
        version = VersionInfo("0.0.5", "file:" + os.sep + os.sep + self.res_path + os.sep + "bitbloqLibsV5.zip")
        self.updater.currentVersionInfoPath = os.path.join(pm.TEST_SETTINGS_PATH, "Updater", "currentVersion.version")
        self.__testUploadProcess(version)

    def test_update_raiseExceptionIfOnlineVersionIsNone(self):
        flexmock(json).should_receive("dump").never()
        flexmock(self.updater.downloader).should_receive("download").never()

        with self.assertRaises(Exception):
            self.updater.update(self.updater.current_version_info)


    @unittest.skip("skip until we have good urls")
    def test_upload_withRealValues(self):
        self.__testUploadProcess()
