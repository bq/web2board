from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *
from os.path import join


class LinuxPackager(Packager):
    RELEASE_TYPES = ({"path": "web2board", "desktopName": "Web2Board-PROD"},
                     {"path": "dev/bet", "desktopName": "Web2Board-BETA"},
                     {"path": "dev/qa", "desktopName": "Web2Board-QA"},
                     {"path": "dev/staging", "desktopName": "Web2Board-STAGING"})

    def __init__(self, architecture=Packager.ARCH_64):
        Packager.__init__(self)
        self.architecture = architecture
        self.installerPath = self.installerFolder + os.sep + "debian_{}".format(architecture)

        self.installerCreationPath = join(self.web2boardPath, "deb_web2board_{}_{}".format(architecture, self.version))
        self.installerCreationName = os.path.basename(self.installerCreationPath)
        self.installerCreationExecutablesPath = join(self.installerCreationPath, "executables")
        self.installerCreationDistPath = join(self.installerCreationPath, "web2board")

        self.pkgPlatformPath = join(self.pkgPath, "linux")
        self.resPlatformPath = join(self.resPath, "linux")
        self.web2boardExecutableName = "web2board"
        self.web2boardSpecPath = join(self.web2boardPath, "web2board-linux.spec")
        self.sconsExecutableName = "sconsScript"
        self.sconsSpecPath = join(self.web2boardPath, "scons-linux.spec")
        self.installerSpecPath = join(self.web2boardPath, "linuxInstaller.spec")

        self.packageDebianMetadataPath = join(self.installerCreationPath, "DEBIAN")
        self.debDistPath = join(self.installerPath, "deb_dist")
        self.debianMetadataPath = join(self.pkgPlatformPath, "debian")
        with open(self.packagerResPath + os.sep + "Web2Board-template.desktop") as desktopFile:
            self.Web2BoardDesktopTemplate = desktopFile.read()

    def _makeMainDirs(self):
        Packager._makeMainDirs(self)
        os.makedirs(self.debDistPath)

    def _addMetadataForInstaller(self):
        os.system("pyinstaller \"{0}\" -F --distpath {1}".format(self.installerSpecPath, self.installerCreationPath))

    def _clearBuildFiles(self):
        Packager._clearBuildFiles(self)
        if os.path.exists(self.srcPath + os.sep + "web2board.zip"):
            os.remove(self.srcPath + os.sep + "web2board.zip")

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.debug("Adding metadata for installer")
            log.info("Creating Installer")
            shutil.make_archive(self.installerCreationDistPath, "zip", self.installerCreationPath)
            shutil.rmtree(self.installerCreationDistPath)
            shutil.copy(self.installerCreationDistPath + ".zip", self.srcPath + os.sep + "web2board.zip")
            self._addMetadataForInstaller()

        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearBuildFiles()
            # self._deleteInstallerCreationFolder()
