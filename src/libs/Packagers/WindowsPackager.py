from subprocess import call
from libs.Packagers.Packager import Packager
from libs.utils import *
from os.path import join

log = logging.getLogger(__name__)


class WindowsPackager(Packager):
    def __init__(self):
        Packager.__init__(self)
        self.installer_path = self.installer_folder + os.sep + "win32"
        self.installer_offline_path = self.installer_folder + os.sep + "win32Offline"
        self.installer_creation_path = self.web2board_path + os.sep + "win_web2board_{}".format(self.version)
        self.installer_creation_name = os.path.basename(self.installer_creation_path)
        self.installer_creation_dist_path = join(self.installer_creation_path, "dist")
        self.installer_creation_executables_path = join(self.installer_creation_path, "executables")
        self.pkg_platform_path = join(self.pkg_path, "win32")
        self.res_platform_path = join(self.res_path, "windows")
        self.web2board_executable_name = "web2board.exe"
        self.sconsExecutableName = "sconsScript.exe"

    def _add_bat_scrips_to_win_dist(self):
        bat_name = "afterInstall.bat"
        shutil.copy2(join(self.installer_creation_path, bat_name), join(self.installer_creation_dist_path, bat_name))
        web2board_reg = "web2board.reg"
        shutil.copy2(join(self.src_res_path, web2board_reg), join(self.installer_creation_dist_path, web2board_reg))
        web2board_reg = "web2boardTo32.reg"
        shutil.copy2(join(self.src_res_path, web2board_reg), join(self.installer_creation_dist_path, web2board_reg))

    def _add_metadata_for_installer(self):
        Packager._add_metadata_for_installer(self)
        copytree(self.pkg_platform_path, self.installer_creation_path)
        shutil.copy2(self.icon_path, self.installer_creation_path + os.sep + os.path.basename(self.icon_path))
        self._add_bat_scrips_to_win_dist()

    def _move_installer_to_installer_folder(self):
        shutil.copy2(self.installer_creation_path + os.sep + "Web2board.exe", self.installer_path)

    def create_package(self):
        try:
            self._create_main_structure_and_executables()
            log.debug("Adding metadata for installer")
            self._add_metadata_for_installer()
            os.chdir(self.installer_creation_path)
            log.info("Creating Installer")
            call(["makensis", "installer.nsi"])
            self._move_installer_to_installer_folder()
            log.info("installer created successfully")
        except Exception as e:
            log.exception("Error compiling")
            print(str(e))
        finally:
            log.debug("Cleaning files")
            os.chdir(self.web2board_path)
            self._clear_build_files()
            # self._deleteInstallerCreationFolder()
