import json
import logging
import os
import platform
import shutil

import subprocess

from libs import utils

from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater, VersionInfo

log = logging.getLogger(__name__)
__globalWeb2BoardUpdater = None


class Web2BoardUpdater(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.currentVersionInfoPath = os.path.join(PathsManager.RES_PATH, "web2board.version")
        self.settingsVersionInfoPath = os.path.join(PathsManager.SETTINGS_PATH, "web2board.version")
        self.settingsVersionInfo = None
        self.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/res/common/web2board.version"  # todo: recheck this
        self.destinationPath = PathsManager.SETTINGS_PATH + os.sep + "web2board_installer.txt"
        self.name = "Web2BoardUpdater"

        self.readCurrentVersionInfo()
        self.readSettingsVersionInfo()

    def _areWeMissingLibraries(self):
        return False

    def _getSettingsVersionNumber(self):
        return self.getVersionNumber(self.settingsVersionInfo)

    def _getDownloadUrl(self):
        onlineVersionInfo = self.downloadOnlineVersionInfo()
        if utils.isLinux():
            if utils.is64bits():
                downloadUrl = onlineVersionInfo.file2DownloadUrl["linux64"]
            else:
                downloadUrl = onlineVersionInfo.file2DownloadUrl["linux32"]
        elif utils.isMac():
            downloadUrl = onlineVersionInfo.file2DownloadUrl["Mac"]
        elif utils.isWindows():
            downloadUrl = onlineVersionInfo.file2DownloadUrl["windows"]
        else:
            raise Exception("Platform: {} not supported".format(platform.system()))
        return downloadUrl

    def _moveDownloadedToDestinationPath(self, downloadedPath):
        if os.path.exists(self.destinationPath) and os.path.isdir(self.destinationPath):
            shutil.rmtree(self.destinationPath)
        os.rename(downloadedPath, self.destinationPath)

    def isNecessaryToUpdateSettings(self, reloadVersions=False):
        if reloadVersions:
            self.readCurrentVersionInfo()
            self.readSettingsVersionInfo()

        return self._getCurrentVersionNumber() != self._getSettingsVersionNumber()

    def readSettingsVersionInfo(self):
        if not os.path.exists(self.settingsVersionInfoPath):
            self.settingsVersionInfo = VersionInfo(self.NONE_VERSION)
            logText = "[{0}] Unable to find version in settings path: {1}"
            log.warning(logText.format(self.name, self.settingsVersionInfoPath))
            return self.settingsVersionInfo
        with open(self.settingsVersionInfoPath) as versionFile:
            jsonVersion = json.load(versionFile)
        self.settingsVersionInfo = VersionInfo(**jsonVersion)
        log.debug("[{0}] Read settings version: {1}".format(self.name, self.settingsVersionInfo.version))
        return self.settingsVersionInfo

    def update(self, versionToUpload = None):


        downloadUrl = self._getDownloadUrl()

        log.debug("[{0}] Downloading installer from: {1}".format(self.name, downloadUrl))
        downloadedPath = utils.downloadFile(downloadUrl)
        self._moveDownloadedToDestinationPath(downloadedPath)
        log.debug("[{0}] Downloaded installer successfully".format(self.name))
        subprocess.call(self.destinationPath, shell=True)


def getWeb2boardUpdater():
    """
    :rtype: CompilerUploader
    """
    global __globalWeb2BoardUpdater
    if __globalWeb2BoardUpdater is None:
        __globalWeb2BoardUpdater = Web2BoardUpdater()
    return __globalWeb2BoardUpdater
