import os
import json

import logging

from libs.PathsManager import PathsManager


class Config:
    _log = logging.getLogger(__name__)
    proxy = None
    version = "2.0.1"
    downloadUrlTemplate = "https://github.com/bq/web2board/archive/devel.zip"
    bitbloqLibsVersion = "0.0.5"
    bitbloqLibsLibraries = [
        "BitbloqBatteryReader",
        "BitbloqButtonPad",
        "BitbloqEnableInterrupt",
        "BitbloqEncoder",
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


    @classmethod
    def readConfigFile(cls):
        if os.path.exists(PathsManager.CONFIG_PATH):
            try:
                with open(PathsManager.CONFIG_PATH) as f:
                    jsonObject = json.loads(f)
                cls.__dict__.update(jsonObject)
            except ValueError:
                cls._log.error("Json corrupted so it was ignored, necessary to check!")
