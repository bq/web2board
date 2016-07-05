import os
import unittest

from flexmock import flexmock, flexmock_teardown

from Test.testingUtils import restore_test_resources
from libs.PathsManager import PathsManager
from libs.AppVersion import AppVersion
from libs.Updaters.LibsUpdater import LibsUpdater


class TestLibsUpdater(unittest.TestCase):

    def setUp(self):
        self.libs_updater = LibsUpdater()
        self.libs_updater.destination_path = os.path.join(PathsManager.TEST_SETTINGS_PATH,
                                                          "Updater",
                                                          "destinationPath")
        restore_test_resources("Updater")

    def tearDown(self):
        PathsManager.set_all_constants()
        AppVersion.read_version_values()
        flexmock_teardown()

    def test_is_necessary_to_update_returnsTrueIfDifferentVersions(self):
        AppVersion.libs.version_string = "0.1.1"

        self.assertTrue(self.libs_updater.is_necessary_to_update("0.2.1"))

    def test_is_necessary_to_update_returnsTrueIfSameVersion(self):
        AppVersion.libs.version_string = "0.1.1"

        self.assertFalse(self.libs_updater.is_necessary_to_update("0.1.1"))

    def test_is_necessary_to_update_raisesExceptionIfNoVersionProvided(self):
        AppVersion.libs.version_string = "0.1.1"

        with self.assertRaises(Exception):
            self.libs_updater.is_necessary_to_update()

    def test_is_necessary_to_update_raisesExceptionIfBadFormattedVersion(self):
        AppVersion.libs.version_string = "0.1.1"

        with self.assertRaises(Exception):
            self.libs_updater.is_necessary_to_update("a.b.c")

    def test__are_we_missing_libraries_returnsTrueIfDestinationPathDoesNotExist(self):
        self.assertTrue(self.libs_updater._are_we_missing_libraries())

    def test__are_we_missing_libraries_returnsTrueIfMissingLibrariesInDestinationPath(self):
        AppVersion.libs.libraries_names = ["l1", "l2", "l3"]
        os.makedirs(self.libs_updater.destination_path)

        self.assertTrue(self.libs_updater._are_we_missing_libraries())

    def test_restore_current_version_if_necessary_returnsFalseIfAllLibrariesInDestinationPath(self):
        AppVersion.libs.libraries_names = ["l1", "l2", "l3"]

