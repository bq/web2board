import glob
import logging
import os
import sys
from os.path import expanduser
import platform
import shutil

from libs import utils

_pathsLog = logging.getLogger(__name__)


class PathsManager:
    def __init__(self):
        pass

    EXECUTABLE_PATH = None
    EXECUTABLE_FILE = None
    MAIN_PATH = None
    PLATFORMIO_PACKAGES_NAME = "pp"
    PLATFORMIO_PACKAGES_PATH = None
    CONFIG_PATH = None
    COPY_PATH = None
    ORIGINAL_PATH = None

    RES_PATH = None
    RES_ICO_PATH = None
    RES_ICONS_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
    TEST_RES_PATH = None

    PROGRAM_PATH = None
    PLATFORMIO_WORKSPACE_SKELETON = None
    PLATFORMIO_WORKSPACE_PATH = None
    PLATFORMIO_INI_PATH = None
    TEST_SETTINGS_PATH = None

    SCONS_EXECUTABLE_PATH = None

    @classmethod
    def getMainPath(cls):
        return cls.getBasePath()

    @staticmethod
    def getBasePath():
        if utils.areWeFrozen():
            if utils.isMac():
                return os.getcwd()
            return os.getcwd()
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
        return os.path.join(cls.getHomePath(), u"web2board_{}".format(version))

    @classmethod
    def getSonsExecutablePath(cls):
        return os.path.abspath(os.path.join(cls.RES_PATH, "Scons", "sconsScript.py"))

    @classmethod
    def getPlatformIOPackagesPath(cls):
        path = os.path.join(cls.RES_PATH, cls.PLATFORMIO_PACKAGES_NAME)
        return os.path.abspath(path)

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

    @classmethod
    def setAllConstants(cls):
        cls.EXECUTABLE_PATH = os.getcwd()
        cls.EXECUTABLE_FILE = os.getcwd() + os.sep + "web2board" + utils.getOsExecutableExtension()
        cls.MAIN_PATH = cls.getMainPath()
        cls.CONFIG_PATH = os.path.normpath(os.path.join(cls.MAIN_PATH, os.pardir, 'web2board-config.json'))
        cls.COPY_PATH = cls.getCopyPathForUpdate()
        cls.ORIGINAL_PATH = cls.getOriginalPathForUpdate()

        if utils.isMac() and utils.areWeFrozen():
            cls.RES_PATH = os.path.join(cls.MAIN_PATH, os.pardir, 'Resources', 'res')
            cls.RES_PATH = os.path.abspath(cls.RES_PATH)
        else:
            cls.RES_PATH = os.path.join(cls.MAIN_PATH, 'res')
        cls.RES_ICO_PATH = os.path.join(cls.RES_PATH, 'Web2board.ico')
        cls.RES_ICONS_PATH = os.path.join(cls.RES_PATH, 'icons')
        cls.TEST_RES_PATH = os.path.join(cls.MAIN_PATH, 'Test', 'resources')
        cls.RES_BOARDS_PATH = os.path.join(cls.RES_PATH, 'boards.txt')
        cls.RES_PLATFORMIO_PATH = os.path.abspath(os.path.join(cls.RES_PATH, os.pardir, 'platformio'))
        cls.RES_LOGGING_CONFIG_PATH = os.path.join(cls.RES_PATH, 'logging.json')
        cls.RES_SCONS_ZIP_PATH = os.path.join(cls.MAIN_PATH, "res", "sconsRes.zip")

        cls.PROGRAM_PATH = cls.getExternalDataFolder()
        cls.PLATFORMIO_WORKSPACE_SKELETON = os.path.join(cls.RES_PATH, 'platformioWorkSpaceSkeleton')
        cls.PLATFORMIO_WORKSPACE_PATH = cls.PLATFORMIO_WORKSPACE_SKELETON
        cls.PLATFORMIO_INI_PATH = os.path.join(cls.PLATFORMIO_WORKSPACE_SKELETON, 'platformio.ini')
        cls.TEST_SETTINGS_PATH = os.path.join(cls.RES_PATH, 'TestSettings', 'resources')
        cls.SCONS_EXECUTABLE_PATH = cls.getSonsExecutablePath()

        cls.PLATFORMIO_PACKAGES_PATH = cls.getPlatformIOPackagesPath()

    @classmethod
    def getIconPath(cls, iconName):
        return os.path.join(PathsManager.RES_ICONS_PATH, iconName)

    @classmethod
    def cleanPioEnvs(cls):
        path = os.path.join(cls.PLATFORMIO_WORKSPACE_PATH, ".pioenvs")
        if os.path.exists(path):
            shutil.rmtree(path)

# set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))


PathsManager.setAllConstants()
