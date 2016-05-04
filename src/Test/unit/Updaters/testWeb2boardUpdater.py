import os
import shutil
import unittest
import time

import sys
from flexmock import flexmock

from Test.testingUtils import restoreAllTestResources, restorePaths
from libs import utils
from libs.PathsManager import PathsManager
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater


class TestWeb2boardUpdater(unittest.TestCase):
    def setUp(self):
        self.testDataPath = os.path.join(PathsManager.TEST_SETTINGS_PATH, "Updater", "Web2boardUpdater")
        self.versionPath = os.path.join(self.testDataPath, "versionPath")
        self.mainPath = os.path.join(self.testDataPath, "main")
        self.copyPath = os.path.join(self.testDataPath, "copy")
        self.updater = Web2BoardUpdater()
        self.original_osPopen = os.popen
        self.original_osRename = os.rename
        self.original_sleep = time.sleep
        self.original_logCritical = Web2BoardUpdater.log.critical
        self.original_shutil_copy = shutil.copytree
        self.original_killProcess = utils.kill_process
        self.original_exit = sys.exit

        self.osMock = flexmock(os, popen=lambda x: None)
        self.exitMock = flexmock(sys, exit=lambda x: None)
        restoreAllTestResources()

    def tearDown(self):
        os.popen = self.original_osPopen
        os.rename = self.original_osRename
        time.sleep = self.original_sleep
        utils.kill_process = self.original_killProcess
        shutil.copytree = self.original_shutil_copy
        sys.exit = self.original_exit
        Web2BoardUpdater.log.critical = self.original_logCritical
        restorePaths()

    def __setUpForCopyingFolders(self):
        PathsManager.MAIN_PATH = self.mainPath
        PathsManager.ORIGINAL_PATH = self.mainPath
        PathsManager.COPY_PATH = self.copyPath
        time.sleep = lambda x: None
        self.updater = Web2BoardUpdater("readme", "readme_copy")

    def test_makeAuxiliaryCopy_refreshContentInCopyPathIfCopyPathDoesNotExist(self):
        self.__setUpForCopyingFolders()

        self.updater.makeAnAuxiliaryCopy()

        self.assertTrue(os.path.exists(self.copyPath))
        self.assertTrue(os.path.isfile(self.copyPath + os.sep + "readme_copy"))

    def test_makeAuxiliaryCopy_runsCopyProgram(self):
        self.__setUpForCopyingFolders()
        self.osMock.should_receive("popen").with_args('"{}" &'.format(self.copyPath + os.sep + "readme_copy"))

        self.updater.makeAnAuxiliaryCopy()

    def test_makeAuxiliaryCopy_callsLogCriticalEvenRaisingException(self):
        self.__setUpForCopyingFolders()
        flexmock(self.updater.log).should_receive("critical").once()
        self.osMock.should_receive("rename").and_raise(Exception)

        self.updater.makeAnAuxiliaryCopy()

        self.assertTrue(os.path.exists(self.mainPath))
        self.assertTrue(os.path.isfile(self.mainPath + os.sep + "readme"))
        self.assertTrue(os.path.isfile(self.mainPath + os.sep + "0.zip"))

    def test_update_callsLogCriticalIfWeAreInOriginalPath(self):
        self.__setUpForCopyingFolders()
        flexmock(self.updater.log).should_receive("critical").once()

        self.updater.update("/")

    def __setUpForUpdate(self):
        self.__setUpForCopyingFolders()
        PathsManager.MAIN_PATH = PathsManager.COPY_PATH
        with open(self.versionPath + ".confirm", "w"):
            pass

    def test_update_killsWeb2boardProcess(self):
        self.__setUpForUpdate()
        flexmock(utils).should_receive("kill_process").with_args("web2board").once()

        self.updater.update(self.versionPath)

    def test_update_updatesFilesInMain(self):
        self.__setUpForUpdate()
        flexmock(utils).should_receive("kill_process")

        self.updater.update(self.versionPath)

        self.assertTrue(os.path.isfile(self.mainPath + os.sep + "new"))
        self.assertFalse(os.path.isfile(self.mainPath + os.sep + "0.zip"))
        self.assertFalse(os.path.isfile(self.mainPath + os.sep + "readme"))

    def test_update_callsExitAfterExecutingUpdate(self):
        self.__setUpForUpdate()
        flexmock(utils).should_receive("kill_process")
        self.exitMock.should_receive("exit").once()

        self.updater.update(self.versionPath)

