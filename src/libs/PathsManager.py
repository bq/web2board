import logging
import os
import sys
from os.path import expanduser
import platform
from libs import utils

_pathsLog = logging.getLogger(__name__)


class PathsManager:
    def __init__(self):
        pass

    EXECUTABLE_PATH = None
    MAIN_PATH = None
    PLATFORMIO_PACKAGES_ZIP_NAME = "platformIoPackages.zip"
    PLATFORMIO_PACKAGES_ZIP_PATH = None

    RES_PATH = None
    RES_ICO_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
    TEST_RES_PATH = None

    SETTINGS_PATH = None
    PLATFORMIO_WORKSPACE_PATH = None
    TEST_SETTINGS_PATH = None

    SCONS_EXECUTABLE_PATH = None

    @classmethod
    def getMainPath(cls):
        return cls.getBasePath()

    @staticmethod
    def getBasePath():
        if utils.areWeFrozen():
            return sys._MEIPASS
        else:
            return os.getcwd()

    @staticmethod
    def getExternalDataFolder():
        home = expanduser("~")
        if utils.isLinux():
            return os.path.join(home, ".web2board")
        elif utils.isWindows():
            return os.path.join(os.getenv('APPDATA'), 'web2board')
        elif utils.isMac():
            return os.path.join(home, ".web2board")
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @classmethod
    def getSonsExecutablePath(cls):
        if utils.areWeFrozen():
            if utils.isWindows():
                scriptName = "sconsScript.exe"
            else:
                scriptName = "sconsScript"
            return os.path.abspath(os.path.join(cls.RES_PATH, "Scons", scriptName))
        else:
            scriptName = "sconsScript.py"
        return os.path.abspath(os.path.join(cls.RES_PATH, "Scons", scriptName))

    @classmethod
    def logRelevantEnvironmentalPaths(cls):
        _pathsLog.debug('Working directory: {}'.format(os.getcwd()))
        items = cls.__dict__.items()
        items = sorted(items, key=lambda x: x[0])
        for key, path  in items:
            if "PATH" in key:
                _pathsLog.debug('{key}: {path}'.format(key=key, path=path))

    @staticmethod
    def getExternalResourcesPath():
        if utils.areWeFrozen() and utils.isMac():
            return os.path.join(pm.EXECUTABLE_PATH, os.path.pardir, "Resources")
        if pm.EXECUTABLE_PATH.endswith("externalResources"):
            return pm.EXECUTABLE_PATH

        return os.path.join(pm.EXECUTABLE_PATH, "externalResources")

    @classmethod
    def getCopyPathForUpdate(cls):
        return os.path.abspath(os.path.join(cls.MAIN_PATH, os.pardir, "web2board_copy"))

    @classmethod
    def getOriginalPathForUpdate(cls):
        return os.path.abspath(os.path.join(cls.MAIN_PATH, os.pardir, "web2board"))


# set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))

pm = PathsManager
pm.EXECUTABLE_PATH = os.getcwd()
pm.MAIN_PATH = pm.getMainPath()

pm.RES_PATH = os.path.join(pm.MAIN_PATH, 'res')
pm.RES_ICO_PATH = os.path.join(pm.RES_PATH, 'Web2board.ico')
pm.TEST_RES_PATH = os.path.join(pm.MAIN_PATH, 'Test', 'resources')
pm.RES_BOARDS_PATH = os.path.join(pm.RES_PATH, 'boards.txt')
pm.RES_PLATFORMIO_PATH = os.path.join(pm.RES_PATH, 'platformio')
pm.RES_LOGGING_CONFIG_PATH = os.path.join(pm.RES_PATH, 'logging.json')
pm.RES_SCONS_ZIP_PATH = os.path.join(pm.MAIN_PATH, "res", "sconsRes.zip")

pm.SETTINGS_PATH = pm.getExternalDataFolder()
pm.PLATFORMIO_WORKSPACE_PATH = os.path.join(pm.RES_PATH, 'platformioWorkSpace')
pm.TEST_SETTINGS_PATH = os.path.join(pm.RES_PATH, 'TestSettings', 'resources')
pm.SCONS_EXECUTABLE_PATH = pm.getSonsExecutablePath()

pm.PLATFORMIO_PACKAGES_ZIP_PATH = os.path.join(pm.RES_PATH, pm.PLATFORMIO_PACKAGES_ZIP_NAME)

