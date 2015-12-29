from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *

log = logging.getLogger(__name__)


class MacPackager(Packager):
    def __init__(self):
        Packager.__init__(self)
        self.versionPath = self.web2boardPath + os.sep + "darwin_web2board_{}".format(self.version)
        self.installerPath = self.installerFolder + os.sep + "darwin"
        self.macDist = os.path.join(self.versionPath, "dist")
        self.folderVersionName = os.path.basename(self.versionPath)
        self.macMetadataPath = os.path.join(self.pkgPath, "darwin")
        self.executableResPath = os.path.join(self.macDist, "res")

    def _clearMainFolders(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)
        if os.path.exists(self.installerPath):
            shutil.rmtree(self.installerPath)
        self._clearBuildFiles()

    def _makeMainDirs(self):
        os.makedirs(self.versionPath)
        os.makedirs(self.macDist)
        os.makedirs(self.executableResPath)
        os.makedirs(self.installerPath)

    def _addResFilesForExecutable(self):
        copytree(os.path.join(self.resPath, "common"), self.executableResPath)
        copytree(os.path.join(self.resPath, "darwin"), self.executableResPath)

    def _addMetadataForInstaller(self):
        copytree(self.macMetadataPath, self.versionPath)

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            call(["pyinstaller", "--onefile", "web2board.py"])
            call(["pyinstaller", "--onefile", "SerialMonitor.py"])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, "web2board.exe"), self.macDist)
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, "SerialMonitor.exe"), self.macDist)
        finally:
            os.chdir(currentPath)

    def _deleteVersionFolder(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)

    def _moveInstallerToInstallerFolder(self):
        shutil.copy2(self.versionPath + os.sep + "web2board.exe", self.installerPath + os.sep + "Web2board.exe")

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
            #call(["makensis", "installer.nsi"])
            #self._moveInstallerToInstallerFolder()
            #log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearBuildFiles()
            self._deleteVersionFolder()
