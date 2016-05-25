from os.path import join
from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *


class LinuxPackager(Packager):
    RELEASE_TYPES = ({"path": "web2board", "desktopName": "Web2Board-PROD"},
                     {"path": "dev/bet", "desktopName": "Web2Board-BETA"},
                     {"path": "dev/qa", "desktopName": "Web2Board-QA"},
                     {"path": "dev/staging", "desktopName": "Web2Board-STAGING"})

    def __init__(self, architecture=Packager.ARCH_64):
        Packager.__init__(self)
        self.architecture = architecture
        self.installerPath = self.installerFolder + os.sep + "debian_{}".format(architecture)
        self.installerOfflinePath = self.installerFolder + os.sep + "debian_{}Offline".format(architecture)

        self.installerCreationPath = join(self.web2boardPath, "deb_web2board_{}_{}".format(architecture, self.version))
        self.installerCreationName = os.path.basename(self.installerCreationPath)
        self.installerCreationExecutablesPath = join(self.installerCreationPath, "executables")
        self.installerCreationDistPath = join(self.installerCreationPath, "opt", "web2board")

        self.pkgPlatformPath = join(self.pkgPath, "linux")
        self.resPlatformPath = join(self.resPath, "linux")
        self.web2boardExecutableName = "web2board"
        self.web2boardSpecPath = join(self.web2boardPath, "web2board-linux.spec")

        self.packageDebianMetadataPath = join(self.installerCreationPath, "DEBIAN")
        self.debianMetadataPath = join(self.pkgPlatformPath, "debian")
        with open(self.packagerResPath + os.sep + "Web2Board-template.desktop") as desktopFile:
            self.Web2BoardDesktopTemplate = desktopFile.read()

    def _makeMainDirs(self):
        Packager._makeMainDirs(self)

    def _addMetadataForInstaller(self):
        Packager._addMetadataForInstaller(self)
        copytree(self.debianMetadataPath, self.packageDebianMetadataPath)
        with open(self.packageDebianMetadataPath + os.sep + "control", "r") as controlFile:
            controlText = controlFile.read()
        with open(self.packageDebianMetadataPath + os.sep + "control", "w") as controlFile:
            controlFile.write(controlText.format(version=self.version, architecture=self.architecture))

        os.chmod(self.debianMetadataPath + os.sep + "control", int("655", 8))

    def _moveDebToInstallerPath(self):
        resulting_deb = self.web2boardPath + os.sep + self.installerCreationName + ".deb"
        shutil.move(resulting_deb, self.installerPath + os.sep + "web2board.deb")


    def _create_linux_installer(self):
        installer_files = ["web2board_installer.py", "web2board_installer.spec"]
        for installer_file in installer_files:
            shutil.copy(self.pkgPlatformPath + os.sep + installer_file, self.installerPath + os.sep + installer_file)
        currentPath = os.getcwd()
        os.chdir(self.installerPath)
        try:
            log.info("Creating web2board_installer Executable")
            os.system("pyinstaller \"{}\"".format("web2board_installer.spec"))
            shutil.copy(join("dist", "web2board_installer"), "web2board_installer")
            for installer_file in installer_files:
                os.remove(installer_file)
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            os.system("chmod 0777 web2board_installer")
        finally:
            os.chdir(currentPath)

    def createPackage(self):
        try:
            self._createMainStructureAndExecutables()
            log.info("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.installerCreationPath)
            log.info("Creating deb")
            os.system("chmod -R 777 " + self.installerCreationDistPath)
            call(["dpkg-deb", "--build", self.installerCreationPath])
            self._moveDebToInstallerPath()
            log.info("Creating Linux installer")
            self._create_linux_installer()
            log.info("installer created successfully")
        finally:
            log.info("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearBuildFiles()
            # self._deleteInstallerCreationFolder()
