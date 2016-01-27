#!/usr/bin/env python
import os

import shutil

from libs.Decorators.Asynchronous import asynchronous
from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager
from libs import utils
from platformio import util


@asynchronous(daemon=False)
def run():
    log = initLogging(__name__)
    log.info("running afterInstallScript")
    log.info("adding settings files...")
    if not os.path.exists(PathsManager.PLATFORMIO_PACKAGES_PATH):
        log.warning("No platformio packages zip found. (ignored)")
    else:
        log.info("extracting platformIO packages...")
        utils.copytree(PathsManager.PLATFORMIO_PACKAGES_PATH, util.get_home_dir(), forceCopy=True)

    log.info("Removing platformioPackages")
    shutil.rmtree(PathsManager.PLATFORMIO_PACKAGES_PATH)
    assert os.path.exists(util.get_home_dir())
    assert os.path.exists(PathsManager.RES_PATH)
    log.info("afterInstallScript was successfully executed")

if __name__ == '__main__':
    run()
