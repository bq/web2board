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
    PLATFORMIO_PACKAGES_NAME = "platformIoPackages"
    PLATFORMIO_PACKAGES_PATH = None
    CONFIG_PATH = None
    COPY_PATH = None
    ORIGINAL_PATH = None

    RES_PATH = None
    RES_ICO_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
    TEST_RES_PATH = None

    PROGRAM_PATH = None
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

    @classmethod
    def getExternalDataFolder(cls):
        if utils.isLinux():
            folder = ".web2board"
        elif utils.isWindows():
            folder = "web2board"
        elif utils.isMac():
            folder = ".web2board"
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))
        return os.path.join(cls.getHomePath(), folder)

    @staticmethod
    def getHomePath():
        if utils.isLinux():
            return expanduser("~")
        elif utils.isWindows():
            return os.getenv('APPDATA')
        elif utils.isMac():
            return expanduser("~")
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @classmethod
    def getDstPathForUpdate(cls, version):
        return os.path.join(cls.getHomePath(), "web2board_{}".format(version))

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
        for key, path in items:
            if "PATH" in key:
                _pathsLog.debug('{key}: {path}'.format(key=key, path=path))

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
pm.CONFIG_PATH = os.path.join(pm.MAIN_PATH, 'config.json')
pm.COPY_PATH = pm.getCopyPathForUpdate()
pm.ORIGINAL_PATH = pm.getOriginalPathForUpdate()

pm.RES_PATH = os.path.join(pm.MAIN_PATH, 'res')
pm.RES_ICO_PATH = os.path.join(pm.RES_PATH, 'Web2board.ico')
pm.TEST_RES_PATH = os.path.join(pm.MAIN_PATH, 'Test', 'resources')
pm.RES_BOARDS_PATH = os.path.join(pm.RES_PATH, 'boards.txt')
pm.RES_PLATFORMIO_PATH = os.path.join(pm.RES_PATH, 'platformio')
pm.RES_LOGGING_CONFIG_PATH = os.path.join(pm.RES_PATH, 'logging.json')
pm.RES_SCONS_ZIP_PATH = os.path.join(pm.MAIN_PATH, "res", "sconsRes.zip")

pm.PROGRAM_PATH = pm.getExternalDataFolder()
pm.PLATFORMIO_WORKSPACE_PATH = os.path.join(pm.RES_PATH, 'platformioWorkSpace')
pm.TEST_SETTINGS_PATH = os.path.join(pm.RES_PATH, 'TestSettings', 'resources')
pm.SCONS_EXECUTABLE_PATH = pm.getSonsExecutablePath()

pm.PLATFORMIO_PACKAGES_PATH = os.path.join(pm.RES_PATH, pm.PLATFORMIO_PACKAGES_NAME)