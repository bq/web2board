import os

import shutil

from libs.PathsManager import PathsManager
from libs import utils


def restoreAllTestResources():
    if os.path.exists(PathsManager.TEST_SETTINGS_PATH):
        shutil.rmtree(PathsManager.TEST_SETTINGS_PATH)
    os.makedirs(PathsManager.TEST_SETTINGS_PATH)
    utils.copytree(PathsManager.TEST_RES_PATH, PathsManager.TEST_SETTINGS_PATH, ignore=".pioenvs", forceCopy=True)
