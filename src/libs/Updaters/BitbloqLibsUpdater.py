import logging
import os

from libs import utils
from libs.Config import Config
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo

log = logging.getLogger(__name__)
__globalBitbloqLibsUpdater = None


class BitbloqLibsUpdaterError(Exception):
    pass


class BitbloqLibsUpdater(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.currentVersionInfo = VersionInfo(Config.bitbloqLibsVersion, librariesNames=Config.bitbloqLibsLibraries)
        self.destinationPath = os.path.join(PathsManager.PLATFORMIO_WORKSPACE_SKELETON, "lib")
        self.name = "BitbloqLibsUpdater"

    def _updateCurrentVersionInfoTo(self, versionToUpload):
        Updater._updateCurrentVersionInfoTo(self, versionToUpload)

        Config.bitbloqLibsLibraries = self.currentVersionInfo.librariesNames
        Config.bitbloqLibsVersion = self.currentVersionInfo.version
        Config.storeConfigInFile()

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        directoriesInUnzippedFolder = utils.listDirectoriesInPath(downloadedPath)
        if len(directoriesInUnzippedFolder) != 1:
            raise BitbloqLibsUpdaterError("Not only one bitbloqLibs folder in unzipped file")
        downloadedPath = downloadedPath + os.sep + utils.listDirectoriesInPath(downloadedPath)[0]

        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloadedPath, self.destinationPath, forceCopy=True)

    def restoreCurrentVersionIfNecessary(self):
        if self.isNecessaryToUpdate():
            log.warning("It is necessary to upload BitbloqLibs")
            url = Config.bitbloqLibsDownloadUrlTemplate.format(**self.currentVersionInfo.__dict__)
            self.currentVersionInfo.file2DownloadUrl = url
            self.update(self.currentVersionInfo)
        else:
            log.debug("BitbloqLibs is up to date")


def getBitbloqLibsUpdater():
    """
    :rtype: BitbloqLibsUpdater
    """
    global __globalBitbloqLibsUpdater
    if __globalBitbloqLibsUpdater is None:
        __globalBitbloqLibsUpdater = BitbloqLibsUpdater()
    return __globalBitbloqLibsUpdater
