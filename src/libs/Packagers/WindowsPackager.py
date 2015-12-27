from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *

log = logging.getLogger(__name__)


class WindowsPackager(Packager):
    def __init__(self):
        Packager.__init__(self)
        self.versionPath = self.web2boardPath + os.sep + "win_web2board_{}".format(self.version)
        self.installerPath = self.installerFolder + os.sep + "win32"
        self.winDist = os.path.join(self.versionPath, "dist")
        self.folderVersionName = os.path.basename(self.versionPath)
        self.winMetadataPath = os.path.join(self.pkgPath, "win32")
        self.executableResPath = os.path.join(self.winDist, "res")

    def _clearMainFolders(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)
        if os.path.exists(self.installerPath):
            shutil.rmtree(self.installerPath)
        self._clearBuildFiles()

    def _makeMainDirs(self):
        os.makedirs(self.versionPath)
        os.makedirs(self.winDist)
        os.makedirs(self.executableResPath)
        os.makedirs(self.installerPath)

    def _addResFilesForExecutable(self):
        copytree(os.path.join(self.resPath, "common"), self.executableResPath)
        copytree(os.path.join(self.resPath, "windows"), self.executableResPath)

    def _addBatScripsToWinDist(self):
        batName = "afterInstall.bat"
        shutil.copy2(self.versionPath + os.sep + batName, self.winDist + os.sep + batName)

    def _addMetadataForInstaller(self):
        copytree(self.winMetadataPath, self.versionPath)
        self._addBatScripsToWinDist()

    def _deleteVersionFolder(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)

    def _moveInstallerToInstallerFolder(self):
        shutil.copy2(self.versionPath + os.sep + "Web2board.exe", self.installerPath + os.sep + "Web2board.exe")

    def createPackage(self):
        try:
            log.debug("Removing main folders")
            self._clearMainFolders()
            log.debug("Creating main folders")
            self._makeMainDirs()
            log.debug("Adding resources for executable")
            self._addResFilesForExecutable()
            log.info("Constructing executable")
            self._constructAndMoveExecutable()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.versionPath)
            log.info("Creating Installer")
            call(["makensis", "installer.nsi"])
            self._moveInstallerToInstallerFolder()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearBuildFiles()
            self._deleteVersionFolder()
