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

        self.onlineVersionUrl = None
        """:type : str """

        self.destinationPath = None
        """:type : str """

        self.name = "Updater"

    def _getCurrentVersionNumber(self):
        return self.getVersionNumber(self.currentVersionInfo)

    def _areWeMissingLibraries(self):
        log.debug("[{0}] Checking library names".format(self.name))
        if not os.path.exists(self.destinationPath):
            return True
        libraries = utils.listDirectoriesInPath(self.destinationPath)
        libraries = map(lambda x: x.lower(), libraries)
        for cLibrary in self.currentVersionInfo.librariesNames:
            if cLibrary.lower() not in libraries:
                return True

        return len(self.currentVersionInfo.librariesNames) > len(libraries)

    def _isVersionDifferentToCurrent(self, versionToCheck):
        """
        :type versionToCheck: VersionInfo
        """
        logArgs = self.name, self.currentVersionInfo.version, versionToCheck.version
        log.debug("[{0}] Checking version {1} - {2}".format(*logArgs))
        return self._getCurrentVersionNumber() != self.getVersionNumber(versionToCheck)

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        raise NotImplementedError

    def _updateCurrentVersionInfoTo(self, versionToUpload):
        """
        :type versionToUpload: VersionInfo
        """
        log.debug("[{0}] Updating version to: {1}".format(self.name, versionToUpload.version))
        self.currentVersionInfo.version = versionToUpload.version
        self.currentVersionInfo.file2DownloadUrl = versionToUpload.file2DownloadUrl
        self.currentVersionInfo.librariesNames = utils.listDirectoriesInPath(self.destinationPath)
        with open(self.currentVersionInfoPath, 'w') as cvpf:
            json.dump(self.currentVersionInfo.getDictionary(), cvpf, indent=4)
        log.info("Current version updated")

    def getVersionNumber(self, versionInfo=None):
        """
        :type versionInfo: VersionInfo
        """
        versionInfo = self.currentVersionInfo if versionInfo is None else versionInfo
        return int(versionInfo.version.replace('.', ''))

    def readCurrentVersionInfo(self):
        try:
            if not os.path.exists(self.currentVersionInfoPath):
                self.currentVersionInfo = VersionInfo(self.NONE_VERSION)
                logText = "[{0}] Unable to find version in settings path: {1}"
                log.warning(logText.format(self.name, self.currentVersionInfoPath))
                return self.currentVersionInfo
            with open(self.currentVersionInfoPath) as versionFile:
                jsonVersion = json.load(versionFile)
            self.currentVersionInfo = VersionInfo(**jsonVersion)
            log.debug("[{0}] Read current version: {1}".format(self.name, self.currentVersionInfo.version))
        except:
            log.error("unable to read currentVersionInfo")
            self.currentVersionInfo = VersionInfo(self.NONE_VERSION)

        return self.currentVersionInfo

    def downloadOnlineVersionInfo(self):
        jsonVersion = json.loads(utils.getDataFromUrl(self.onlineVersionUrl))
        onlineVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Downloaded online version: {1}".format(self.name, onlineVersionInfo.version))
        return onlineVersionInfo

    def isNecessaryToUpdate(self, versionToCompare=None):
        """
        :type versionToCompare: VersionInfo
        """
        versionToCompare = self.currentVersionInfo if versionToCompare is None else versionToCompare
        return self._isVersionDifferentToCurrent(versionToCompare) or self._areWeMissingLibraries()

    def update(self, versionToUpload):
        log.info('[{0}] Downloading version {1}, from {2}'
                 .format(self.name, versionToUpload.version, versionToUpload.file2DownloadUrl))
        downloadedFilePath = utils.downloadFile(versionToUpload.file2DownloadUrl)
        extractFolder = tempfile.gettempdir() + os.sep + "web2board_tmp_folder"
        if not os.path.exists(extractFolder):
            os.mkdir(extractFolder)
        try:
            log.info('[{0}] extracting zipfile: {1}'.format(self.name, downloadedFilePath))
            utils.extractZip(downloadedFilePath, extractFolder)
            self._moveDownloadedToDestinationPath(extractFolder)
            self._updateCurrentVersionInfoTo(versionToUpload)
        finally:
            if os.path.exists(downloadedFilePath):
                os.unlink(downloadedFilePath)
            if os.path.exists(extractFolder):
                shutil.rmtree(extractFolder)
