from subprocess import call

from libs import utils
from libs.Packagers.Packager import Packager
from libs.utils import *

log = logging.getLogger(__name__)


class MacPackager(Packager):
    def __init__(self):
        Packager.__init__(self)

        self.installerPath = self.installerFolder + os.sep + "darwin"
        self.installerCreationPath = self.web2boardPath + os.sep + "darwin_web2board_{}".format(self.version)
        self.installerCreationDistPath = os.path.join(self.installerCreationPath, "dist")
        self.installerCreationName = os.path.basename(self.installerCreationPath)
        self.installerCreationExecutablesPath = os.path.join(self.installerCreationPath, "executables")
        self.pkgPlatformPath = os.path.join(self.pkgPath, "darwin")
        self.resPlatformPath = os.path.join(self.resPath, "darwin")

        self.web2boardExecutableName = "web2board.app"
        self.sconsExecutableName = "sconsScript"

        self.web2boardSpecPath = os.path.join(self.web2boardPath, "web2board-mac.spec")
        self.sconsSpecPath = os.path.join(self.web2boardPath, "scons-mac.spec")

        self.pkgprojPath = os.path.join(self.installerCreationPath, "create-mpkg", "web2board", "web2board.pkgproj")
        self.installerBackgroundPath = os.path.join(self.resPlatformPath, "installer_background.jpg")
        self.licensePath = os.path.join(self.web2boardPath, "LICENSE.txt")

        self.appResourcesPath = os.path.join(self.installerCreationDistPath, self.web2boardExecutableName, "Contents",
                                             "MacOS", "res")

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            log.debug("Creating Scons Executable")
            call(["pyinstaller", self.sconsSpecPath])
            utils.copytree(os.path.join(self.pyInstallerDistFolder, "sconsScript"),
                           os.path.join(self._getInstallerCreationResPath(), "Scons"))

            log.debug("Gettings Scons Packages")
            self._getSconsPackages()

            log.debug("Creating Web2board Executable")
            call(["pyinstaller", '-w', self.web2boardSpecPath])
            shutil.move(os.path.join(self.pyInstallerDistFolder, "web2board.app"), self.installerCreationDistPath)

        finally:
            os.chdir(currentPath)

    def _addMetadataForInstaller(self):
        Packager._addMetadataForInstaller(self)
        copytree(self.pkgPlatformPath, self.installerCreationPath)
        shutil.copy2(self.installerBackgroundPath, self.installerCreationDistPath)
        shutil.copy2(self.licensePath, self.installerCreationDistPath)
        copytree(self._getInstallerCreationResPath(), self.appResourcesPath)

    def _moveInstallerToInstallerFolder(self):
        shutil.copy2(self.installerCreationDistPath + os.sep + "Web2Board.pkg", self.installerPath)

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.installerCreationDistPath)
            log.info("Creating Installer")

            call(["/usr/local/bin/packagesbuild", self.pkgprojPath])
            self._moveInstallerToInstallerFolder()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearBuildFiles()
            # self._deleteInstallerCreationFolder()
