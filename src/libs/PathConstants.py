import logging
import os
import sys
import platform
from Arduino import base

log = logging.getLogger(__name__)


class Web2BoardPaths:
    def __init__(self):
        pass

    @staticmethod
    def getMainPath():
        path = sys.path[0]
        if platform.system() == 'Darwin':
            if os.environ.get('PYTHONPATH') is not None:
                path = os.environ.get('PYTHONPATH')
        return path

    @staticmethod
    def getSketchbookPath():
        path = sys.path[0]
        if platform.system() == 'Darwin':
            if os.environ.get('PYTHONPATH') is not None:
                path = os.environ.get('PYTHONPATH')
        return path

    @staticmethod
    def logRelevantEnvironmentalPaths():
        log.debug('sys.path[0]: {}'.format(sys.path[0]))
        log.debug('PWD: {}'.format(os.environ.get('PWD')))
        log.debug('PYTHONPATH: {}'.format(os.environ.get('PYTHONPATH')))
        log.debug('ENVIRON: {}'.format(os.environ))

    @staticmethod
    def getDownloadedFilePath(url):
        return base.sys_path.get_tmp_path() + os.sep + os.path.basename(url)

    @staticmethod
    def getBitbloqLibsTempPath(version):
        return base.sys_path.get_tmp_path() + '/bitbloqLibs-' + version

    @staticmethod
    def getSketchbookLibrariesPath():
        return SKETCHBOOK_PATH + os.sep + 'libraries' + os.sep


MAIN_PATH = Web2BoardPaths.getMainPath()

RES_CONFIG_PATH = MAIN_PATH + '/res/config.json'

WEB2BOARD_CONFIG_PATH = base.sys_path.get_home_path() + '/.web2boardconfig'

SKETCHBOOK_PATH = Web2BoardPaths.getSketchbookPath()

SKETCHBOOK_LIBRARIES_PATH = Web2BoardPaths.getSketchbookLibrariesPath()
