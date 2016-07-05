import os
import unittest

from Test.testingUtils import restore_test_resources
from libs.PathsManager import PathsManager
from libs.AppVersion import AppVersion
from libs.Updaters.LibsUpdater import LibsUpdater


class TestLibsUpdater(unittest.TestCase):
    def setUp(self):
        self.test_settings_path = os.path.join(PathsManager.TEST_SETTINGS_PATH, "Updater")


        self.libs_updater = LibsUpdater()
        self.libs_updater.destination_path = os.path.join(self.test_settings_path,
                                                          "newLibrariesPath")
        restore_test_resources("Updater")

    def tearDown(self):
        PathsManager.set_all_constants()
        AppVersion.read_version_values()

