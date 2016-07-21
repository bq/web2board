import os
import unittest

from Test.testingUtils import restore_test_resources
from libs.PathsManager import PathsManager
from libs.AppVersion import AppVersion
from libs.Updaters.LibsUpdater import LibsUpdater


class TestLibsUpdater(unittest.TestCase):
    def setUp(self):
        restore_test_resources("Updater")
        self.test_settings_path = os.path.join(PathsManager.TEST_SETTINGS_PATH, "Updater")

        #Temporary version file that will be written when testing restore_current_version_if_necessary()
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, "w2b.version")

        self.libs_updater = LibsUpdater()
        self.libs_updater.destination_path = os.path.join(self.test_settings_path,
                                                          "destinationPath")


    def tearDown(self):
        PathsManager.set_all_constants()
        AppVersion.read_version_values()

    def test_restore_current_version_if_necessary_returnsFalseIfAllLibrariesInDestinationPath(self):
        AppVersion.libs.libraries_names = ["l1", "l2", "l3"]

        for library in AppVersion.libs.libraries_names:
            os.makedirs(os.path.join(self.libs_updater.destination_path, library))

        self.assertFalse(self.libs_updater.restore_current_version_if_necessary())

    def test_restore_current_version_if_necessary_restoresLibsIfDestinationPathDoesNotExist(self):
        AppVersion.libs.url = "file:" + os.sep + os.sep + self.test_settings_path + os.sep + "bitbloqLibsV5.zip"
        self.assertTrue(self.libs_updater.restore_current_version_if_necessary())


        # TODO: ckeck that libraries have been downloaded and saved correctly

    # TODO: refactor this test for method restore_current_version_if_necessary()
    def test__are_we_missing_libraries_returnsTrueIfMissingLibrariesInDestinationPath(self):
        AppVersion.libs.libraries_names = ["l1", "l2", "l3"]
        os.makedirs(self.libs_updater.destination_path)

        self.assertTrue(self.libs_updater._are_we_missing_libraries())



    #TODO: tests for update() method