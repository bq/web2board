import os
import zipfile

import click

from libs.LoggingUtils import initLogging
from libs.PathsManager import PathsManager as pm
from libs.utils import findFiles
from platformio import util
from platformio.platforms.base import PlatformFactory


def run():
    log = initLogging(__name__)
    originalCurrentDirectory = os.getcwd()
    def clickConfirm(message):
        print message
        return True

    click.confirm = clickConfirm
    try:
        os.chdir(pm.SETTINGS_PLATFORMIO_PATH)
        config = util.get_project_config()
        for section in config.sections():
            envOptionsDict = {x[0]: x[1] for x in config.items(section)}
            platform = PlatformFactory.newPlatform(envOptionsDict["platform"])
            log.info("getting packages for: {}".format(envOptionsDict))
            platform.configure_default_packages(envOptionsDict, ["upload"])
            platform._install_default_packages()

        log.info("all packages where successfully installed")
        platformIOPackagesSettingsPath = os.path.abspath(util.get_home_dir())
        log.info("constructing zip file in : {}".format(pm.RES_PLATFORMIO_PACKAGES_ZIP_PATH))
        packagesFiles = findFiles(platformIOPackagesSettingsPath, ["appstate.json", "packages/**/*"])
        packagesFiles = [x[len(platformIOPackagesSettingsPath)+1:] for x in packagesFiles]
        os.chdir(platformIOPackagesSettingsPath)
        with zipfile.ZipFile(pm.RES_PLATFORMIO_PACKAGES_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
            for zipFilePath in packagesFiles:
                log.debug("adding file: {}".format(zipFilePath))
                z.write(zipFilePath)

        log.info("zip file constructed")

    finally:
        os.chdir(originalCurrentDirectory)

if __name__ == '__main__':
    run()