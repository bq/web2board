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

    @staticmethod
    def getMainPath():
        path = PathsManager.getBasePath()
        return path

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

    @staticmethod
    def getSketchbookPath():
        if utils.isLinux():
            # self.pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino/libraries'
            return sys_path.get_home_path() + os.sep + 'Arduino'
        elif utils.isWindows() or utils.isMac():
            # self.pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'
            return sys_path.get_document_path() + os.sep + 'Arduino'
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @staticmethod
    def logRelevantEnvironmentalPaths():
        _pathsLog.debug('sys.path[0]: {}'.format(sys.path[0]))
        _pathsLog.debug('PWD: {}'.format(os.environ.get('PWD')))
        _pathsLog.debug('PYTHONPATH: {}'.format(os.environ.get('PYTHONPATH')))

        _pathsLog.debug('MAIN_PATH: {}'.format(MAIN_PATH))
        _pathsLog.debug('RES_CONFIG_PATH: {}'.format(RES_CONFIG_PATH))
        _pathsLog.debug('WEB2BOARD_CONFIG_PATH: {}'.format(SETTINGS_CONFIG_PATH))
        _pathsLog.debug('SKETCHBOOK_PATH: {}'.format(SKETCHBOOK_PATH))
        _pathsLog.debug('SKETCHBOOK_LIBRARIES_PATH: {}'.format(SKETCHBOOK_LIBRARIES_PATH))
        # log.debug('ENVIRON: {}'.format(os.environ))

    @staticmethod
    def getBitbloqLibsTempPath(version):
        return sys_path.get_tmp_path() + os.sep + 'bitbloqLibs-' + version

    @staticmethod
    def getSketchbookLibrariesPath():
        return SKETCHBOOK_PATH + os.sep + 'libraries' + os.sep

    @staticmethod
    def getPathForNewPackage(version):
        return MAIN_PATH + os.sep + "web2board_{}".format(version)

    @staticmethod
    def moveInternalConfigToExternalIfNecessary():
        if not os.path.isfile(SETTINGS_CONFIG_PATH):
            shutil.copyfile(RES_CONFIG_PATH, SETTINGS_CONFIG_PATH)
        if not os.path.isdir(SETTINGS_PLATFORMIO_PATH):
            os.makedirs(SETTINGS_PLATFORMIO_PATH)
            copytree(RES_PLATFORMIO_PATH, SETTINGS_PLATFORMIO_PATH)
        if not os.path.isfile(SETTINGS_LOGGING_CONFIG_PATH):
            shutil.copyfile(RES_LOGGING_CONFIG_PATH, SETTINGS_LOGGING_CONFIG_PATH)
        if not os.path.exists(TEST_SETTINGS_PATH):
            os.makedirs(TEST_SETTINGS_PATH)
            copytree(TEST_RES_PATH, TEST_SETTINGS_PATH)

#set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))

EXECUTABLE_PATH = os.getcwd()
MAIN_PATH = PathsManager.getMainPath()
RES_PATH = os.path.join(MAIN_PATH, 'res')
TEST_RES_PATH = os.path.join(MAIN_PATH, 'Test', 'resources')
RES_CONFIG_PATH = os.path.join(RES_PATH, 'config.json')
RES_BOARDS_PATH = os.path.join(RES_PATH, 'boards.txt')
RES_PLATFORMIO_PATH = os.path.join(RES_PATH, 'platformio')
RES_LOGGING_CONFIG_PATH = os.path.join(RES_PATH, 'logging.json')

SETTINGS_PATH = PathsManager.getExternalDataFolder()
SETTINGS_PLATFORMIO_PATH = os.path.join(SETTINGS_PATH, 'platformio')
SETTINGS_CONFIG_PATH = os.path.join(SETTINGS_PATH, '.web2boardconfig')
SETTINGS_LOGGING_CONFIG_PATH = os.path.join(SETTINGS_PATH, 'logging.json')
TEST_SETTINGS_PATH = os.path.join(SETTINGS_PATH, 'Test', 'resources')

SKETCHBOOK_PATH = PathsManager.getSketchbookPath()
SKETCHBOOK_LIBRARIES_PATH = PathsManager.getSketchbookLibrariesPath()


#construct External_data_path if not exists
if not os.path.exists(SETTINGS_PATH):
    os.makedirs(SETTINGS_PATH)