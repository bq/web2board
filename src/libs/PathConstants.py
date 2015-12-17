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
        #log.debug('ENVIRON: {}'.format(os.environ))

    @staticmethod
    def getDownloadedFilePath(url):
        return base.sys_path.get_tmp_path() + os.sep + os.path.basename(url)

    @staticmethod
    def getBitbloqLibsTempPath(version):
        return base.sys_path.get_tmp_path() + '/bitbloqLibs-' + version

    @staticmethod
    def getSketchbookLibrariesPath():
        return SKETCHBOOK_PATH + os.sep + 'libraries' + os.sep

for i in range(5000):
    try:
        MAIN_PATH = Web2BoardPaths.getMainPath()
        RES_CONFIG_PATH = MAIN_PATH + '{0}res{0}config.json'.format(os.sep)
        WEB2BOARD_CONFIG_PATH = base.sys_path.get_home_path() + os.sep + '.web2boardconfig'
        SKETCHBOOK_PATH = Web2BoardPaths.getSketchbookPath()
        SKETCHBOOK_LIBRARIES_PATH = Web2BoardPaths.getSketchbookLibrariesPath()
    except Exception as e:
        log.error("Error finding paths", exc_info=1)
        # raise e
