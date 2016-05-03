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

    def getConfig(self):
        config = deepcopy(Config.get_config_values())
        config.update(dict(librariesPath=self.getLibrariesPath()))
        return config

    def setValues(self, configDic):
        configValues = Config.get_config_values()
        if "librariesPath" in configDic:
            librariesPath = configDic.pop("librariesPath")
            self.setLibrariesPath(librariesPath)
        for k in configValues.keys():
            if k in configDic:
                Config.__dict__[k] = configDic[k]
        Config.store_config_in_file()
        return True

    def setWebSocketInfo(self, IP, port):
        Config.web_socket_ip = IP
        Config.web_socket_port = port
        Config.store_config_in_file()
        return True

    def setLogLevel(self, logLevel):
        utils.setLogLevel(logLevel)
        return True

    def setLibrariesPath(self, libDir):
        Config.set_platformio_lib_dir(libDir)
        return True

    def getLibrariesPath(self):
        return Config.get_platformio_lib_dir()

    def isPossibleLibrariesPath(self, path):
        return os.path.exists(path)

    def changePlatformioIniFile(self, content):
        with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
            f.write(content)
        return True

    def restorePlatformioIniFile(self):
        with open(PathsManager.PLATFORMIO_INI_PATH + ".copy") as fcopy:
            with open(PathsManager.PLATFORMIO_INI_PATH, "w") as f:
                f.write(fcopy.read())
        return True

    def setProxy(self, proxyUrl):
        Config.proxy = proxyUrl
        Config.store_config_in_file()

    def testProxy(self, proxyUrl):
        proxy = urllib2.ProxyHandler({'http': proxyUrl})
        opener = urllib2.build_opener(proxy)
        print opener.open(urllib2.Request("http://bitbloq.bq.com/")).read()
        return True
