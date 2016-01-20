import logging
import os
import shutil
import zipfile

import click

from libs import utils
from libs.PathsManager import PathsManager as pm
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater, Web2BoardUpdater
from libs.utils import findFiles
from platformio import util
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
        self.iconPath = pm.RES_ICO_PATH
        self.srcResPath = os.path.join(self.srcPath, "res")
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
        self.installerCreationExecutablesPath = None
        self.installerCreationDistPath = None
        self.installerCreationName = None
        self.pkgPlatformPath = None
        self.resPlatformPath = None

        self.web2boardExecutableName = None
        self.sconsExecutableName = None

    # todo move this to attribute
    def _getInstallerCreationResPath(self):
        return os.path.join(self.installerCreationExecutablesPath, 'res')

    # todo move this to attribute
    def _getPlatformIOPackagesPath(self):
        return os.path.join(self._getInstallerCreationResPath(), pm.PLATFORMIO_PACKAGES_ZIP_NAME)

    def _prepareResFolderForExecutable(self):
        if os.path.exists(self.srcResPath):
            shutil.rmtree(self.srcResPath)
        os.makedirs(self.srcResPath)

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
        self._clearBuildFiles()
        self._deleteInstallerCreationFolder()

    def _clearBuildFiles(self):
        if os.path.exists(self.pyInstallerDistFolder):
            shutil.rmtree(self.pyInstallerDistFolder)
        if os.path.exists(self.pyInstallerBuildFolder):
            shutil.rmtree(self.pyInstallerBuildFolder)

    def _addMetadataForInstaller(self):
        pass

    def _makeMainDirs(self):
        os.makedirs(self.installerCreationPath)
        os.makedirs(self.installerCreationDistPath)
        os.makedirs(self.installerCreationExecutablesPath)
        os.makedirs(self.installerPath)

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            self._constructSconsExecutable()
            self._getSconsPackages()
            self._constructWeb2boardExecutable()
            self._compressExecutables()
            self._constructLinkExecutable()
        finally:
            os.chdir(currentPath)
            shutil.rmtree(self.installerCreationExecutablesPath)

    def _constructLinkExecutable(self):
        os.chdir(self.srcPath)
        log.debug("Creating Web2boardLink Executable")
        os.system("pyinstaller -w \"{}\"".format("web2boardLink.py"))
        utils.copytree(os.path.join(self.pyInstallerDistFolder, "web2boardLink"), self.installerCreationDistPath)

    def _constructWeb2boardExecutable(self):
        log.debug("Creating Web2board Executable")
        os.system("pyinstaller  -w \"{}\"".format(self.web2boardSpecPath))
        utils.copytree(os.path.join(self.pyInstallerDistFolder, "web2board"), self.installerCreationExecutablesPath)

    def _constructSconsExecutable(self):
        log.debug("Creating Scons Executable")
        os.system("pyinstaller \"{}\"".format(self.sconsSpecPath))

        installerSconsPath = os.path.join(self._getInstallerCreationResPath(), "Scons")
        utils.copytree(os.path.join(self.pyInstallerDistFolder, "sconsScript"), installerSconsPath)

        shutil.copytree(os.path.join(self.srcPath, "platformio"), os.path.join(installerSconsPath, "plarformio"))
        shutil.copytree(self.srcResPath, os.path.join(installerSconsPath, "res"))

    def _compressExecutables(self):
        packagesFiles = findFiles(self.installerCreationExecutablesPath, ["*", "**/*"])
        packagesFiles = [x[len(self.installerCreationExecutablesPath) + 1:] for x in packagesFiles]
        with zipfile.ZipFile(self.installerCreationDistPath + os.sep + "web2board.zip", "w",
                             zipfile.ZIP_DEFLATED) as z:
            os.chdir(self.installerCreationExecutablesPath)
            with click.progressbar(packagesFiles, label='Compressing...') as packagesFilesInProgressBar:
                for zipFilePath in packagesFilesInProgressBar:
                    z.write(zipFilePath)

    def _getSconsPackages(self):
        log.debug("Gettings Scons Packages")
        originalCurrentDirectory = os.getcwd()
        originalClickConfirm = click.confirm

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm
        try:
            os.chdir(pm.PLATFORMIO_WORKSPACE_PATH)
            config = util.get_project_config()
            for section in config.sections():
                envOptionsDict = {x[0]: x[1] for x in config.items(section)}
                platform = PlatformFactory.newPlatform(envOptionsDict["platform"])
                log.info("getting packages for: {}".format(envOptionsDict))
                platform.configure_default_packages(envOptionsDict, ["upload"])
                platform._install_default_packages()
            os.chdir(originalCurrentDirectory)

            log.info("all packages where successfully installed")
            platformIOPackagesPath = os.path.abspath(util.get_home_dir())
            log.info("constructing zip file in : {}".format(self._getPlatformIOPackagesPath()))
            packagesFiles = findFiles(platformIOPackagesPath, ["appstate.json", "packages/**/*"])

            def isDoc(filePath):
                isDoc = os.sep + "doc" + os.sep not in filePath
                isDoc = isDoc and os.sep + "examples" + os.sep not in filePath
                isDoc = isDoc and os.sep + "tool-scons" + os.sep not in filePath
                return isDoc and os.sep + "README" not in filePath.upper()

            packagesFiles = [x[len(platformIOPackagesPath) + 1:] for x in packagesFiles if isDoc(x)]

            if not os.path.exists(os.path.dirname(self._getPlatformIOPackagesPath())):
                os.makedirs(os.path.dirname(self._getPlatformIOPackagesPath()))

            with zipfile.ZipFile(self._getPlatformIOPackagesPath(), "w", zipfile.ZIP_DEFLATED) as z:
                os.chdir(platformIOPackagesPath)
                with click.progressbar(packagesFiles, label='Compressing...') as packagesFilesInProgressBar:
                    for zipFilePath in packagesFilesInProgressBar:
                        z.write(zipFilePath)

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
