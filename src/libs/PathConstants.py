import logging
import os
import platform
import sys

from libs import utils
from libs.Arduino import base

log = logging.getLogger(__name__)


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
            return base.sys_path.get_home_path() + os.sep + 'Arduino'
        elif platform.system() == 'Windows' or platform.system() == 'Darwin':
            # self.pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'
            return base.sys_path.get_document_path() + os.sep + 'Arduino'
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @staticmethod
    def logRelevantEnvironmentalPaths():
        log.debug('sys.path[0]: {}'.format(sys.path[0]))
        log.debug('PWD: {}'.format(os.environ.get('PWD')))
        log.debug('PYTHONPATH: {}'.format(os.environ.get('PYTHONPATH')))

        log.debug('MAIN_PATH: {}'.format(MAIN_PATH))
        log.debug('RES_CONFIG_PATH: {}'.format(RES_CONFIG_PATH))
        log.debug('WEB2BOARD_CONFIG_PATH: {}'.format(WEB2BOARD_CONFIG_PATH))
        log.debug('SKETCHBOOK_PATH: {}'.format(SKETCHBOOK_PATH))
        log.debug('SKETCHBOOK_LIBRARIES_PATH: {}'.format(SKETCHBOOK_LIBRARIES_PATH))
        # log.debug('ENVIRON: {}'.format(os.environ))

    @staticmethod
    def getBitbloqLibsTempPath(version):
        return base.sys_path.get_tmp_path() + os.sep + 'bitbloqLibs-' + version

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
WEB2BOARD_CONFIG_PATH = base.sys_path.get_home_path() + os.sep + '.web2boardconfig'
SKETCHBOOK_PATH = Web2BoardPaths.getSketchbookPath()
SKETCHBOOK_LIBRARIES_PATH = Web2BoardPaths.getSketchbookLibrariesPath()
