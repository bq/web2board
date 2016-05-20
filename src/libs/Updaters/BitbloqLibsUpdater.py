import logging
import os
import tempfile

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
                                              libraries_names=Version.bitbloq_libs_libraries)
        self.destinationPath = Config.get_platformio_lib_dir()
        self.name = "BitbloqLibsUpdater"

    def _updateCurrentVersionInfoTo(self, versionToUpload):
        Updater._updateCurrentVersionInfoTo(self, versionToUpload)

        Version.bitbloq_libs_libraries = self.currentVersionInfo.libraries_names
        Version.bitbloq_libs = self.currentVersionInfo.version
        Version.store_values()

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        directories_in_folder = utils.list_directories_in_path(downloadedPath)
        if len(directories_in_folder) != 1:
            raise BitbloqLibsUpdaterError("Not only one bitbloqLibs folder in unzipped file")
        downloadedPath = downloadedPath + os.sep + directories_in_folder[0]

        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloadedPath, self.destinationPath, force_copy=True)

    def restoreCurrentVersionIfNecessary(self):
        if self.isNecessaryToUpdate():
            log.warning("It is necessary to upload BitbloqLibs")
            url = Config.bitbloq_libs_download_url_template.format(**self.currentVersionInfo.__dict__)
            self.currentVersionInfo.file_to_download_url = url
            self.update(self.currentVersionInfo)
        else:
            log.debug("BitbloqLibs is up to date")

    def update(self, versionToUpload):
        log.info('[{0}] Downloading version {1}, from {2}'
                 .format(self.name, versionToUpload.version, versionToUpload.file2DownloadUrl))
        downloadedFilePath = tempfile.gettempdir() + os.sep + "w2b_tmp_libs.zip"
        self.downloader.download(versionToUpload.file2DownloadUrl, downloadedFilePath).result()

        extractFolder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
        if not os.path.exists(extractFolder):
            os.mkdir(extractFolder)
        try:
            log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloadedFilePath))
            utils.extract_zip(downloadedFilePath, extractFolder)
            self._moveDownloadedToDestinationPath(extractFolder)
            self._updateCurrentVersionInfoTo(versionToUpload)
        finally:
            if os.path.exists(extractFolder):
                shutil.rmtree(extractFolder)


