import logging
import os
import tempfile
import shutil
import threading

from libs import utils
from libs.AppVersion import AppVersion
from libs.Config import Config
from libs.Downloader import Downloader


log = logging.getLogger(__name__)


class LibsUpdaterError(Exception):
    pass


class LibsUpdater:

    replace_libs_lock = threading.Lock()

    def __init__(self):
        self.downloader = Downloader()

    @property
    def destination_path(self):
        return Config.get_platformio_lib_dir()

    def restore_current_version_if_necessary(self):
        if self._are_we_missing_libraries():
            log.warning("Necessary to restore libs")
            self._replace_libs()
            return True
        else:
            log.debug("Libs checked - no need to restore")
            return False

    def is_necessary_to_update(self, version_string):
        log.debug("Checking version %s != %s", AppVersion.libs.version_string, version_string)
        return AppVersion.libs != version_string

    def update(self, version_string, url):
        log.debug("Updating version to: %s", version_string)
        self._replace_libs(version_string, url)
        return True

    ###########################################################################
    # Protected methods
    ###########################################################################
    def _replace_libs(self, version_string=None, url=None):
        version_string = AppVersion.libs.version_string if version_string is None else version_string
        url = AppVersion.libs.url if url is None else url

        with self.replace_libs_lock:
            log.info("Downloading version %s from %s", version_string, url)

            downloaded_zip_file_path = tempfile.gettempdir() + os.sep + "w2b_tmp_libs.zip"
            self.downloader.download(url, downloaded_zip_file_path).result()
            extract_folder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
            if not os.path.exists(extract_folder):
                os.mkdir(extract_folder)
            try:
                log.info('Extracting zipfile: %s', downloaded_zip_file_path)
                utils.extract_zip(downloaded_zip_file_path, extract_folder)
                self._move_libs_to_destination(extract_folder)

                version_values = {"version": version_string,
                                  "librariesNames": utils.list_directories_in_path(self.destination_path),
                                  "url": url}
                AppVersion.libs.set_version_values(version_values)
                AppVersion.store_values()
            finally:
                if os.path.exists(extract_folder):
                    shutil.rmtree(extract_folder)

    def _are_we_missing_libraries(self):
        # todo: this is only for librariesUpdater
        log.debug("Checking library names")
        if not os.path.exists(self.destination_path):
            return True
        libraries = utils.list_directories_in_path(self.destination_path)
        libraries = map(lambda x: x.lower(), libraries)
        for cLibrary in AppVersion.libs.libraries_names:
            if cLibrary.lower() not in libraries:
                return True

        return len(AppVersion.libs.libraries_names) > len(libraries)

    def _move_libs_to_destination(self, downloaded_path):
        directories_in_folder = utils.list_directories_in_path(downloaded_path)
        if len(directories_in_folder) != 1:
            raise LibsUpdaterError("Not only one libs folder in unzipped file")
        downloaded_path = downloaded_path + os.sep + directories_in_folder[0]

        if not os.path.exists(self.destination_path):
            os.makedirs(self.destination_path)
        utils.copytree(downloaded_path, self.destination_path, force_copy=True)

