import logging
import os

import sys

import subprocess

import libs.utils as utils
from libs.PathsManager import PathsManager


def startLogger():
    fileHandler = logging.FileHandler("web2boardLauncher.log", 'a')
    fileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(fileHandler)
    log.setLevel(logging.DEBUG)

def open_file(filename):
    if sys.platform == "win32":
        subprocess.call([filename] + sys.argv[1:])
    else:
        subprocess.call(["./" + filename] + sys.argv[1:])

startLogger()
log = logging.getLogger(__name__)
web2boardPath = "web2board" + utils.getOsExecutableExtension()

if __name__ == '__main__':
    utils.killProcess("web2board" + utils.getOsExecutableExtension())
    open_file("web2board")
