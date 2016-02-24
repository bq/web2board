import os
import json

import logging

import sys
from ConfigParser import ConfigParser

from libs.Decorators.Synchronized import synchronized
from libs.PathsManager import PathsManager
from threading import Lock
my_lock = Lock()


class Config:
    _log = logging.getLogger(__name__)
    webSocketIP = "127.0.0.1"
    webSocketPort = 9876
    proxy = None
    version = "2.0.0"
    downloadUrlTemplate = "https://github.com/bq/web2board/archive/devel.zip"
    bitbloqLibsVersion = "0.1.0"
    bitbloqLibsLibraries = [
        "BitbloqBatteryReader",
        "BitbloqButtonPad",
        "BitbloqEnableInterrupt",
        "BitbloqEncoder",
        "BitbloqEvolution",
        "BitbloqHTS221",
        "BitbloqJoystick",
        "BitbloqLedMatrix",
        "BitbloqLineFollower",
        "BitbloqLiquidCrystal",
        "BitbloqOscillator",
        "BitbloqRGB",
        "BitbloqRTC",
        "BitbloqSoftwareSerial",
        "BitbloqUS",
        "BitbloqZowi",
        "BitbloqZowiSerialCommand"
    ]
    bitbloqLibsDownloadUrlTemplate = 'https://github.com/bq/bitbloqLibs/archive/v{version}.zip'
    checkOnlineUpdates = True
    logLevel = logging.INFO
    pluginsPath = (PathsManager.MAIN_PATH + os.sep + "plugins").decode(sys.getfilesystemencoding())

    @classmethod
    def getPlatformioLibDir(cls):
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_WORKSPACE_PATH + os.sep + "platformio.ini") as platformioIniFile:
            parser.readfp(platformioIniFile)
        if parser.has_option("platformio", "lib_dir"):
            return os.path.abspath(parser.get("platformio", "lib_dir"))
        else:
            return PathsManager.PLATFORMIO_WORKSPACE_PATH + os.sep + "lib"

    @classmethod
    def setPlatformioLibDir(cls, libDir):
        parser = ConfigParser()
        with open(PathsManager.PLATFORMIO_INI_PATH) as platformioIniFile:
            parser.readfp(platformioIniFile)
        assert os.path.isdir(libDir)
        parser.set("platformio", "lib_dir", os.path.abspath(libDir))
        with open(PathsManager.PLATFORMIO_INI_PATH, "wb") as platformioIniFile:
            parser.write(platformioIniFile)

    @classmethod
    def getConfigValues(cls):
        configValues = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}
        configValues.pop("readConfigFile")
        configValues.pop("storeConfigInFile")
        configValues.pop("setPlatformioLibDir")
        configValues.pop("getPlatformioLibDir")
        configValues.pop("getConfigValues")
        return configValues

    @classmethod
    def readConfigFile(cls):
        if os.path.exists(PathsManager.CONFIG_PATH):
            try:
                cls._log.info("Reading config file")
                with open(PathsManager.CONFIG_PATH) as f:
                    jsonObject = json.load(f)
                cls.__dict__.update(jsonObject)
            except ValueError:
                cls._log.error("Json corrupted so it was ignored, necessary to check!")
        else:
            cls.storeConfigInFile()

    @classmethod
    @synchronized(my_lock)
    def storeConfigInFile(cls):
        with open(PathsManager.CONFIG_PATH, "w") as f:
            configValues = cls.getConfigValues()
            json.dump(configValues, f, indent=4)
