import logging
import urllib2

from wshubsapi.Hub import Hub
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
        return Config.getConfigValues()

    def setValues(self, configDic):
        configValues = Config.getConfigValues()
        for k in configValues.keys():
            if k in configDic:
                Config.__dict__[k] = configDic[k]
        Config.storeConfigInFile()
        return True

    def setWebSocketInfo(self, IP, port):
        Config.webSocketIP = IP
        Config.webSocketPort = port
        Config.storeConfigInFile()
        return True

    def setLogLevel(self, logLevel):
        utils.setLogLevel(logLevel)
        return True

    def setLibrariesPath(self, libDir):
        Config.setPlatformioLibDir(libDir)
        return True

    def getLibrariesPath(self):
        return Config.getPlatformioLibDir()

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
        Config.storeConfigInFile()

    def testProxy(self, proxyUrl):
        proxy = urllib2.ProxyHandler({'http': proxyUrl})
        opener = urllib2.build_opener(proxy)
        print opener.open(urllib2.Request("http://bitbloq.bq.com/")).read()
        return True