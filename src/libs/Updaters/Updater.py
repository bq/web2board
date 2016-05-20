import json
import logging
import os
import tempfile

import shutil

from libs import utils
from libs.Config import Config
from libs.Downloader import Downloader

log = logging.getLogger(__name__)


class VersionInfo:
    def __init__(self, version, file_to_download_url="", libraries_names=list()):
        self.version = version
        """:type : str """
        self.file_to_download_url = file_to_download_url
        """:type : str | dict """
        self.libraries_names = libraries_names
        try:
            self.__get_version_numbers()
        except (ValueError, AttributeError):
            raise Exception("bad format version: {}".format(version))

    def __eq__(self, other):
        return self.version == other.version

    def __ne__(self, other):
        return self.version != other.version

    def __gt__(self, other):
        zipped = zip(self.__get_version_numbers(), other.__get_version_numbers())
        for s, o in zipped:
            if s > o:
                return True
        return False

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return other >= self

    def __lt__(self, other):
        return other > self

    def __get_version_numbers(self):
        return [int(n) for n in self.version.split(".")]

    def getDictionary(self):
        return self.__dict__


class Updater:
    NONE_VERSION = "0.0.0"

    def __init__(self):
        self.current_version_info = None
        """:type : VersionInfo """

        self.onlineVersionUrl = None
        """:type : str """

        self.destinationPath = None
        """:type : str """

        self.name = "Updater"
        self.downloader = Downloader()

    def _are_we_missing_libraries(self):
        # todo: this is only for librariesUpdater
        log.debug("[{0}] Checking library names".format(self.name))
        if not os.path.exists(self.destinationPath):
            return True
        libraries = utils.list_directories_in_path(self.destinationPath)
        libraries = map(lambda x: x.lower(), libraries)
        for cLibrary in self.current_version_info.libraries_names:
            if cLibrary.lower() not in libraries:
                return True

        return len(self.current_version_info.libraries_names) > len(libraries)

    def _update_current_version_to(self, versionToUpload):
        """
        :type versionToUpload: VersionInfo
        """
        log.debug("[{0}] Updating version to: {1}".format(self.name, versionToUpload.version))
        self.current_version_info.version = versionToUpload.version
        self.current_version_info.file_to_download_url = versionToUpload.file_to_download_url
        self.current_version_info.libraries_names = utils.list_directories_in_path(self.destinationPath)
        log.info("Current version updated")

    def getVersionNumber(self, versionInfo=None):
        """
        :type versionInfo: VersionInfo
        """
        versionInfo = self.current_version_info if versionInfo is None else versionInfo
        return int(versionInfo.version.replace('.', ''))

    def downloadOnlineVersionInfo(self):
        jsonVersion = json.loads(utils.get_data_from_url(self.onlineVersionUrl))
        onlineVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Downloaded online version: {1}".format(self.name, onlineVersionInfo.version))
        return onlineVersionInfo

    def isNecessaryToUpdate(self, versionToCompare=None):
        """
        :type versionToCompare: VersionInfo
        """
        versionToCompare = self.current_version_info if versionToCompare is None else versionToCompare
        logArgs = self.name, self.current_version_info.version, versionToCompare.version
        log.debug("[{0}] Checking version {1} - {2}".format(*logArgs))
        return self.current_version_info != versionToCompare or self._are_we_missing_libraries()