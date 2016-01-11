import logging
import os
import platform
import shutil
import sys
from libs import utils
from libs.base import sys_path
from libs.utils import copytree

_pathsLog = logging.getLogger(__name__)


class PathsManager:
    def __init__(self):
        pass

    EXECUTABLE_PATH = None
    MAIN_PATH = None
    RES_PATH = None
    RES_CONFIG_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
    RES_PLATFORMIO_PACKAGES_ZIP_PATH = None
    TEST_RES_PATH = None

    SETTINGS_PATH = None
    SETTINGS_PLATFORMIO_PATH = None
    SETTINGS_CONFIG_PATH = None
    SETTINGS_LOGGING_CONFIG_PATH = None
    TEST_SETTINGS_PATH = None

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
        if utils.isLinux():
            return os.path.join(sys_path.get_home_path(), ".web2board")
        elif utils.isWindows():
            return os.path.join(os.getenv('APPDATA'), 'web2board')
        elif utils.isMac():
            return sys_path.get_home_path() + os.sep + ".web2board"
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @classmethod
    def getSonsExecutablePath(cls):
        if utils.areWeFrozen():
            return cls.EXECUTABLE_PATH + os.sep + "scons.exe"
        else:
            return cls.EXECUTABLE_PATH + os.sep + "scons.py"

    @classmethod
    def logRelevantEnvironmentalPaths(cls):
        _pathsLog.debug('sys.path[0]: {}'.format(sys.path[0]))
        _pathsLog.debug('PWD: {}'.format(os.environ.get('PWD')))
        for key, path  in cls.__dict__.items():
            if "PATH" in key:
                _pathsLog.debug('{key}: {path}'.format(key=key, path=path))

    @classmethod
    def moveInternalConfigToExternalIfNecessary(cls):
        from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
        web2boardUpdater = getWeb2boardUpdater()
        if web2boardUpdater.isNecessaryToUpdateSettings():
            _pathsLog.info("Creating settings folder structure in: {}".format(cls.TEST_SETTINGS_PATH))
            shutil.copyfile(cls.RES_CONFIG_PATH, cls.SETTINGS_CONFIG_PATH)

            if os.path.exists(cls.SETTINGS_PLATFORMIO_PATH):
                shutil.rmtree(cls.SETTINGS_PLATFORMIO_PATH)
            os.makedirs(cls.SETTINGS_PLATFORMIO_PATH)
            copytree(cls.RES_PLATFORMIO_PATH, cls.SETTINGS_PLATFORMIO_PATH)

            shutil.copyfile(cls.RES_LOGGING_CONFIG_PATH, cls.SETTINGS_LOGGING_CONFIG_PATH)

            if os.path.exists(cls.TEST_SETTINGS_PATH):
                shutil.rmtree(cls.TEST_SETTINGS_PATH)
            os.makedirs(cls.TEST_SETTINGS_PATH)
            copytree(cls.TEST_RES_PATH, cls.TEST_SETTINGS_PATH, ignore=".pioenvs")

            shutil.copyfile(web2boardUpdater.currentVersionInfoPath, web2boardUpdater.settingsVersionInfoPath)


# set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))

PathsManager.EXECUTABLE_PATH = os.getcwd()
PathsManager.MAIN_PATH = PathsManager.getMainPath()
PathsManager.RES_PATH = os.path.join(PathsManager.MAIN_PATH, 'res')
PathsManager.TEST_RES_PATH = os.path.join(PathsManager.MAIN_PATH, 'Test', 'resources')
PathsManager.RES_CONFIG_PATH = os.path.join(PathsManager.RES_PATH, 'config.json')
PathsManager.RES_BOARDS_PATH = os.path.join(PathsManager.RES_PATH, 'boards.txt')
PathsManager.RES_PLATFORMIO_PATH = os.path.join(PathsManager.RES_PATH, 'platformio')
PathsManager.RES_LOGGING_CONFIG_PATH = os.path.join(PathsManager.RES_PATH, 'logging.json')
PathsManager.RES_SCONS_ZIP_PATH = os.path.join(PathsManager.MAIN_PATH, "res", "sconsRes.zip")
PathsManager.RES_PLATFORMIO_PACKAGES_ZIP_PATH = os.path.join(PathsManager.MAIN_PATH, "res", "platformPackages.zip")

PathsManager.SETTINGS_PATH = PathsManager.getExternalDataFolder()
PathsManager.SETTINGS_PLATFORMIO_PATH = os.path.join(PathsManager.SETTINGS_PATH, 'platformio')
PathsManager.SETTINGS_CONFIG_PATH = os.path.join(PathsManager.SETTINGS_PATH, '.web2boardconfig')
PathsManager.SETTINGS_LOGGING_CONFIG_PATH = os.path.join(PathsManager.SETTINGS_PATH, 'logging.json')
PathsManager.TEST_SETTINGS_PATH = os.path.join(PathsManager.SETTINGS_PATH, 'Test', 'resources')

# construct External_data_path if not exists
if not os.path.exists(PathsManager.SETTINGS_PATH):
    os.makedirs(PathsManager.SETTINGS_PATH)
