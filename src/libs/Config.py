import os
import json
import logging

import sys
from ConfigParser import ConfigParser

from libs.Decorators.Synchronized import synchronized
from libs.PathsManager import PathsManager
from threading import Lock
from libs.utils import rmtree
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
    parallel_compiling_max_threads = 50

    @classmethod
    def get_platformio_lib_dir(cls):
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_WORKSPACE_PATH + os.sep + "platformio.ini") as platformioIniFile:
            parser.readfp(platformioIniFile)
        if parser.has_option("platformio", "lib_dir"):
            return os.path.abspath(parser.get("platformio", "lib_dir"))
        else:
            return PathsManager.PLATFORMIO_WORKSPACE_PATH + os.sep + "lib"

    @classmethod
    def set_platformio_lib_dir(cls, lib_dir):
        if not os.path.exists(lib_dir):
            raise ConfigException("Libraries directory does not exist")
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_INI_PATH) as platformioIniFile:
            parser.readfp(platformioIniFile)
        if not parser.has_section("platformio"):
            parser.add_section("platformio")
        parser.set("platformio", "lib_dir", os.path.abspath(lib_dir))
        platformio_libs_path = os.path.join(PathsManager.PLATFORMIO_WORKSPACE_PATH, 'lib')
        if os.path.exists(platformio_libs_path) and lib_dir != platformio_libs_path:
            rmtree(platformio_libs_path)
        with open(PathsManager.PLATFORMIO_INI_PATH, "wb") as platformioIniFile:
            parser.write(platformioIniFile)

    @classmethod
    def get_config_values(cls):
        config_values = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}
        config_values.pop("read_config_file")
        config_values.pop("store_config_in_file")
        config_values.pop("set_platformio_lib_dir")
        config_values.pop("get_platformio_lib_dir")
        config_values.pop("get_config_values")
        config_values.pop("get_client_ws_ip")
        config_values.pop("log_values")
        return config_values

    @classmethod
    def read_config_file(cls):
        if os.path.exists(PathsManager.CONFIG_PATH):
            try:
                cls._log.info("Reading config file")
                with open(PathsManager.CONFIG_PATH) as f:
                    json_object = json.load(f)
                cls.__dict__.update(json_object)
                cls.proxy = cls.proxy if cls.proxy != "" else None
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
