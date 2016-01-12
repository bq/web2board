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
        self.sconsExecutableName = "sconsScript.exe"

    def _addBatScripsToWinDist(self):
        batName = "afterInstall.bat"
        shutil.copy2(self.installerCreationPath + os.sep + batName, self.installerCreationDistPath + os.sep + batName)
        web2boardRegName = "web2board.reg"
        shutil.copy2(self.srcResPath + os.sep + "web2board.reg", self.installerCreationDistPath + os.sep + web2boardRegName)
        web2boardRegName = "web2boardTo32.reg"
        shutil.copy2(self.srcResPath + os.sep + "web2boardTo32.reg", self.installerCreationDistPath + os.sep + web2boardRegName)

    def _addMetadataForInstaller(self):
        Packager._addMetadataForInstaller(self)
        copytree(self.pkgPlatformPath, self.installerCreationPath)
        shutil.copy2(self.iconPath, self.installerCreationPath + os.sep + os.path.basename(self.iconPath))
        self._addBatScripsToWinDist()

    def _moveInstallerToInstallerFolder(self):
        shutil.copy2(self.installerCreationPath + os.sep + "Web2board.exe", self.installerPath)

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.installerCreationPath)
            log.info("Creating Installer")
            call(["makensis", "installer.nsi"])
            self._moveInstallerToInstallerFolder()
            log.info("installer created successfully")
        except Exception as e:
            print str(e)
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._restoreSrcResFolder()
            self._clearBuildFiles()
            #self._deleteInstallerCreationFolder()
