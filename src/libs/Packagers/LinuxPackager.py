from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *


class LinuxPackager(Packager):
    ARCH_64, ARCH_32 = "amd64", "i386"

    RELEASE_TYPES = ({"path": "web2board", "desktopName": "Web2Board-PROD"},
                     {"path": "dev/bet", "desktopName": "Web2Board-BETA"},
                     {"path": "dev/qa", "desktopName": "Web2Board-QA"},
                     {"path": "dev/staging", "desktopName": "Web2Board-STAGING"})

    def __init__(self, architecture=ARCH_64):
        Packager.__init__(self)
        self.architecture = architecture
        self.installerPath = self.installerFolder + os.sep + "debian_{}".format(architecture)

        self.installerCreationPath = self.web2boardPath + os.sep + "deb_web2board_{}_{}".format(architecture, self.version)
        self.installerCreationName = os.path.basename(self.installerCreationPath)
        self.installerCreationDistPath = os.path.join(self.installerCreationPath, "usr", "lib", "python2.7", "dist-packages", "Scripts",
                                           "web2board")

        self.pkgPlatformPath = os.path.join(self.pkgPath, "linux")
        self.resPlatformPath = os.path.join(self.resPath, "linux")
        self.web2boardExecutableName = "web2board"
        self.serialMonitorExecutableName = "SerialMonitor"

        self.packageDebianMetadataPath = os.path.join(self.installerCreationPath, "DEBIAN")
        self.debDistPath = os.path.join(self.installerPath, "deb_dist")
        self.debianMetadataPath = os.path.join(self.pkgPlatformPath, "debian")
        with open(self.packagerResPath + os.sep + "Web2Board-template.desktop") as desktopFile:
            self.Web2BoardDesktopTemplate = desktopFile.read()

    def _makeMainDirs(self):
        Packager._makeMainDirs(self)
        os.makedirs(self.debDistPath)

    def _addMetadataForInstaller(self):
        copytree(self.debianMetadataPath, self.packageDebianMetadataPath)
        with open(self.packageDebianMetadataPath + os.sep + "control", "r") as controlFile:
            controlText = controlFile.read()
        with open(self.packageDebianMetadataPath + os.sep + "control", "w") as controlFile:
            controlFile.write(controlText.format(version=self.version, architecture=self.architecture))

        os.chmod(self.debianMetadataPath + os.sep + "postinst", int("775", 8))
        os.chmod(self.debianMetadataPath + os.sep + "postrm", int("775", 8))

    def _createDesktops(self):
        tarTypePathTemplate = self.debDistPath + os.sep + "{desktopName}.tar.gz"
        desktopPath = self.debDistPath + os.sep + "Web2board.desktop"
        currentDirectory = os.getcwd()
        try:
            os.chdir(self.debDistPath)
            for releaseType in self.RELEASE_TYPES:
                tarPath = tarTypePathTemplate.format(**releaseType)
                with open(desktopPath, "w") as desktopFile:
                    desktopFile.write(self.Web2BoardDesktopTemplate.format(**releaseType))
                call(["tar", "-czpf", tarPath, os.path.basename(desktopPath)])

            os.remove(desktopPath)
        finally:
            os.chdir(currentDirectory)

    def _moveDebToInstallerPath(self):
        resultingDeb = self.installerCreationPath + os.sep + self.installerCreationName + ".deb"
        shutil.copy2(resultingDeb, self.installerPath)

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            self._createDesktops()
            os.chdir(self.installerCreationPath)
            log.info("Creating Installer")
            call(["dpkg-deb", "--build", self.installerCreationPath])
            self._moveDebToInstallerPath()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._restoreSrcResFolder()
            self._clearBuildFiles()
            self._deleteInstallerCreationFolder()
