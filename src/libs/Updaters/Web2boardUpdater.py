import logging
import os
import platform
import shutil
import sys
import time

from libs import utils
from libs.Decorators.Asynchronous import asynchronous
from libs.Downloader import Downloader
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo

__globalWeb2BoardUpdater = None


class Web2BoardUpdater(Updater):
    DOWNLOAD_LINK_TEMPLATE = "https://github.com/bq/web2board/archive/devel.zip"

    log = logging.getLogger(__name__)

    def __init__(self, copyOriginName=None, copyNewName=None):
        Updater.__init__(self)
        self.currentVersionInfoPath = os.path.join(PathsManager.RES_PATH, "web2board.version")
        self.settingsVersionInfo = None
        self.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/res/common/web2board.version"  # todo: recheck this
        self.destinationPath = PathsManager.getOriginalPathForUpdate()
        self.name = "Web2BoardUpdater"

        copyPath = PathsManager.getCopyPathForUpdate()
        if copyOriginName is None:
            copyOriginName = "web2board" + utils.getOsExecutableExtension()
        if copyNewName is None:
            copyNewName = "web2board_copy" + utils.getOsExecutableExtension()
        self.__copyOriginName = os.path.join(copyPath, copyOriginName)
        self.__copyNewName = os.path.join(copyPath, copyNewName)

        self.readCurrentVersionInfo()
        self.downloader = Downloader(refreshTime=1)

    def _areWeMissingLibraries(self):
        return False

    def getDownloadUrl(self, onlineVersionInfo=None):
        if onlineVersionInfo is None:
            onlineVersionInfo = self.downloadOnlineVersionInfo()

        args = dict(arch=64 if utils.is64bits() else 32,
                    os=platform.system(),
                    version=onlineVersionInfo.version)

        return self.DOWNLOAD_LINK_TEMPLATE.format(**args)

    @asynchronous()
    def downloadVersion(self, version):
        confirmationPath = PathsManager.getDstPathForUpdate(version) + ".confirm"
        zipDstPath = PathsManager.getDstPathForUpdate(version) + ".zip"
        if not os.path.exists(confirmationPath):
            url = getWeb2boardUpdater().getDownloadUrl(VersionInfo(version))
            self.downloader.download(url, dst=zipDstPath,
                                     infoCallback=lambda x, y, p: sys.stdout.write(str(p) + "\n")).get()
            utils.extractZip(zipDstPath, PathsManager.getDstPathForUpdate(version))
            os.remove(zipDstPath)
            with open(confirmationPath, "w"):
                pass

    def makeAnAuxiliaryCopyAndRunIt(self, version):
        try:
            self.log.info("Creating an auxiliary copy of the program")
            if os.path.exists(PathsManager.getCopyPathForUpdate()):
                shutil.rmtree(PathsManager.getCopyPathForUpdate())
            shutil.copytree(PathsManager.MAIN_PATH, PathsManager.getCopyPathForUpdate())
            os.rename(self.__copyOriginName, self.__copyNewName)
        except Exception:
            self.log.critical("Upload process finished due to a problem in the uploader", exc_info=1)

    def runAuxiliaryCopy(self, version):
        try:
            self.log.info("Running auxiliary copy")
            os.popen('"{0} --update2version {1}" &'.format(self.__copyNewName, version))
            self.log.info("waiting to be finished")
            time.sleep(10)
            raise Exception("Program not ended after calling copy")
        except Exception:
            self.log.critical("Upload process finished due to a problem in the uploader", exc_info=1)

    def update(self, zipFilePath):
        if PathsManager.MAIN_PATH != PathsManager.getCopyPathForUpdate():
            raise Exception("Unable to update, we are in the original version")
        self.log.info("updating in process")
        self.log.debug("killing original web2board")
        utils.killProcess("web2board")
        if os.path.exists(PathsManager.getOriginalPathForUpdate()):
            self.log.info("removing original files")
            shutil.rmtree(PathsManager.getOriginalPathForUpdate())
        self.log.info("extracting files")
        utils.extractZip(zipFilePath, PathsManager.getOriginalPathForUpdate())
        sys.exit(1)


def getWeb2boardUpdater():
    """
    :rtype: Web2BoardUpdater
    """
    global __globalWeb2BoardUpdater
    if __globalWeb2BoardUpdater is None:
        __globalWeb2BoardUpdater = Web2BoardUpdater()
    return __globalWeb2BoardUpdater
