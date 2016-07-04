import os
from subprocess import call

from libs import utils
from libs.Packagers.Packager import Packager
from libs.utils import *

log = logging.getLogger(__name__)


class MacPackager(Packager):
    def __init__(self):
        Packager.__init__(self)

        self.installer_path = self.installer_folder + os.sep + "darwin"
        self.installer_offline_path = self.installer_folder + os.sep + "darwinOffline"
        self.installer_creation_path = self.web2board_path + os.sep + "darwin_web2board_{}".format(self.version)
        self.installer_creation_dist_path = os.path.join(self.installer_creation_path, "dist")
        self.installerCreationAppPath = os.path.join(self.installer_creation_dist_path, 'web2boardLink.app')
        self.installer_creation_name = os.path.basename(self.installer_creation_path)
        self.installer_creation_w2b_path = os.path.join(self.installer_creation_path, "executables")
        self.pkg_platform_path = os.path.join(self.pkg_path, "darwin")
        self.res_platform_path = os.path.join(self.res_path, "darwin")

        self.web2board_executable_name = "web2boardLink.app"
        self.web2board_spec_path = os.path.join(self.web2board_path, "web2board-mac.spec")

        self.pkgprojPath = os.path.join(self.installer_creation_path, "create-mpkg", "web2board", "web2board.pkgproj")
        self.installer_background_path = os.path.join(self.res_platform_path, "installer_background.jpg")
        self.licensePath = os.path.join(self.web2board_path, "LICENSE.txt")

        self.app_resources_path = os.path.join(self.installerCreationAppPath, "Contents", "MacOS", "res")
        self.info_plist_path = os.path.join(self.web2board_path, "info.plist")
        self.info_plist_path_dst = os.path.join(self.installerCreationAppPath, "Contents", "info.plist")

    def _add_metadata_for_installer(self):
        Packager._add_metadata_for_installer(self)
        copytree(self.pkg_platform_path, self.installer_creation_path)
        shutil.copy2(self.installer_background_path, self.installer_creation_dist_path)
        shutil.copy2(self.licensePath, self.installer_creation_dist_path)
        shutil.copyfile(self.info_plist_path, self.info_plist_path_dst)
        #  copytree(self._getInstallerCreationResPath(), self.appResourcesPath)

    def _construct_link_executable(self):
        self._clear_build_files()
        os.chdir(self.src_path)
        log.debug("Creating Web2boardLink Executable")
        os.system("pyinstaller -w --onefile \"{}\"".format(self.web2board_path + os.sep + "web2boardLink-mac.spec"))
        utils.copytree(os.path.join(self.pyinstaller_dist_folder, "web2boardLink.app"), self.installerCreationAppPath)

        w2b_origin = os.path.join(self.installer_creation_dist_path, 'web2board')
        w2b_dst = os.path.join(self.app_resources_path, os.pardir, 'web2board')
        shutil.move(w2b_origin, w2b_dst)
        utils.copytree(self.res_common_path, self.app_resources_path)

    def _move_installer_to_installer_folder(self):
        shutil.copy2(self.installer_creation_dist_path + os.sep + "Web2Board.pkg", self.installer_path)

    def create_package(self):
        try:
            self._create_main_structure_and_executables()
            log.debug("Adding metadata for installer")
            self._add_metadata_for_installer()
            os.chdir(self.installer_creation_dist_path)
            log.info("Creating Installer")

            call(["/usr/local/bin/packagesbuild", self.pkgprojPath])
            self._move_installer_to_installer_folder()
            log.info("installer created successfully")
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2board_path)
            self._clear_build_files()
            # self._deleteInstallerCreationFolder()
