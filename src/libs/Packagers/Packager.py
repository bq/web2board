import json
import os

from libs import utils
pDir = os.path.pardir


class Packager:
    web2boardPath = None
    srcPath = None
    resPath = None
    pkgPath = None
    packagerResPath = None

    def __init__(self):
        self.version = None
        self._initPaths()
        os.chdir(self.srcPath)

    def _initPaths(self):
        if self.web2boardPath is None:
            modulePath = utils.getModulePath()
            self.packagerResPath = os.path.join(modulePath, "res")
            self.web2boardPath = os.path.abspath(os.path.join(modulePath, pDir, pDir, pDir))
            self.srcPath = os.path.join(self.web2boardPath, "src")
            self.resPath = os.path.join(self.web2boardPath, "res")
            self.pkgPath = os.path.join(self.web2boardPath, "pkg")
        self.version = json.load(open(os.path.join(self.resPath, "common", "config.json")))["version"]


