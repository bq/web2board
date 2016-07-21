import os
import unittest
import shutil

from Test.testingUtils import restore_test_resources
from libs import utils
from libs.PathsManager import PathsManager
from libs.AppVersion import AppVersion
from libs.Updaters.LibsUpdater import LibsUpdater, LibsUpdaterError


class TestLibsUpdater(unittest.TestCase):

    def setUp(self):
        restore_test_resources("Updater")
        self.test_settings_path = os.path.join(PathsManager.TEST_SETTINGS_PATH, "Updater")

        # Temporary version file to test restoring and updating versions
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, "w2b.version")
        AppVersion.read_version_values()
        AppVersion.libs.url = "file:" + os.sep + os.sep + self.test_settings_path + os.sep + "bitbloqLibsV5.zip"

        self.libs_updater = LibsUpdater()
        self.libs_updater.destination_path = os.path.join(self.test_settings_path, "destinationPath")


    def tearDown(self):
        PathsManager.set_all_constants()
        AppVersion.read_version_values()


    def test_restore_current_version_if_necessary_returnsFalseIfAllLibrariesInDestinationPath(self):
        AppVersion.libs.libraries_names = ["l1", "l2", "l3"]

        for library in AppVersion.libs.libraries_names:
            os.makedirs(os.path.join(self.libs_updater.destination_path, library))

        self.assertFalse(self.libs_updater.restore_current_version_if_necessary())


    def _check_correct_version(self):
        # Check that libraries have been downloaded and saved correctly
        libs_in_path = utils.list_directories_in_path(self.libs_updater.destination_path)
        for lib in AppVersion.libs.libraries_names:
            self.assertTrue(lib in libs_in_path)


    def test_restore_current_version_if_necessary_restoresLibsIfDestinationPathDoesNotExist(self):
        if os.path.exists(self.libs_updater.destination_path):
            shutil.rmtree(self.libs_updater.destination_path)
        self.assertFalse(os.path.exists(self.libs_updater.destination_path))

        self.assertTrue(self.libs_updater.restore_current_version_if_necessary())
        self._check_correct_version()


    def test_restore_current_version_if_necessary_restoresLibsIfDestinationPathIsEmpty(self):
        os.makedirs(self.libs_updater.destination_path)
        self.assertTrue([] == utils.list_directories_in_path(self.libs_updater.destination_path))

        self.assertTrue(self.libs_updater.restore_current_version_if_necessary())
        self._check_correct_version()


    def test_restore_current_version_if_necessary_restoresLibsIfMissingLibrariesInDestinationPath(self):
        os.makedirs(self.libs_updater.destination_path + os.sep + "BitbloqRGB")
        self.assertTrue(["BitbloqRGB"] == utils.list_directories_in_path(self.libs_updater.destination_path))

        self.assertTrue(self.libs_updater.restore_current_version_if_necessary())
        self._check_correct_version()


    def test_update_raisesExceptionIfBadFormattedUrl(self):
        with self.assertRaises(ValueError):
            self.libs_updater.update("0.1.1", "aaa")


    def test_update_raisesExceptionIfUrlDoesNotExist(self):
        with self.assertRaises(IOError):
            self.libs_updater.update("0.1.1", "https://raw.githubusercontent.com/bq/web2board/bitbloq.zip")


    def test_update_raisesExceptionIfZipDoesNotContainLibsFolder(self):
        empty_libs_url = "file:" + os.sep + os.sep + self.test_settings_path + os.sep + "emptyLibs.zip"
        with self.assertRaises(LibsUpdaterError):
            self.libs_updater.update("0.0.1", empty_libs_url)


    def test_update_successfullyUpdatesVersion(self):
        self.assertTrue(self.libs_updater.update("0.1.2", "https://github.com/bq/bitbloqLibs/archive/v0.1.2.zip"))
        self._check_correct_version()