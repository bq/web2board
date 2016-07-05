import logging
import os
import tempfile
import shutil
from libs import utils
from libs.Config import Config
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo
from libs.AppVersion import AppVersion
import threading

log = logging.getLogger(__name__)


class BitbloqLibsUpdaterError(Exception):
    pass


class BitbloqLibsUpdater(Updater):
    __globalBitbloqLibsUpdater = None
    update_lock = threading.Lock()

    def __init__(self):
        Updater.__init__(self)
        self.current_version_info = VersionInfo(AppVersion.libs,
                                                libraries_names=AppVersion.bitbloq_libs_libraries)
        self.name = "BitbloqLibsUpdater"

    @property
    def destination_path(self):
        return Config.get_platformio_lib_dir()

    def _update_current_version_to(self, version_to_upload):
        Updater._update_current_version_to(self, version_to_upload)

        AppVersion.bitbloq_libs_libraries = self.current_version_info.libraries_names
        AppVersion.libs = self.current_version_info.version
        AppVersion.store_values()

    def _move_libs_to_destination(self, downloaded_path):
        directories_in_folder = utils.list_directories_in_path(downloaded_path)
        if len(directories_in_folder) != 1:
            raise BitbloqLibsUpdaterError("Not only one libs folder in unzipped file")
        downloaded_path = downloaded_path + os.sep + directories_in_folder[0]

        if not os.path.exists(self.destination_path):
            os.makedirs(self.destination_path)
        utils.copytree(downloaded_path, self.destination_path, force_copy=True)

    def restore_current_version_if_necessary(self):
        if self.is_necessary_to_update():
            log.warning("It is necessary to upload BitbloqLibs")
            url = Config.bitbloq_libs_download_url_template.format(**self.current_version_info.__dict__)
            self.current_version_info.file_to_download_url = url
            self.update(self.current_version_info)
        else:
            log.debug("BitbloqLibs is up to date")

    def update(self, version_to_upload):
        with self.update_lock:
            log.info('[{0}] Downloading version {1}, from {2}'
                     .format(self.name, version_to_upload.version, version_to_upload.file_to_download_url))
            downloaded_file_path = tempfile.gettempdir() + os.sep + "w2b_tmp_libs.zip"
            self.downloader.download(version_to_upload.file_to_download_url, downloaded_file_path).result()

            extract_folder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
            if not os.path.exists(extract_folder):
                os.mkdir(extract_folder)
            try:
                log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloaded_file_path))
                utils.extract_zip(downloaded_file_path, extract_folder)
                self._move_libs_to_destination(extract_folder)
                self._update_current_version_to(version_to_upload)
            finally:
                if os.path.exists(extract_folder):
                    shutil.rmtree(extract_folder)


