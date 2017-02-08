import logging
import os
import shutil
import urllib2
from copy import deepcopy

import time
from wshubsapi.hub import Hub
from libs.Config import Config
from libs import utils
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)


class ConfigHubException(Exception):
    pass


class ConfigHub(Hub):
    def __init__(self):
        super(ConfigHub, self).__init__()
        self.default_platformio_ini_path = PathsManager.PLATFORMIO_INI_PATH + ".default"

    def get_config(self):
        config = deepcopy(Config.get_config_values())
        config.update(dict(libraries_path=self.get_libraries_path()))
        return config

    def set_values(self, config_dic):
        config_values = Config.get_config_values()
        if "libraries_path" in config_dic:
            libraries_path = config_dic.pop("libraries_path")
            self.set_libraries_path(libraries_path)
        for k in config_values.keys():
            if k in config_dic:
                Config.__dict__[k] = config_dic[k]
        if Config.proxy is not None:
            utils.set_proxy(dict(http=Config.proxy, https=Config.proxy))
        Config.store_config_in_file()
        return True

    def set_web_socket_info(self, IP, port):
        Config.web_socket_ip = IP
        Config.web_socket_port = port
        Config.store_config_in_file()

    def set_log_level(self, log_level):
        utils.set_log_level(log_level)

    def set_libraries_path(self, lib_dir):
        Config.set_platformio_lib_dir(lib_dir)
        PathsManager.clean_pio_envs()

    def get_libraries_path(self):
        return Config.get_platformio_lib_dir()

    def is_possible_libraries_path(self, path):
        return os.path.exists(path)

    def change_platformio_ini_file(self, content):
        if not os.path.exists(self.default_platformio_ini_path):
            shutil.copyfile(PathsManager.PLATFORMIO_INI_PATH, self.default_platformio_ini_path)
        with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
            f.write(content)

    def restore_platformio_ini_file(self):
        if os.path.exists(self.default_platformio_ini_path):
            with open(self.default_platformio_ini_path) as f_default:
                with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
                    f.write(f_default.read())
            return True
        else:
            return False

    def set_proxy(self, proxy_url):
        Config.proxy = proxy_url
        Config.store_config_in_file()

    def test_proxy(self, proxy_url):
        proxy_info = dict(http=proxy_url, https=proxy_url) if proxy_url not in ("", None) else None
        proxy = urllib2.ProxyHandler(proxy_info)
        opener = urllib2.build_opener(proxy)
        opener.open(urllib2.Request("http://bitbloq.bq.com/"), timeout=5).read()
