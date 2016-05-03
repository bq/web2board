import logging
import os
import urllib2
from copy import deepcopy

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

    def get_config(self):
        config = deepcopy(Config.get_config_values())
        config.update(dict(librariesPath=self.get_libraries_path()))
        return config

    def set_values(self, config_dic):
        config_values = Config.get_config_values()
        if "libraries_path" in config_dic:
            libraries_path = config_dic.pop("libraries_path")
            self.set_libraries_path(libraries_path)
        for k in config_values.keys():
            if k in config_dic:
                Config.__dict__[k] = config_dic[k]
        Config.store_config_in_file()
        return True

    def set_web_socket_info(self, IP, port):
        Config.web_socket_ip = IP
        Config.web_socket_port = port
        Config.store_config_in_file()

    def set_log_level(self, logLevel):
        utils.setLogLevel(logLevel)

    def set_libraries_path(self, libDir):
        Config.set_platformio_lib_dir(libDir)

    def get_libraries_path(self):
        return Config.get_platformio_lib_dir()

    def is_possible_libraries_path(self, path):
        return os.path.exists(path)

    def change_platformio_ini_file(self, content):
        with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
            f.write(content)

    def restore_platformio_ini_file(self):
        with open(PathsManager.PLATFORMIO_INI_PATH + ".copy") as fcopy:
            with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
                f.write(fcopy.read())

    def set_proxy(self, proxyUrl):
        Config.proxy = proxyUrl
        Config.store_config_in_file()

    def test_proxy(self, proxyUrl):
        proxy = urllib2.ProxyHandler({'http': proxyUrl})
        opener = urllib2.build_opener(proxy)
        log.debug(opener.open(urllib2.Request("http://bitbloq.bq.com/")).read())
