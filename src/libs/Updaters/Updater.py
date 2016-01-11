import json
import logging
import os
import tempfile

import shutil

from libs import utils

log = logging.getLogger(__name__)


class VersionInfo:
    def __init__(self, version, file2DownloadUrl="", librariesNames=list()):
        self.version = version
        """:type : str """
        self.file2DownloadUrl = file2DownloadUrl
        """:type : str | dict """
        self.librariesNames = librariesNames

    def getDictionary(self):
        return self.__dict__


class Updater:
    NONE_VERSION = "0.0.0"

    def __init__(self):
        self.currentVersionInfo = None
        """:type : VersionInfo """
        self.currentVersionInfoPath = None
        """:type : str """

        self.onlineVersionInfo = None
        """:type : VersionInfo """
        self.onlineVersionUrl = None
        """:type : str """

        self.destinationPath = None
        """:type : str """

        self.name = "Updater"

    def _reloadVersions(self):
        self.readCurrentVersionInfo()
        self.downloadOnlineVersionInfo()

    def _getCurrentVersionNumber(self):
        return self.getVersionNumber(self.currentVersionInfo)

    def _getOnlineVersionNumber(self):
        return self.getVersionNumber(self.onlineVersionInfo)

    def _areWeMissingLibraries(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersions()
        log.debug("[{0}] Checking library names".format(self.name))
        libraries = utils.listDirectoriesInPath(self.destinationPath)
        libraries = map(lambda x: x.lower(), libraries)
        for cLibrary in self.currentVersionInfo.librariesNames:
            if cLibrary.lower() not in libraries:
                return True

        return len(self.currentVersionInfo.librariesNames) > len(libraries)

    def _checkVersions(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersions()

        return self._getCurrentVersionNumber() != self._getOnlineVersionNumber()

    def _updateVersionInfo(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersions()

        log.debug("[{0}] Updating version to: {}".format(self.name, self.onlineVersionInfo.version))
        with open(self.currentVersionInfoPath, 'w') as currentVersionFile:
            json.dump(self.onlineVersionInfo.getDictionary(), currentVersionFile, indent=4)

        self.currentVersionInfo = self.onlineVersionInfo

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        raise NotImplementedError

    def _updateCurrentVersionInfo(self):
        self.currentVersionInfo.version = self.onlineVersionInfo.version
        self.currentVersionInfo.file2DownloadUrl = self.onlineVersionInfo.file2DownloadUrl
        self.currentVersionInfo.librariesNames = utils.listDirectoriesInPath(self.destinationPath)

    def getVersionNumber(self, versionInfo):
        """
        :type versionInfo: VersionInfo
        """
        return int(versionInfo.version.replace('.', ''))

    def readCurrentVersionInfo(self):
        if not os.path.exists(self.currentVersionInfoPath):
            self.currentVersionInfo = VersionInfo(self.NONE_VERSION)
            logText = "[{0}] Unable to find version in settings path: {1}"
            log.warning(logText.format(self.name, self.currentVersionInfoPath))
            return self.currentVersionInfo
        with open(self.currentVersionInfoPath) as versionFile:
            jsonVersion = json.load(versionFile)
        self.currentVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Read current version: {1}".format(self.name, self.currentVersionInfo.version))
        return self.currentVersionInfo

    def downloadOnlineVersionInfo(self):
        jsonVersion = json.loads(utils.getDataFromUrl(self.onlineVersionUrl))
        self.onlineVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Downloaded online version: {1}".format(self.name, self.onlineVersionInfo.version))
        return self.onlineVersionInfo

    def isNecessaryToUpdate(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersions()

        return self._checkVersions() or self._areWeMissingLibraries()

    def update(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersions()
        log.info('[{0}] Downloading version {1}, from {2}'
                 .format(self.name, self.onlineVersionInfo.version, self.onlineVersionInfo.file2DownloadUrl))
        downloadedFilePath = utils.downloadFile(self.onlineVersionInfo.file2DownloadUrl)
        extractFolder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
        if not os.path.exists(extractFolder):
            os.mkdir(extractFolder)
        try:
            log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloadedFilePath))
            utils.extractZip(downloadedFilePath, extractFolder)
            self._moveDownloadedToDestinationPath(extractFolder)
            self._updateCurrentVersionInfo()
        finally:
            if os.path.exists(downloadedFilePath):
                os.unlink(downloadedFilePath)
            if os.path.exists(extractFolder):
                shutil.rmtree(extractFolder)
