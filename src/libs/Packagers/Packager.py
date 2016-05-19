import logging
import os
import shutil
import zipfile

import click

from libs import utils
from libs.PathsManager import PathsManager as pm
from libs.Updaters.Updater import Updater
from libs.Version import Version
from libs.utils import find_files
from platformio import util
from platformio.platforms.base import PlatformFactory

pardir = os.path.pardir
log = logging.getLogger(__name__)


class Packager:
    ARCH_64, ARCH_32 = "amd64", "i386"

    def __init__(self):
        modulePath = utils.get_module_path()
        self.packagerResPath = os.path.join(modulePath, "res")
        self.web2boardPath = os.path.abspath(os.path.join(modulePath, pardir, pardir, pardir))
        self.srcPath = os.path.join(self.web2boardPath, "src")
        self.resPath = os.path.join(self.web2boardPath, "res")
        self.resCommonPath = os.path.join(self.resPath, "common")
        self.iconPath = pm.RES_ICO_PATH
        self.srcResPath = os.path.join(self.srcPath, "res")
        self.pkgPath = os.path.join(self.web2boardPath, "pkg")
        self.pyInstallerDistFolder = self.srcPath + os.sep + "dist"
        self.pyInstallerBuildFolder = self.srcPath + os.sep + "build"
        self.installerFolder = os.path.join(self.web2boardPath, "installers")
        Version.read_version_values()
        self.version = Version.web2board

        self.web2boardSpecPath = os.path.join(self.web2boardPath, "web2board.spec")

        # abstract attributes
        self.installerPath = None
        self.installerOfflinePath = None
        self.installerCreationPath = None
        self.installerCreationExecutablesPath = None
        self.installerCreationDistPath = None
        self.installerCreationName = None
        self.pkgPlatformPath = None
        self.resPlatformPath = None

        self.web2boardExecutableName = None

    # todo move this to attribute
    def _getInstallerCreationResPath(self):
        return os.path.join(self.installerCreationExecutablesPath, 'res')

    # todo move this to attribute
    def _getPlatformIOPackagesPath(self):
        return os.path.join(self._getInstallerCreationResPath(), pm.PLATFORMIO_PACKAGES_NAME)

    def prepareResFolderForExecutable(self):
        if not os.path.exists(self.srcResPath):
            os.makedirs(self.srcResPath)

        utils.copytree(self.resCommonPath, self.srcResPath, force_copy=True)
        utils.copytree(self.resPlatformPath, self.srcResPath, force_copy=True)

    def _deleteInstallerCreationFolder(self):
        if os.path.exists(self.installerCreationPath):
            shutil.rmtree(self.installerCreationPath)

    def _clearMainFolders(self):
        if os.path.exists(self.installerPath):
            shutil.rmtree(self.installerPath)
        if os.path.exists(self.installerOfflinePath):
            shutil.rmtree(self.installerOfflinePath)
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
            self._getPlatformioPackages()
            self._constructWeb2boardExecutable()
            shutil.move(self.installerCreationExecutablesPath, self.installerCreationDistPath + os.sep + "web2board")
            self._constructLinkExecutable()
        finally:
            os.chdir(currentPath)

    def _constructLinkExecutable(self):
        os.chdir(self.srcPath)
        log.debug("Creating Web2boardLink Executable")
        os.system("pyinstaller -w \"{}\"".format("web2boardLink.py"))
        utils.copytree(os.path.join(self.pyInstallerDistFolder, "web2boardLink"), self.installerCreationDistPath)

    def _constructWeb2boardExecutable(self):
        log.debug("Creating Web2board Executable")
        os.system("pyinstaller \"{}\"".format(self.web2boardSpecPath))
        utils.copytree(os.path.join(self.pyInstallerDistFolder, "web2board"), self.installerCreationExecutablesPath)

    def _compressExecutables(self):
        packagesFiles = find_files(self.installerCreationExecutablesPath, ["*", "**/*"])
        packagesFiles = [x[len(self.installerCreationExecutablesPath) + 1:] for x in packagesFiles]
        with zipfile.ZipFile(self.installerCreationDistPath + os.sep + "web2board.zip", "w",
                             zipfile.ZIP_DEFLATED) as z:
            os.chdir(self.installerCreationExecutablesPath)
            with click.progressbar(packagesFiles, label='Compressing...') as packagesFilesInProgressBar:
                for zipFilePath in packagesFilesInProgressBar:
                    z.write(zipFilePath)

    def _getPlatformioPackages(self):
        log.debug("Gettings Scons Packages")
        originalCurrentDirectory = os.getcwd()
        originalClickConfirm = click.confirm

        def clickConfirm(message):
            print message
            return True

        click.confirm = clickConfirm
        try:
            os.chdir(pm.PLATFORMIO_WORKSPACE_SKELETON)
            config = util.get_project_config()
            for section in config.sections():
                envOptionsDict = {x[0]: x[1] for x in config.items(section)}
                platform = PlatformFactory.newPlatform(envOptionsDict["platform"])
                log.info("getting packages for: {}".format(envOptionsDict))
                platform.configure_default_packages(envOptionsDict, ["upload"])
                platform._install_default_packages()
            os.chdir(originalCurrentDirectory)

            log.info("all platformio packages are successfully installed")

            platformIOPackagesPath = os.path.abspath(util.get_home_dir())
            def isDoc(filePath):
                isDoc = os.sep + "doc" + os.sep not in filePath
                isDoc = isDoc and os.sep + "examples" + os.sep not in filePath
                isDoc = isDoc and os.sep + "tool-scons" + os.sep not in filePath
                isDoc = isDoc and os.sep + "README" not in filePath.upper()
                return not isDoc

            # installerPlatformioPackagesPath = self._getPlatformIOPackagesPath()
            # if os.path.exists(installerPlatformioPackagesPath):
            #     shutil.rmtree(installerPlatformioPackagesPath)
            #
            # os.makedirs(installerPlatformioPackagesPath)
            log.info("Cleaning platformio packages files")
            allFiles = sorted(utils.find_files(platformIOPackagesPath, ["*", "**" + os.sep + "*"]), reverse=True)
            for i, f in enumerate(allFiles):
                if isDoc(f):
                    if os.path.isfile(f):
                        os.remove(f)
                    else:
                        try:
                            os.rmdir(f)
                        except:
                            shutil.rmtree(f)
        finally:
            os.chdir(originalCurrentDirectory)
            click.confirm = originalClickConfirm

    def _createMainStructureAndExecutables(self):
        if self.version == Updater.NONE_VERSION:
            self.prepareResFolderForExecutable()
            self.__init__()
            return self._createMainStructureAndExecutables()

        log.debug("Removing main folders")
        self._clearMainFolders()
        log.debug("Creating main folders")
        self._makeMainDirs()
        log.info("Constructing executable")
        self._constructAndMoveExecutable()

    def createPackage(self):
        raise NotImplementedError

    def createPackageForOffline(self):
        log.debug("Removing main folders")
        self._clearMainFolders()
        log.debug("Creating main folders")
        self._makeMainDirs()
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            self._getPlatformioPackages()
            self._constructWeb2boardExecutable()
            shutil.move(self.installerCreationExecutablesPath, self.installerOfflinePath)
            web2boardLauncherPath = os.path.join(self.installerOfflinePath, "res", "web2boardLauncher" + utils.get_executable_extension(True))
            shutil.move(web2boardLauncherPath, self.installerOfflinePath)
        finally:
            os.chdir(currentPath)
            self._clearBuildFiles()


    @staticmethod
    def constructCurrentPlatformPackager(architecture=ARCH_64):
        """
        :param architecture: use this architecture to for linux packager
        :rtype: Packager
        """
        if utils.is_mac():
            from MacPackager import MacPackager
            return MacPackager()
        elif utils.is_linux():
            from LinuxPackager import LinuxPackager
            return LinuxPackager(architecture=architecture)
        elif utils.is_windows():
            from WindowsPackager import WindowsPackager
            return WindowsPackager()
