from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *

log = logging.getLogger(__name__)


class WindowsPackager(Packager):
    def __init__(self):
        Packager.__init__(self)
        self.installerPath = self.installerFolder + os.sep + "win32"
        self.installerCreationPath = self.web2boardPath + os.sep + "win_web2board_{}".format(self.version)
        self.installerCreationName = os.path.basename(self.installerCreationPath)
        self.installerCreationDistPath = os.path.join(self.installerCreationPath, "dist")
        self.pkgPlatformPath = os.path.join(self.pkgPath, "win32")
        self.resPlatformPath = os.path.join(self.resPath, "windows")
        self.web2boardExecutableName = "web2board.exe"
        self.serialMonitorExecutableName = "SerialMonitor.exe"

    def _addBatScripsToWinDist(self):
        batName = "afterInstall.bat"
        shutil.copy2(self.installerCreationPath + os.sep + batName, self.installerCreationDistPath + os.sep + batName)

    def _addMetadataForInstaller(self):
        copytree(self.pkgPlatformPath, self.installerCreationPath)
        shutil.copy2(self.iconPath, self.installerCreationPath + os.sep + os.path.basename(self.iconPath))
        self._addBatScripsToWinDist()

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            call(["pyinstaller", "--onefile", "web2board.spec"])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.web2boardExecutableName), self.installerCreationDistPath)
            call(["pyinstaller", "--onefile", "serialMonitor.spec"])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.serialMonitorExecutableName), self.installerCreationDistPath)
        finally:
            os.chdir(currentPath)

    def _moveInstallerToInstallerFolder(self):
        shutil.copy2(self.installerCreationPath + os.sep + "Web2board.exe", self.installerPath)

    def createPackage(self):
        try:
            log.debug("Removing main folders")
            self._clearMainFolders()
            log.debug("Creating main folders")
            self._makeMainDirs()
            log.debug("Adding resources for executable")
            self._prepareResFolderForExecutable()
            log.info("Constructing executable")
            self._constructAndMoveExecutable()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.installerCreationPath)
            log.info("Creating Installer")
            call(["makensis", "installer.nsi"])
            self._moveInstallerToInstallerFolder()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._restoreSrcResFolder()
            self._clearBuildFiles()
            # self._deleteInstallerCreationFolder()
