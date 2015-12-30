import json
import logging
import logging.config
import os
import shutil
from subprocess import call

import platform

from libs import utils

pDir = os.path.pardir

logging.config.dictConfig(json.load(open('res' + os.sep + 'logging.json')))
log = logging.getLogger(__name__)


class Packager:
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
        self.version = json.load(open(os.path.join(self.resPath, "common", "config.json")))["version"]

        self.web2boardSpecPath = os.path.join(self.srcResPath, "web2board.spec")
        self.serialMonitorSpecPath = os.path.join(self.srcResPath, "serialMonitor.spec")

        # abstract attributes
        self.installerPath = None
        self.installerCreationPath = None
        self.installerCreationDistPath = None
        self.installerCreationName = None
        self.pkgPlatformPath = None
        self.resPlatformPath = None

        self.web2boardExecutableName = None
        self.serialMonitorExecutableName = None

        os.chdir(self.web2boardPath)

    def _prepareResFolderForExecutable(self):
        if os.path.exists(self.srcResPath):
            shutil.move(self.srcResPath, self.auxiliarySrcResPath)
        utils.copytree(self.resCommonPath, self.srcResPath)
        utils.copytree(self.resPlatformPath, self.srcResPath)

    def _deleteInstallerCreationFolder(self):
        if os.path.exists(self.installerCreationPath):
            shutil.rmtree(self.installerCreationPath)

    def _clearMainFolders(self):
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

    def _makeMainDirs(self):
        os.makedirs(self.installerCreationPath)
        os.makedirs(self.installerCreationDistPath)
        os.makedirs(self.installerPath)

    def _restoreSrcResFolder(self):
        shutil.rmtree(self.srcResPath)
        if os.path.exists(self.auxiliarySrcResPath):
            shutil.move(self.auxiliarySrcResPath, self.srcResPath)

    def _constructAndMoveExecutable(self):
        currentPath = os.getcwd()
        os.chdir(self.srcPath)
        try:
            call(["pyinstaller", "--onefile", self.web2boardSpecPath])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.web2boardExecutableName), self.installerCreationDistPath)
            call(["pyinstaller", "--onefile", self.serialMonitorSpecPath])
            shutil.copy2(os.path.join(self.pyInstallerDistFolder, self.serialMonitorExecutableName),
                         self.installerCreationDistPath)
        finally:
            os.chdir(currentPath)

    def _createMainStructureAndExecutables(self):
        log.debug("Removing main folders")
        self._clearMainFolders()
        log.debug("Creating main folders")
        self._makeMainDirs()
        log.debug("Adding resources for executable")
        self._prepareResFolderForExecutable()
        log.info("Constructing executable")
        self._constructAndMoveExecutable()

    @staticmethod
    def constructCurrentPlatformPackager():
        """
        :rtype: Packager
        """
        if platform.system() == 'Darwin':
            from MacPackager import MacPackager
            return MacPackager()
        elif platform.system() == 'linux':
            from LinuxPackager import LinuxPackager
            return LinuxPackager()
        elif platform.system() == 'windows':
            from WindowsPackager import WindowsPackager
            return WindowsPackager()

