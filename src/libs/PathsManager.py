import glob
import logging
import os
import sys
from os.path import expanduser, join
import platform
import shutil

from libs import utils

_pathsLog = logging.getLogger(__name__)


class PathsManager:
    def __init__(self):
        pass

    EXECUTABLE_PATH = None
    EXECUTABLE_FILE = None
    MAIN_PATH = None
    PLATFORMIO_PACKAGES_NAME = "pp"
    PLATFORMIO_PACKAGES_PATH = None
    CONFIG_PATH = None
    VERSION_PATH = None
    COPY_PATH = None
    ORIGINAL_PATH = None

    RES_PATH = None
    RES_ICO_PATH = None
    RES_ICONS_PATH = None
    RES_BOARDS_PATH = None
    RES_PLATFORMIO_PATH = None
    RES_LOGGING_CONFIG_PATH = None
    RES_SCONS_ZIP_PATH = None
    TEST_RES_PATH = None

    PROGRAM_PATH = None
    PLATFORMIO_WORKSPACE_SKELETON = None
    PLATFORMIO_WORKSPACE_PATH = None
    PLATFORMIO_INI_PATH = None
    TEST_SETTINGS_PATH = None

    SCONS_EXECUTABLE_PATH = None

    @classmethod
    def get_main_path(cls):
        return cls.get_base_path()

    @staticmethod
    def get_base_path():
        if utils.are_we_frozen():
            if utils.is_mac():
                return os.getcwd()
            return os.getcwd()
        else:
            return os.getcwd()

    @classmethod
    def get_external_data_folder(cls):
        if utils.is_linux():
            folder = ".web2board"
        elif utils.is_windows():
            folder = "web2board"
        elif utils.is_mac():
            folder = ".web2board"
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))
        return join(cls.get_home_path(), folder)

    @staticmethod
    def get_home_path():
        if utils.is_linux():
            return expanduser("~")
        elif utils.is_windows():
            return os.getenv('APPDATA')
        elif utils.is_mac():
            return expanduser("~")
        else:
            raise Exception("Not supported platform: {}".format(platform.system()))

    @classmethod
    def get_dst_path_for_update(cls, version):
        return join(cls.get_home_path(), ".web2board_{}".format(version))

    @classmethod
    def get_sons_executable_path(cls):
        return os.path.abspath(join(cls.RES_PATH, "Scons", "sconsScript.py"))

    @classmethod
    def get_platformio_packages_path(cls):
        path = join(cls.RES_PATH, cls.PLATFORMIO_PACKAGES_NAME)
        return os.path.abspath(path)

    @classmethod
    def log_relevant_environmental_paths(cls):
        _pathsLog.debug('Working directory: {}'.format(os.getcwd()))
        items = cls.__dict__.items()
        items = sorted(items, key=lambda x: x[0])
        for key, path in items:
            if "PATH" in key:
                _pathsLog.debug('{key}: {path}'.format(key=key, path=path))

    @classmethod
    def get_copy_path_for_update(cls):
        return os.path.abspath(join(cls.MAIN_PATH, os.pardir, ".web2board_copy"))


    @classmethod
    def set_all_constants(cls):
        cls.EXECUTABLE_PATH = os.getcwd()
        cls.EXECUTABLE_FILE = join(cls.EXECUTABLE_PATH, "web2board" + utils.get_executable_extension())
        cls.MAIN_PATH = cls.get_main_path()
        cls.CONFIG_PATH = os.path.normpath(join(cls.MAIN_PATH, os.pardir, '.web2board-config.json'))
        cls.COPY_PATH = cls.get_copy_path_for_update()
        cls.ORIGINAL_PATH = cls.get_external_data_folder()

        cls.RES_PATH = join(cls.MAIN_PATH, 'res')
        cls.VERSION_PATH = join(cls.RES_PATH, 'web2board.version')
        cls.RES_ICO_PATH = join(cls.RES_PATH, 'Web2board.ico')
        cls.RES_ICONS_PATH = join(cls.RES_PATH, 'icons')
        cls.TEST_RES_PATH = join(cls.MAIN_PATH, 'Test', 'resources')
        cls.RES_BOARDS_PATH = join(cls.RES_PATH, 'boards.txt')
        cls.RES_PLATFORMIO_PATH = os.path.abspath(join(cls.RES_PATH, os.pardir, 'platformio'))
        cls.RES_LOGGING_CONFIG_PATH = join(cls.RES_PATH, 'logging.json')
        cls.RES_SCONS_ZIP_PATH = join(cls.MAIN_PATH, "res", "sconsRes.zip")

        cls.PROGRAM_PATH = cls.get_external_data_folder()
        cls.PLATFORMIO_WORKSPACE_SKELETON = join(cls.RES_PATH, 'platformioWorkSpace')
        cls.PLATFORMIO_WORKSPACE_PATH = cls.PLATFORMIO_WORKSPACE_SKELETON
        cls.PLATFORMIO_INI_PATH = join(cls.PLATFORMIO_WORKSPACE_SKELETON, 'platformio.ini')
        cls.TEST_SETTINGS_PATH = join(cls.RES_PATH, 'TestSettings', 'resources')
        cls.SCONS_EXECUTABLE_PATH = cls.get_sons_executable_path()

        cls.PLATFORMIO_PACKAGES_PATH = cls.get_platformio_packages_path()

    @classmethod
    def get_icon_path(cls, iconName):
        return join(PathsManager.RES_ICONS_PATH, iconName)

    @classmethod
    def clean_pio_envs(cls):
        path = join(cls.PLATFORMIO_WORKSPACE_PATH, ".pioenvs")
        if os.path.exists(path):
            shutil.rmtree(path)

# set working directory to src
if utils.are_we_frozen():
    os.chdir(utils.get_module_path())
else:
    os.chdir(join(utils.get_module_path(), os.path.pardir))


PathsManager.set_all_constants()
