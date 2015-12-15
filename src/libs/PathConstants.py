import logging
import os
import sys
import platform
from Arduino import base

__log = logging.getLogger(__name__)


def __getMainPath():
    path = sys.path[0]
    if platform.system() == 'Darwin':
        if os.environ.get('PYTHONPATH') is not None:
            path = os.environ.get('PYTHONPATH')
    return path


def __getSketchbook():
    path = base.sys_path.get_home_path() + '/Arduino'

    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        # self.pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'
        path = base.sys_path.get_document_path() + '/Arduino'
    return path


MAIN_PATH = __getMainPath()

RES_CONFIG_PATH = MAIN_PATH + '/res/config.json'

WEB2BOARD_CONFIG_PATH = base.sys_path.get_home_path() + '/.web2boardconfig'

SKETCHBOOK_PATH = __getSketchbook()


def logRelevantEnvironmentalPaths():
    __log.debug('sys.path[0]: {}'.format(sys.path[0]))
    __log.debug('PWD: {}'.format(os.environ.get('PWD')))
    __log.debug('PYTHONPATH: {}'.format(os.environ.get('PYTHONPATH')))
    __log.debug('ENVIRON: {}'.format(os.environ))
