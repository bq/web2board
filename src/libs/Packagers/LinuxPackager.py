from subprocess import call

from libs.Packagers.Packager import Packager
from libs.utils import *


class LinuxPackager(Packager):
    versionPath = None
    folderName = None
    executablePath = None
    executableResPath = None
    packageDebianPath = None
    debDistPath = None
    Web2BoardDesktopTemplate = None

    RELEASE_TYPES = ({"path": "web2board", "desktopName": "Web2Board-PROD"},
                     {"path": "dev/bet", "desktopName": "Web2Board-BETA"},
                     {"path": "dev/qa", "desktopName": "Web2Board-QA"},
                     {"path": "dev/staging", "desktopName": "Web2Board-STAGING"})

    def __init__(self):
        Packager.__init__(self)

    def _initPaths(self):
        Packager._initPaths(self)
        if self.versionPath is None:
            self.versionPath = self.srcPath + os.sep + "web2board_{}".format(self.version)
            self.folderVersionName = os.path.basename(self.versionPath)
            self.executablePath = os.path.join(self.versionPath, "usr", "lib", "python2.7", "dist-packages", "Scripts",
                                               "web2board")
            self.executableResPath = os.path.join(self.executablePath, "res")
            self.packageDebianPath = os.path.join(self.versionPath, "DEBIAN")
            self.debDistPath = os.path.join(self.srcPath, "deb_dist")
            with open(self.packagerResPath + os.sep + "Web2Board-template.desktop") as desktopFile:
                self.Web2BoardDesktopTemplate = desktopFile.read()

    def _clearMainFolders(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)
        if os.path.exists(self.debDistPath):
            shutil.rmtree(self.debDistPath)

    def _makeMainDirs(self):
        os.makedirs(self.versionPath)
        os.makedirs(self.executablePath)
        os.mkdir(self.debDistPath)

    def _addResFilesForExecutable(self):
        copytree(os.path.join(self.resPath, "common"), self.executableResPath)
        copytree(os.path.join(self.resPath, "linux"), self.executableResPath)

    def _constructAndMoveExecutable(self):
        call(["pyinstaller", "--onefile", "web2board.py"])
        shutil.copy2(os.path.join(self.srcPath, "dist", "web2board"), self.executablePath)

    def _clearBuildFiles(self):
        if os.path.exists(self.srcPath + os.sep + "dist"):
            shutil.rmtree(self.srcPath + os.sep + "dist")
        if os.path.exists(self.srcPath + os.sep + "build"):
            shutil.rmtree(self.srcPath + os.sep + "build")

    def _addMetadataForExecutable(self):
        os.mkdir(self.packageDebianPath)
        copytree(os.path.join(self.pkgPath, "linux", "debian"), self.packageDebianPath)

    def _deleteVersionFolder(self):
        if os.path.exists(self.versionPath):
            shutil.rmtree(self.versionPath)

    def _createDesktops(self):
        for type in self.RELEASE_TYPES:
            filePath = self.debDistPath + os.sep + type["desktopName"] + ".desktop"
            with open(filePath, "w") as desktopFile:
                desktopFile.write(self.Web2BoardDesktopTemplate.format(**type))

    def _moveDebToDebDistPath(self):
        shutil.copy(self.srcPath + os.sep + "web2board", self.debDistPath + os.sep + "web2board")

    def createPackage(self):
        try:
            self._clearMainFolders()
            self._makeMainDirs()
            self._addResFilesForExecutable()
            self._createDesktops()
            self._constructAndMoveExecutable()
            self._addMetadataForExecutable()
            call(["dpkg-deb", "--build", self.versionPath])
            self._moveDebToDebDistPath()
        finally:
            self._clearBuildFiles()
            self._deleteVersionFolder()
