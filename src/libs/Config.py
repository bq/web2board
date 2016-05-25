import os
import json
import logging

import sys
from ConfigParser import ConfigParser

from libs.Decorators.Synchronized import synchronized
from libs.PathsManager import PathsManager
from threading import Lock
my_lock = Lock()


class ConfigException(Exception):
    pass


class Config:
    _log = logging.getLogger(__name__)
    web_socket_ip = ""
    web_socket_port = 9876
    proxy = None
    download_url_template = "https://github.com/bq/web2board/archive/devel.zip"
    bitbloq_libs_download_url_template = 'https://github.com/bq/bitbloqLibs/archive/v{version}.zip'
    check_online_updates = True
    check_libraries_updates = True
    log_level = logging.INFO
    plugins_path = (PathsManager.MAIN_PATH + os.sep + "plugins").decode(sys.getfilesystemencoding())

    @classmethod
    def get_platformio_lib_dir(cls):
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_WORKSPACE_SKELETON + os.sep + "platformio.ini") as platformioIniFile:
            parser.readfp(platformioIniFile)
        if parser.has_option("platformio", "lib_dir"):
            return os.path.abspath(parser.get("platformio", "lib_dir"))
        else:
            return PathsManager.PLATFORMIO_WORKSPACE_SKELETON + os.sep + "lib"

    @classmethod
    def set_platformio_lib_dir(cls, libDir):
        if not os.path.exists(libDir):
            raise ConfigException("Libraries directory does not exist")
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_INI_PATH) as platformioIniFile:
            parser.readfp(platformioIniFile)
        if not parser.has_section("platformio"):
            parser.add_section("platformio")
        parser.set("platformio", "lib_dir", os.path.abspath(libDir))
        with open(PathsManager.PLATFORMIO_INI_PATH, "wb") as platformioIniFile:
            parser.write(platformioIniFile)

    @classmethod
    def get_config_values(cls):
        configValues = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}
        configValues.pop("read_config_file")
        configValues.pop("store_config_in_file")
        configValues.pop("set_platformio_lib_dir")
        configValues.pop("get_platformio_lib_dir")
        configValues.pop("get_config_values")
        configValues.pop("get_client_ws_ip")
        configValues.pop("log_values")
        return configValues

    @classmethod
    def read_config_file(cls):
        if os.path.exists(PathsManager.CONFIG_PATH):
            try:
                cls._log.info("Reading config file")
                with open(PathsManager.CONFIG_PATH) as f:
                    jsonObject = json.load(f)
                cls.__dict__.update(jsonObject)
            except ValueError:
                cls._log.error("Json corrupted so it was ignored, necessary to check!")
        else:
            cls.store_config_in_file()

    @classmethod
    @synchronized(my_lock)
    def store_config_in_file(cls):
        with open(PathsManager.CONFIG_PATH, "w") as f:
            configValues = cls.get_config_values()
            json.dump(configValues, f, indent=4)

    @classmethod
    def get_client_ws_ip(cls):
        return "127.0.0.1" if Config.web_socket_ip == "" else Config.web_socket_ip

    @classmethod
    def log_values(cls):
        cls._log.debug("configuration: {}".format(cls.get_config_values()))
