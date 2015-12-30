import logging
import os
import platform
import sys

from libs import utils
from libs.base import sys_path

_pathsLog = logging.getLogger(__name__)


class Web2BoardPaths:
    def __init__(self):
        pass

    @staticmethod
    def getMainPath():
        path = Web2BoardPaths.getBasePath()
        return path

    @staticmethod
    def getBasePath():
        if utils.areWeFrozen():
            return sys._MEIPASS
        else:
            return os.getcwd()

    @staticmethod
    def getSketchbookPath():
        if platform.system() == 'Linux':
            # self.pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino/libraries'
            return sys_path.get_home_path() + os.sep + 'Arduino'
        elif platform.system() == 'Windows' or platform.system() == 'Darwin':
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
        _pathsLog.debug('WEB2BOARD_CONFIG_PATH: {}'.format(WEB2BOARD_CONFIG_PATH))
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

#set working directory to src
if utils.areWeFrozen():
    os.chdir(utils.getModulePath())
else:
    os.chdir(os.path.join(utils.getModulePath(), os.path.pardir))

EXECUTABLE_PATH = os.getcwd()
MAIN_PATH = Web2BoardPaths.getMainPath()
RES_PATH = os.path.join(MAIN_PATH, 'res')
RES_CONFIG_PATH = os.path.join(RES_PATH, 'config.json')
RES_BOARDS_PATH = os.path.join(RES_PATH, 'boards.txt')
EXTERNAL_DATA_PATH = os.path.join(sys_path.get_home_path(), ".webtoboard")
WEB2BOARD_CONFIG_PATH = os.path.join(EXTERNAL_DATA_PATH, '.web2boardconfig')
SKETCHBOOK_PATH = Web2BoardPaths.getSketchbookPath()
SKETCHBOOK_LIBRARIES_PATH = Web2BoardPaths.getSketchbookLibrariesPath()
