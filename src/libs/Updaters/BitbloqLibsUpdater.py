import logging
import os
import tempfile
import shutil
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
        self.current_version_info = VersionInfo(Version.bitbloq_libs,
                                                libraries_names=Version.bitbloq_libs_libraries)
        self.destinationPath = Config.get_platformio_lib_dir()
        self.name = "BitbloqLibsUpdater"

    def _update_current_version_to(self, version_to_upload):
        Updater._update_current_version_to(self, version_to_upload)

        Version.bitbloq_libs_libraries = self.current_version_info.libraries_names
        Version.bitbloq_libs = self.current_version_info.version
        Version.store_values()

    def _move_libs_to_destination(self, downloaded_path):
        directories_in_folder = utils.list_directories_in_path(downloaded_path)
        if len(directories_in_folder) != 1:
            raise BitbloqLibsUpdaterError("Not only one bitbloqLibs folder in unzipped file")
        downloaded_path = downloaded_path + os.sep + directories_in_folder[0]

        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloaded_path, self.destinationPath, force_copy=True)

    def restore_current_version_if_necessary(self):
        if self.isNecessaryToUpdate():
            log.warning("It is necessary to upload BitbloqLibs")
            url = Config.bitbloq_libs_download_url_template.format(**self.current_version_info.__dict__)
            self.current_version_info.file_to_download_url = url
            self.update(self.current_version_info)
        else:
            log.debug("BitbloqLibs is up to date")

    def update(self, versionToUpload):
        log.info('[{0}] Downloading version {1}, from {2}'
                 .format(self.name, versionToUpload.version, versionToUpload.file_to_download_url))
        downloadedFilePath = tempfile.gettempdir() + os.sep + "w2b_tmp_libs.zip"
        self.downloader.download(versionToUpload.file_to_download_url, downloadedFilePath).result()

        extractFolder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
        if not os.path.exists(extractFolder):
            os.mkdir(extractFolder)
        try:
            log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloadedFilePath))
            utils.extract_zip(downloadedFilePath, extractFolder)
            self._move_libs_to_destination(extractFolder)
            self._update_current_version_to(versionToUpload)
        finally:
            if os.path.exists(extractFolder):
                shutil.rmtree(extractFolder)


