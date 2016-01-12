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
    EXTERNAL_RESOURCES_PATH = None

    RES_PATH = None
    RES_CONFIG_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
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
            if utils.isWindows():
                return cls.EXTERNAL_RESOURCES_PATH + os.sep + "sconsScript.exe"
            else:
                return cls.EXTERNAL_RESOURCES_PATH + os.sep + "sconsScript"
        else:
            return cls.EXTERNAL_RESOURCES_PATH + os.sep + "sconsScript.py"

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
            web2boardUpdater.readSettingsVersionInfo()

            from Scripts import afterInstallScript
            afterInstallScript.run()

    @staticmethod
    def getExternalResourcesPath():
        if pm.EXECUTABLE_PATH.endswith("externalResources"):
            return pm.EXECUTABLE_PATH

        return os.path.join(pm.EXECUTABLE_PATH, "externalResources")


# set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))

pm = PathsManager
pm.EXECUTABLE_PATH = os.getcwd()
pm.MAIN_PATH = pm.getMainPath()
pm.EXTERNAL_RESOURCES_PATH = pm.getExternalResourcesPath()

pm.RES_PATH = os.path.join(pm.MAIN_PATH, 'res')
pm.TEST_RES_PATH = os.path.join(pm.MAIN_PATH, 'Test', 'resources')
pm.RES_CONFIG_PATH = os.path.join(pm.RES_PATH, 'config.json')
pm.RES_BOARDS_PATH = os.path.join(pm.RES_PATH, 'boards.txt')
pm.RES_PLATFORMIO_PATH = os.path.join(pm.RES_PATH, 'platformio')
pm.RES_LOGGING_CONFIG_PATH = os.path.join(pm.RES_PATH, 'logging.json')
pm.RES_SCONS_ZIP_PATH = os.path.join(pm.MAIN_PATH, "res", "sconsRes.zip")


pm.SETTINGS_PATH = pm.getExternalDataFolder()
pm.SETTINGS_PLATFORMIO_PATH = os.path.join(pm.SETTINGS_PATH, 'platformio')
pm.SETTINGS_CONFIG_PATH = os.path.join(pm.SETTINGS_PATH, '.web2boardconfig')
pm.SETTINGS_LOGGING_CONFIG_PATH = os.path.join(pm.SETTINGS_PATH, 'logging.json')
pm.TEST_SETTINGS_PATH = os.path.join(pm.SETTINGS_PATH, 'Test', 'resources')

# construct External_data_path if not exists
if not os.path.exists(pm.SETTINGS_PATH):
    os.makedirs(pm.SETTINGS_PATH)
