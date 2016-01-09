import logging
import os
import shutil

from libs import utils
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo

log = logging.getLogger(__name__)
__globalBitbloqLibsUpdater = None


class BitbloqLibsUpdaterError(Exception):
    pass


class BitbloqLibsUpdater(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.currentVersionInfoPath = os.path.join(PathsManager.SETTINGS_PATH, "bitbloqLibs.version")
        self.onlineVersionUrl = "https://github.com/bq/bitbloqLibs/archive/master.zip"  # todo: recheck this
        self.destinationPath = os.path.join(PathsManager.SETTINGS_PLATFORMIO_PATH, "lib")
        self.name = "BitbloqLibsUpdater"
        # self._reloadVersion()

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        directoriesInUnzippedFolder = utils.listDirectoriesInPath(downloadedPath)
        if len(directoriesInUnzippedFolder) != 1:
            raise BitbloqLibsUpdaterError("Not only one bitbloqLibs folder in unzipped file")
        downloadedPath = downloadedPath + os.sep + utils.listDirectoriesInPath(downloadedPath)[0]

        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloadedPath, self.destinationPath, forceCopy=True)

def getBitbloqLibsUpdater():
    """
    :rtype: CompilerUploader
    """
    global __globalBitbloqLibsUpdater
    if __globalBitbloqLibsUpdater is None:
        __globalBitbloqLibsUpdater = BitbloqLibsUpdater()
    return __globalBitbloqLibsUpdater


u = getBitbloqLibsUpdater()
u.onlineVersionInfo = VersionInfo("0.0.1", "https://github.com/bq/bitbloqLibs/archive/master.zip")
u.currentVersionInfo = VersionInfo("0.0.0", "https://github.com/bq/bitbloqLibs/archive/master.zip")
u.update()
