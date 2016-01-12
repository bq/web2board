import os
import shutil
import zipfile
from subprocess import call
import logging
import click

from libs.utils import findFiles, copytree
from platformio import util

from libs import utils
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater, Web2BoardUpdater
from libs.PathsManager import PathsManager as pm
from platformio.platforms.base import PlatformFactory

pDir = os.path.pardir
log = logging.getLogger(__name__)


class Packager:
    ARCH_64, ARCH_32 = "amd64", "i386"

    def __init__(self):
        modulePath = utils.getModulePath()
        self.packagerResPath = os.path.join(modulePath, "res")
        self.web2boardPath = os.path.abspath(os.path.join(modulePath, pDir, pDir, pDir))
        self.srcPath = os.path.join(self.web2boardPath, "src")
        self.resPath = os.path.join(self.web2boardPath, "res")
        self.resCommonPath = os.path.join(self.resPath, "common")
        self.iconPath = os.path.join(self.resPath, "common", "Web2board.ico")
        self.srcResPath = os.path.join(self.srcPath, "res")
        self.auxiliarySrcResPath = os.path.join(self.srcPath, "auxiliaryRes")
        self.pkgPath = os.path.join(self.web2boardPath, "pkg")
        self.pyInstallerDistFolder = self.srcPath + os.sep + "dist"
        self.pyInstallerBuildFolder = self.srcPath + os.sep + "build"
        self.installerFolder = os.path.join(self.web2boardPath, "installers")

        self.version = getWeb2boardUpdater().currentVersionInfo.version

        self.web2boardSpecPath = os.path.join(self.web2boardPath, "web2board.spec")
        self.sconsSpecPath = os.path.join(self.web2boardPath, "scons.spec")

        # abstract attributes
        self.installerPath = None
        self.installerCreationPath = None
        self.installerCreationDistPath = None
        self.installerCreationName = None
        self.pkgPlatformPath = None
        self.resPlatformPath = None

        self.web2boardExecutableName = None
        self.sconsExecutableName = None

        os.chdir(self.web2boardPath)

    def _getInstallerExternalResourcesPath(self):
        return self.installerCreationDistPath + pm.EXTERNAL_RESOURCES_PATH[len(pm.MAIN_PATH):]

    def _getPlatformIOPackagesPath(self):
        return os.path.join(self._getInstallerExternalResourcesPath(), "platformIoPackages.zip")

    def _prepareResFolderForExecutable(self):
        if os.path.exists(self.srcResPath):
            shutil.move(self.srcResPath, self.auxiliarySrcResPath)
        utils.copytree(self.resCommonPath, self.srcResPath)
        utils.copytree(self.resPlatformPath, self.srcResPath)

    def _deleteInstallerCreationFolder(self):
        if os.path.exists(self.installerCreationPath):
            shutil.rmtree(self.installerCreationPath)

    def _clearMainFolders(self):
        if os.path.exists(os.path.join(self.srcPath, self.sconsExecutableName)):
            os.remove(os.path.join(self.srcPath, self.sconsExecutableName))
        if os.path.exists(self.installerPath):
            shutil.rmtree(self.installerPath)
        if os.path.exists(self.auxiliarySrcResPath):
            shutil.rmtree(self.auxiliarySrcResPath)
        self._clearBuildFiles()
        self._deleteInstallerCreationFolder()

    def _clearBuildFiles(self):
        if os.path.exists(self.pyInstallerDistFolder):
            shutil.rmtree(self.pyInstallerDistFolder)
        if os.path.exists(self.pyInstallerBuildFolder):
            shutil.rmtree(self.pyInstallerBuildFolder)

    def _addMetadataForInstaller(self):
        resourcesInstallerPath = self._getInstallerExternalResourcesPath()
        if not os.path.exists(resourcesInstallerPath):
            os.makedirs(resourcesInstallerPath)

        copytree(pm.EXTERNAL_RESOURCES_PATH, resourcesInstallerPath)

    def _makeMainDirs(self):
        os.makedirs(self.installerCreationPath)
        os.makedirs(self.installerCreationDistPath)
        os.makedirs(self.installerPath)
        os.makedirs(self._getInstallerExternalResourcesPath())

    def _restoreSrcResFolder(self):
        shutil.rmtree(self.srcResPath)
        if os.path.exists(self.auxiliarySrcResPath):
            shutil.move(self.auxiliarySrcResPath, self.srcResPath)

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            log.debug("Creating Scons Executable")
            call(["pyinstaller", "--onefile", self.sconsSpecPath])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.sconsExecutableName),
                         self._getInstallerExternalResourcesPath())

            self._getSconsPackages()
            call(["pyinstaller", "--onefile", '-w', self.web2boardSpecPath])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.web2boardExecutableName),
                         self.installerCreationDistPath)

        finally:
            os.chdir(currentPath)

    def _getSconsPackages(self):
        originalCurrentDirectory = os.getcwd()
        originalClickConfirm = click.confirm

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm
        try:
            os.chdir(pm.SETTINGS_PLATFORMIO_PATH)
            config = util.get_project_config()
            for section in config.sections():
                envOptionsDict = {x[0]: x[1] for x in config.items(section)}
                platform = PlatformFactory.newPlatform(envOptionsDict["platform"])
                log.info("getting packages for: {}".format(envOptionsDict))
                platform.configure_default_packages(envOptionsDict, ["upload"])
                platform._install_default_packages()

            log.info("all packages where successfully installed")
            platformIOPackagesPath = os.path.abspath(util.get_home_dir())
            log.info("constructing zip file in : {}".format(self._getPlatformIOPackagesPath()))
            packagesFiles = findFiles(platformIOPackagesPath, ["appstate.json", "packages/**/*"])
            isDoc = lambda filePath: "doc" not in filePath and not filePath.endswith('.html')
            packagesFiles = [x[len(platformIOPackagesPath) + 1:] for x in packagesFiles if isDoc(x)]
            os.chdir(platformIOPackagesPath)
            if not os.path.exists(self._getInstallerExternalResourcesPath()):
                os.makedirs(self._getInstallerExternalResourcesPath())

            with zipfile.ZipFile(self._getPlatformIOPackagesPath(), "w", zipfile.ZIP_DEFLATED) as z:
                for zipFilePath in packagesFiles:
                    log.debug("adding file: {}".format(zipFilePath))
                    z.write(zipFilePath)
            log.info("zip file constructed")

        finally:
            os.chdir(originalCurrentDirectory)
            click.confirm = originalClickConfirm

    def _createMainStructureAndExecutables(self):
        if self.version == Web2BoardUpdater.NONE_VERSION:
            self._prepareResFolderForExecutable()
            self.__init__()
            return self._createMainStructureAndExecutables()

        log.debug("Removing main folders")
        self._clearMainFolders()
        log.debug("Creating main folders")
        self._makeMainDirs()
        log.debug("Adding resources for executable")
        self._prepareResFolderForExecutable()
        log.info("Constructing executable")
        self._constructAndMoveExecutable()

    def createPackage(self):
        raise NotImplementedError

    @staticmethod
    def constructCurrentPlatformPackager(architecture=ARCH_64):
        """
        :param architecture: use this architecture to for linux packager
        :rtype: Packager
        """
        if utils.isMac():
            from MacPackager import MacPackager
            return MacPackager()
        elif utils.isLinux():
            from LinuxPackager import LinuxPackager
            return LinuxPackager(architecture=architecture)
        elif utils.isWindows():
            from WindowsPackager import WindowsPackager
            return WindowsPackager()
