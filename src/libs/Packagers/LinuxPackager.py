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
        self.installer_path = self.installer_folder + os.sep + "debian_{}".format(architecture)
        self.installer_offline_path = self.installer_folder + os.sep + "debian_{}Offline".format(architecture)

        self.installer_creation_path = join(self.web2board_path,
                                            "deb_web2board_{}_{}".format(architecture, self.version))
        self.installer_creation_name = os.path.basename(self.installer_creation_path)
        self.installer_creation_w2b_path = join(self.installer_creation_path, "executables")
        self.installer_creation_dist_path = join(self.installer_creation_path, "opt", "web2board")

        self.pkg_platform_path = join(self.pkg_path, "linux")
        self.res_platform_path = join(self.res_path, "linux")
        self.web2board_executable_name = "web2board"
        self.web2board_spec_path = join(self.web2board_path, "web2board-linux.spec")

        self.package_debian_metadata_path = join(self.installer_creation_path, "DEBIAN")
        self.debian_metadata_path = join(self.pkg_platform_path, "debian")
        with open(self.packager_res_path + os.sep + "Web2Board-template.desktop") as desktopFile:
            self.Web2BoardDesktopTemplate = desktopFile.read()

    def _make_main_dirs(self):
        Packager._make_main_dirs(self)

    def _add_metadata_for_installer(self):
        Packager._add_metadata_for_installer(self)
        copytree(self.debian_metadata_path, self.package_debian_metadata_path)
        with open(self.package_debian_metadata_path + os.sep + "control", "r") as controlFile:
            control_text = controlFile.read()
        with open(self.package_debian_metadata_path + os.sep + "control", "w") as controlFile:
            controlFile.write(control_text.format(version=self.version, architecture=self.architecture))

        os.chmod(self.debian_metadata_path + os.sep + "control", int("655", 8))

    def _move_deb_to_installer_path(self):
        resulting_deb = self.web2board_path + os.sep + self.installer_creation_name + ".deb"
        shutil.move(resulting_deb, self.installer_path + os.sep + "web2board.deb")

    def _create_linux_installer(self):
        installer_files = ["web2board_installer.py", "web2board_installer.spec"]
        for installer_file in installer_files:
            shutil.copy(self.pkg_platform_path + os.sep + installer_file, self.installer_path + os.sep + installer_file)
        current_path = os.getcwd()
        os.chdir(self.installer_path)
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
            os.chdir(current_path)

    def create_package(self):
        try:
            self._create_main_structure_and_executables()
            log.info("Adding metadata for installer")
            self._add_metadata_for_installer()
            os.chdir(self.installer_creation_path)
            log.info("Creating deb")
            os.system("chmod -R 777 " + self.installer_creation_dist_path)
            call(["dpkg-deb", "--build", self.installer_creation_path])
            self._move_deb_to_installer_path()
            log.info("Creating Linux installer")
            self._create_linux_installer()
            log.info("installer created successfully")
        finally:
            log.info("Cleaning files")
            os.chdir(self.web2board_path)
            self._clear_build_files()
            # self._deleteInstallerCreationFolder()
