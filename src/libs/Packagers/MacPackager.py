from subprocess import call

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
        self.pkgPlatformPath = os.path.join(self.pkgPath, "darwin")
        self.resPlatformPath = os.path.join(self.resPath, "darwin")

        self.web2boardExecutableName = "web2board.exe"
        self.serialMonitorExecutableName = "SerialMonitor.exe"

        self.web2boardSpecPath = os.path.join(self.srcResPath, "web2board-mac.spec")
        self.serialMonitorSpecPath = os.path.join(self.srcResPath, "serialMonitor-mac.spec")

        self.pkgprojPath = os.path.join(self.installerCreationPath, "create-mpkg", "web2board", "web2board.pkgproj")

    def _addMetadataForInstaller(self):
        copytree(self.pkgPlatformPath, self.installerCreationPath)

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.installerCreationDistPath)
            log.info("Creating Installer")

            #call(["/usr/local/bin/packagesbuild", self.pkgprojPath])
            #self._moveInstallerToInstallerFolder()
            #log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._restoreSrcResFolder()
            self._clearBuildFiles()
            # self._deleteInstallerCreationFolder()
