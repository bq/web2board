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
        self.architecture = architecture
        Packager.__init__(self)
        self.versionPath = self.web2boardPath + os.sep + "deb_web2board_{}".format(self.version)
        self.folderVersionName = os.path.basename(self.versionPath)
        self.executablePath = os.path.join(self.versionPath, "usr", "lib", "python2.7", "dist-packages", "Scripts",
                                           "web2board")
        self.executableResPath = os.path.join(self.executablePath, "res")
        self.packageDebianMetadataPath = os.path.join(self.versionPath, "DEBIAN")
        self.debDistPath = os.path.join(self.web2boardPath, "deb_dist")
        self.installerPath = self.installerFolder + os.sep + "debian"
        self.debianMetadataPath = os.path.join(self.pkgPath, "linux", "debian")
        with open(self.packagerResPath + os.sep + "Web2Board-template.desktop") as desktopFile:
            self.Web2BoardDesktopTemplate = desktopFile.read()

    def _clearMainFolders(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)
        if os.path.exists(self.debDistPath):
            shutil.rmtree(self.debDistPath)
        if os.path.exists(self.installerPath):
            shutil.rmtree(self.installerPath)
        self._clearBuildFiles()

    def _makeMainDirs(self):
        os.makedirs(self.versionPath)
        os.makedirs(self.executablePath)
        os.makedirs(self.installerPath)
        os.mkdir(self.debDistPath)

    def _addResFilesForExecutable(self):
        copytree(os.path.join(self.resPath, "common"), self.executableResPath)
        copytree(os.path.join(self.resPath, "linux"), self.executableResPath)

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            call(["pyinstaller", "--onefile", "web2board.py"])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, "web2board"), self.executablePath)
        finally:
            os.chdir(currentPath)

    def _addMetadataForInstaller(self):
        copytree(self.debianMetadataPath, self.packageDebianMetadataPath)
        with open(self.packageDebianMetadataPath + os.sep + "control", "r") as controlFile:
            controlText = controlFile.read()
        with open(self.packageDebianMetadataPath + os.sep + "control", "w") as controlFile:
            controlFile.write(controlText.format(version=self.version, architecture=self.architecture))

        os.chmod(self.debianMetadataPath + os.sep + "postinst", int("775", 8))
        os.chmod(self.debianMetadataPath + os.sep + "postrm", int("775", 8))

    def _deleteVersionFolder(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)

    def _createDesktops(self):
        tarTypePathTemplate = self.debDistPath + os.sep + "{desktopName}.tar.gz"
        desktopPath = self.debDistPath + os.sep + "Web2board.desktop"
        currentDirectory = os.getcwd()
        try:
            os.chdir(self.debDistPath)
            for type in self.RELEASE_TYPES:
                tarPath = tarTypePathTemplate.format(**type)
                with open(desktopPath, "w") as desktopFile:
                    desktopFile.write(self.Web2BoardDesktopTemplate.format(**type))
                call(["tar", "-czpf", tarPath, os.path.basename(desktopPath)])

            os.remove(desktopPath)
        finally:
            os.chdir(currentDirectory)

    def _moveDebToInstallerPath(self):
        resultingDeb = self.srcPath + os.sep + self.folderVersionName + ".deb"
        shutil.copy(resultingDeb, self.installerPath + os.sep + "web2board.deb")

    def createPackage(self):
        try:
            log.debug("Removing main folders")
            self._clearMainFolders()
            log.debug("Creating main folders")
            self._makeMainDirs()
            log.debug("Adding resources for executable")
            self._addResFilesForExecutable()
            # self._createDesktops()
            log.info("Constructing executable")
            self._constructAndMoveExecutable()
            log.debug("Adding metadata for installer")
            self._addMetadataForInstaller()
            os.chdir(self.versionPath)
            log.info("Creating Installer")
            call(["dpkg-deb", "--build", self.versionPath])
            self._moveDebToInstallerPath()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2boardPath)
            self._clearMainFolders()
            self._deleteVersionFolder()
