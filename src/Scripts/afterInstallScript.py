import os
import zipfile

from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager
from platformio import util


def run():
    log = initLogging(__name__)
    log.info("running afterInstallScript")
    log.info("adding settings files...")
    PathsManager.moveInternalConfigToExternalIfNecessary()
    if not os.path.exists(PathsManager.PLATFORMIO_PACKAGES_ZIP_PATH):
        log.warning("No platformio packages zip found. (ignored)")
    else:
        log.info("extracting platformIO packages...")
        with zipfile.ZipFile(PathsManager.PLATFORMIO_PACKAGES_ZIP_PATH, "r") as z:
            z.extractall(os.path.abspath(util.get_home_dir()))
        log.info("afterInstallScript was successfully executed")

    assert os.path.exists(util.get_home_dir())
    assert os.path.exists(PathsManager.SETTINGS_PATH)

if __name__ == '__main__':
    run()