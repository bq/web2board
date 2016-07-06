import logging
import os
import shutil
import zipfile
from os.path import join
import click
import sys

from libs import utils
from libs.PathsManager import PathsManager as pm
from libs.Updaters.LibsUpdater import LibsUpdater
from libs.AppVersion import AppVersion
from libs.utils import find_files
from platformio import util
from platformio.platforms.base import PlatformFactory

pardir = os.path.pardir
log = logging.getLogger(__name__)


class Packager:
    ARCH_64, ARCH_32 = "amd64", "i386"

    def __init__(self):
        module_path = utils.get_module_path().encode(sys.getfilesystemencoding())
        self.packager_res_path = join(module_path, "res")
        self.web2board_path = os.path.abspath(join(module_path, pardir, pardir, pardir))
        self.src_path = join(self.web2board_path, "src")
        self.res_path = join(self.web2board_path, "res")
        self.res_common_path = join(self.res_path, "common")
        self.icon_path = pm.RES_ICO_PATH
        self.src_res_path = join(self.src_path, "res")
        self.pkg_path = join(self.web2board_path, "pkg")
        self.pyinstaller_dist_folder = self.src_path + os.sep + "dist"
        self.pyinstaller_build_folder = self.src_path + os.sep + "build"
        self.installer_folder = join(self.web2board_path, "installers")
        AppVersion.read_version_values()
        self.version = AppVersion.web2board

        self.web2board_spec_path = join(self.web2board_path, "web2board.spec")

        # abstract attributes
        self.installer_path = None
        self.installer_offline_path = None
        self.installer_creation_path = None
        self.installer_creation_w2b_path = None
        self.installer_creation_dist_path = None
        self.installer_creation_name = None
        self.pkg_platform_path = None
        self.res_platform_path = None

        self.web2board_executable_name = None

    # todo move this to attribute
    def _get_installer_creation_res_path(self):
        return join(self.installer_creation_w2b_path, 'res')

    # todo move this to attribute
    def _get_platformio_packages_path(self):
        return join(self._get_installer_creation_res_path(), pm.PLATFORMIO_PACKAGES_NAME)

    def prepare_res_folder_for_executable(self):
        if not os.path.exists(self.src_res_path):
            os.makedirs(self.src_res_path)

        utils.copytree(self.res_common_path, self.src_res_path, force_copy=True)
        utils.copytree(self.res_platform_path, self.src_res_path, force_copy=True)
        LibsUpdater().restore_current_version_if_necessary()

    def _delete_installer_creation_folder(self):
        if os.path.exists(self.installer_creation_path):
            shutil.rmtree(self.installer_creation_path)

    def _clear_main_folders(self):
        log.info("cleaning folders %s, %s", self.installer_path, self.installer_offline_path)
        if os.path.exists(self.installer_path):
            shutil.rmtree(self.installer_path)
        if os.path.exists(self.installer_offline_path):
            shutil.rmtree(self.installer_offline_path)
        self._clear_build_files()
        self._delete_installer_creation_folder()

    def _clear_build_files(self):
        log.info("cleaning folders %s, %s", self.pyinstaller_dist_folder, self.pyinstaller_build_folder)
        if os.path.exists(self.pyinstaller_dist_folder):
            shutil.rmtree(self.pyinstaller_dist_folder)
        if os.path.exists(self.pyinstaller_build_folder):
            shutil.rmtree(self.pyinstaller_build_folder)

    def _add_metadata_for_installer(self):
        pass

    def _make_main_dirs(self):
        os.makedirs(self.installer_creation_path)
        os.makedirs(self.installer_creation_dist_path)
        os.makedirs(self.installer_creation_w2b_path)
        os.makedirs(self.installer_path)

    def _construct_and_move_executable(self):
        current_path = os.getcwd()
        os.chdir(self.src_path)
        try:
            self._get_platformio_packages()
            self._construct_web2board_executable()
            # shutil.move(self.installer_creation_w2b_path, join(self.installer_creation_dist_path, "web2board"))
            self._construct_link_executable()
        finally:
            os.chdir(current_path)

    def _construct_link_executable(self):
        os.chdir(self.src_path)
        log.debug("Creating Web2boardLink Executable")
        os.system("pyinstaller -w \"{}\"".format("web2boardLink.py"))
        utils.copytree(join(self.pyinstaller_dist_folder, "web2boardLink"), self.installer_creation_dist_path)

    def _construct_web2board_executable(self):
        log.debug("Creating Web2board Executable")
        os.system("pyinstaller \"{}\"".format(self.web2board_spec_path))
        src = join(self.pyinstaller_dist_folder, "web2board")
        utils.copytree(src, self.installer_creation_w2b_path)

    def _compress_executables(self):
        packages_files = find_files(self.installer_creation_w2b_path, ["*", "**/*"])
        packages_files = [x[len(self.installer_creation_w2b_path) + 1:] for x in packages_files]
        with zipfile.ZipFile(self.installer_creation_dist_path + os.sep + "web2board.zip", "w",
                             zipfile.ZIP_DEFLATED) as z:
            os.chdir(self.installer_creation_w2b_path)
            with click.progressbar(packages_files, label='Compressing...') as packagesFilesInProgressBar:
                for zipFilePath in packagesFilesInProgressBar:
                    z.write(zipFilePath)

    def _get_platformio_packages(self):
        log.debug("Getting Scons Packages")
        ori_current_dir = os.getcwd()
        ori_click_confirm = click.confirm

        def click_confirm(message):
            print message
            return True

        click.confirm = click_confirm
        try:
            os.chdir(pm.PLATFORMIO_WORKSPACE_SKELETON)
            config = util.get_project_config()
            for section in config.sections():
                env_options_dict = {x[0]: x[1] for x in config.items(section)}
                platform = PlatformFactory.newPlatform(env_options_dict["platform"])
                log.info("getting packages for: {}".format(env_options_dict))
                platform.configure_default_packages(env_options_dict, ["upload"])
                platform._install_default_packages()
            os.chdir(ori_current_dir)

            log.info("all platformio packages are successfully installed")

            platformio_packages_path = os.path.abspath(util.get_home_dir())

            def is_doc(file_path):
                is_doc_condition = os.sep + "doc" + os.sep not in file_path
                is_doc_condition = is_doc_condition and os.sep + "examples" + os.sep not in file_path
                is_doc_condition = is_doc_condition and os.sep + "tool-scons" + os.sep not in file_path
                is_doc_condition = is_doc_condition and os.sep + "README" not in file_path.upper()
                return not is_doc_condition

            # installerPlatformioPackagesPath = self._getPlatformIOPackagesPath()
            # if os.path.exists(installerPlatformioPackagesPath):
            #     shutil.rmtree(installerPlatformioPackagesPath)
            #
            # os.makedirs(installerPlatformioPackagesPath)

            log.info("Cleaning platformio packages files")
            all_files = sorted(utils.find_files(platformio_packages_path, ["*", "**" + os.sep + "*"]), reverse=True)
            for i, f in enumerate(all_files):
                if is_doc(f):
                    if os.path.isfile(f):
                        os.remove(f)
                    else:
                        try:
                            os.rmdir(f)
                        except:
                            shutil.rmtree(f)
        finally:
            os.chdir(ori_current_dir)
            click.confirm = ori_click_confirm

    def _create_main_structure_and_executables(self):
        log.debug("Removing main folders")
        self._clear_main_folders()
        log.debug("Creating main folders")
        self._make_main_dirs()
        log.info("Constructing executable")
        self._construct_and_move_executable()

    def create_package(self):
        raise NotImplementedError

    def create_package_for_offline(self):
        log.debug("Removing main folders")
        self._clear_main_folders()
        log.debug("Creating main folders")
        self._make_main_dirs()
        current_path = os.getcwd()
        os.chdir(self.src_path)
        try:
            self._get_platformio_packages()
            self._construct_web2board_executable()
            shutil.move(join(self.installer_creation_dist_path, "web2board"), self.installer_offline_path)
        finally:
            os.chdir(current_path)
            self._clear_build_files()


    @staticmethod
    def construct_current_platform_packager(architecture=ARCH_64):
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
