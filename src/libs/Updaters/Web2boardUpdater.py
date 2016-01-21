import logging
import os
import platform
import shutil
import sys
import time

from libs import utils
from libs.Downloader import Downloader
from libs.PathsManager import PathsManager
from libs.Updaters.Updater import Updater

log = logging.getLogger(__name__)
__globalWeb2BoardUpdater = None


class Web2BoardUpdater(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.currentVersionInfoPath = os.path.join(PathsManager.RES_PATH, "web2board.version")
        self.settingsVersionInfo = None
        self.onlineVersionUrl = "https://raw.githubusercontent.com/bq/web2board/devel/res/common/web2board.version"  # todo: recheck this
        self.destinationPath = PathsManager.RES_PATH + os.sep + "web2board_installer.txt"
        self.name = "Web2BoardUpdater"

        copyPath = PathsManager.getCopyPathForUpdate()
        self.__copyOriginName = os.path.join(copyPath, "web2board" + utils.getOsExecutableExtension())
        self.__copyNewName = os.path.join(copyPath, "web2board_copy" + utils.getOsExecutableExtension())

        self.readCurrentVersionInfo()
        self.downloader = Downloader()

    def _areWeMissingLibraries(self):
        return False

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

    def makeAnAuxiliaryCopyAndRunIt(self):
        log.info("Creating an auxiliary copy of the program")
        if not os.path.exists(PathsManager.getCopyPathForUpdate()):
            os.mkdir(PathsManager.getCopyPathForUpdate())
        shutil.rmtree(PathsManager.getCopyPathForUpdate())
        shutil.copytree(PathsManager.MAIN_PATH, PathsManager.getCopyPathForUpdate())
        os.rename(self.__copyOriginName, self.__copyNewName)
        log.info("Running auxiliary copy")
        os.popen('"{}" &'.format(self.__copyNewName))
        log.info("waiting to be finished")
        time.sleep(10)
        log.critical("Upload process finished due to a problem in the uploader")

    def update(self, versionToUpload=None):
        if PathsManager.MAIN_PATH != PathsManager.getCopyPathForUpdate():
            raise Exception("Unable to update, we are in the original version")
        print "updating process"
        print "killing original web2board"
        utils.killProcess("web2board")
        if os.path.exists(PathsManager.getOriginalPathForUpdate()):
            print "removing original files"
            shutil.rmtree(PathsManager.getOriginalPathForUpdate())
        print "extracting files"
        utils.extractZip("C:\Users\jorgarira\AppData\Roaming\\web2board.zip", PathsManager.getOriginalPathForUpdate())
        sys.exit(1)


def getWeb2boardUpdater():
    """
    :rtype: CompilerUploader
    """
    global __globalWeb2BoardUpdater
    if __globalWeb2BoardUpdater is None:
        __globalWeb2BoardUpdater = Web2BoardUpdater()
    return __globalWeb2BoardUpdater
