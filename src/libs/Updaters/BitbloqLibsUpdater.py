import logging
import os

from libs import utils
from libs.Config import Config
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo
from libs.Version import Version

log = logging.getLogger(__name__)


class BitbloqLibsUpdaterError(Exception):
    pass


class BitbloqLibsUpdater(Updater):
    __globalBitbloqLibsUpdater = None

    def __init__(self):
        Updater.__init__(self)
        self.currentVersionInfo = VersionInfo(Version.bitbloq_libs,
                                              librariesNames=Version.bitbloq_libs_libraries)
        self.destinationPath = os.path.join(PathsManager.PLATFORMIO_WORKSPACE_SKELETON, "lib")
        self.name = "BitbloqLibsUpdater"

    def _updateCurrentVersionInfoTo(self, versionToUpload):
        Updater._updateCurrentVersionInfoTo(self, versionToUpload)

        Version.bitbloq_libs_libraries = self.currentVersionInfo.librariesNames
        Version.bitbloq_libs = self.currentVersionInfo.version
        Version.store_values()

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        directoriesInUnzippedFolder = utils.list_directories_in_path(downloadedPath)
        if len(directoriesInUnzippedFolder) != 1:
            raise BitbloqLibsUpdaterError("Not only one bitbloqLibs folder in unzipped file")
        downloadedPath = downloadedPath + os.sep + utils.list_directories_in_path(downloadedPath)[0]

        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloadedPath, self.destinationPath, force_copy=True)

    def restoreCurrentVersionIfNecessary(self):
        if self.isNecessaryToUpdate():
            log.warning("It is necessary to upload BitbloqLibs")
            url = Config.bitbloq_libs_download_url_template.format(**self.currentVersionInfo.__dict__)
            self.currentVersionInfo.file2DownloadUrl = url
            self.update(self.currentVersionInfo)
        else:
            log.debug("BitbloqLibs is up to date")

