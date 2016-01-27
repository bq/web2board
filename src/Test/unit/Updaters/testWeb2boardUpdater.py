import os
import shutil
import unittest
from copy import deepcopy

import time
from flexmock import flexmock

from Test.testingUtils import restoreAllTestResources
from libs.PathsManager import PathsManager
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater


class TestWeb2boardUpdater(unittest.TestCase):
    def setUp(self):
        self.testDataPath = os.path.join(PathsManager.TEST_SETTINGS_PATH, "Updater", "Web2boardUpdater")
        self.mainPath = os.path.join(self.testDataPath, "main")
        self.copyPath = os.path.join(self.testDataPath, "copy")
        self.updater = Web2BoardUpdater()
        self.original_osPopen = os.popen
        self.original_pathManagerDict = {x: y for x, y in PathsManager.__dict__.items()}
        self.original_sleep = time.sleep
        self.original_logCritical = Web2BoardUpdater.log.critical
        self.original_shutil_copy = shutil.copytree

        self.osMock = flexmock(os, popen=lambda x: None)
        restoreAllTestResources()

    def tearDown(self):
        os.popen = self.original_osPopen
        time.sleep = self.original_sleep
        shutil.copytree = self.original_shutil_copy
        Web2BoardUpdater.log.critical = self.original_logCritical
        PathsManager.__dict__ = {x: y for x, y in self.original_pathManagerDict.items()}

    def __setUpForMakeAuxiliaryCopy(self):
        PathsManager.MAIN_PATH = self.mainPath
        flexmock(PathsManager).should_receive("getCopyPathForUpdate").and_return(self.copyPath).at_least().times(1)
        time.sleep = lambda x: None
        self.updater = Web2BoardUpdater("readme", "readme_copy")

    def test_makeAuxiliaryCopy_refreshContentInCopyPathIfCopyPathDoesNotExist(self):
        self.__setUpForMakeAuxiliaryCopy()

        self.updater.makeAnAuxiliaryCopyAndRunIt("0.0.0")

        self.assertTrue(os.path.exists(self.copyPath))
        self.assertTrue(os.path.isfile(self.copyPath + os.sep + "readme_copy"))

    def test_makeAuxiliaryCopy_runsCopyProgram(self):
        self.__setUpForMakeAuxiliaryCopy()
        self.osMock.should_receive("popen").with_args('"{}" &'.format(self.copyPath + os.sep + "readme_copy"))

        self.updater.makeAnAuxiliaryCopyAndRunIt("0.0.0")

    def test_makeAuxiliaryCopy_callsLogCriticalEvenRaisingException(self):
        self.__setUpForMakeAuxiliaryCopy()
        self.osMock.should_receive("popen").and_raise(Exception)

        self.updater.makeAnAuxiliaryCopyAndRunIt("0.0.1")

        self.assertTrue(os.path.exists(self.mainPath))
        self.assertTrue(os.path.isfile(self.mainPath + os.sep + "readme"))
        self.assertTrue(os.path.isfile(self.mainPath + os.sep + "0.zip"))
