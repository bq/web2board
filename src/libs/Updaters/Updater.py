import json
import logging
import os
import tempfile

import shutil

from libs import utils

log = logging.getLogger(__name__)


class VersionInfo:
    def __init__(self, version, file2DownloadUrl, librariesNames=list()):
        self.version = version
        """:type : str """
        self.file2DownloadUrl = file2DownloadUrl
        """:type : str """
        self.librariesNames = librariesNames

    def getDictionary(self):
        return self.__dict__


class Updater:
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

    def _reloadVersion(self):
        self.readCurrentVersionInfo()
        self.downloadOnlineVersionInfo()

    def _getVersionNumber(self, versionInfo):
        return int(versionInfo.version.replace('.', ''))

    def _getCurrentVersionNumber(self):
        return self._getVersionNumber(self.currentVersionInfo)

    def _getOnlineVersionNumber(self):
        return self._getVersionNumber(self.onlineVersionInfo)

    def _areWeMissingLibraries(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersion()
        log.debug("[{0}] Checking library names".format(self.name))
        libraries = utils.listDirectoriesInPath(self.destinationPath)
        libraries = map(lambda x: x.lower(), libraries)
        for cLibrary in self.currentVersionInfo.librariesNames:
            if cLibrary.lower() not in libraries:
                return True

        return len(self.currentVersionInfo.librariesNames) > len(libraries)

    def _checkVersions(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersion()

        return self._getCurrentVersionNumber() != self._getOnlineVersionNumber()

    def _updateVersionInfo(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersion()

        log.debug("[{0}] Updating version to: {}".format(self.name, self.onlineVersionInfo.version))
        with open(self.currentVersionInfoPath, 'w') as currentVersionFile:
            json.dump(self.onlineVersionInfo.getDictionary(), currentVersionFile, indent=4)

        self.currentVersionInfo = self.onlineVersionInfo

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)
        utils.copytree(downloadedPath, self.destinationPath, forceCopy=True)

    def readCurrentVersionInfo(self):
        log.debug("[{0}] Reading current version info".format(self.name))
        with open(self.currentVersionInfoPath) as versionFile:
            jsonVersion = json.load(versionFile)
        self.currentVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Read current version: {1}".format(self.name, self.currentVersionInfo.version))
        return self.currentVersionInfo

    def downloadOnlineVersionInfo(self):
        log.debug("[{0}] Downloading online version info".format(self.name))
        jsonVersion = json.loads(utils.getDataFromUrl(self.onlineVersionUrl))
        self.onlineVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Downloaded online version: {1}".format(self.name, self.onlineVersionInfo.version))
        return self.onlineVersionInfo

    def isNecessaryToUpdate(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersion()

        return self._checkVersions() or self._areWeMissingLibraries()

    def update(self, reloadVersions=False):
        if reloadVersions:
            self._reloadVersion()
        log.info(
                '[{0}] Downloading version {1}, from {2}'.format(self.name, self.onlineVersionInfo,
                                                                 self.onlineVersionUrl))
        downloadedFilePath = utils.downloadFile(self.onlineVersionInfo.file2DownloadUrl)
        extractFolder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
        os.mkdir(extractFolder)
        try:
            log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloadedFilePath))
            utils.extractZip(downloadedFilePath, extractFolder)
            self._moveDownloadedToDestinationPath(extractFolder)
        finally:
            if os.path.exists(downloadedFilePath):
                os.unlink(downloadedFilePath)
            if os.path.exists(extractFolder):
                shutil.rmtree(extractFolder)

