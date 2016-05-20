#!/usr/bin/env python
import inspect
import os
import sys

modulePath = os.path.abspath(os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename))
sys.path.append(os.path.normpath(os.path.join(modulePath, os.pardir)))

from libs.Config import Config
from libs.Version import Version

print os.getcwd()
sys.path.append(os.getcwd())

from libs.Packagers.Packager import Packager
from libs.LoggingUtils import initLogging

architectureInt = 64
offline = "offline" in sys.argv
if "32" in sys.argv:
    architectureInt = int(sys.argv[1])

Version.read_version_values()
Config.read_config_file()
architecture = Packager.ARCH_32 if architectureInt == 32 else Packager.ARCH_64
packager = Packager.constructCurrentPlatformPackager(architecture=architecture)
packager.prepareResFolderForExecutable()

log = initLogging(__name__)
log.info("packaging for architecture: {}".format(architecture))
if offline:
    log.info("packaging for OFFLINE")
    packager.createPackageForOffline()
else:
    log.info("packaging")
    packager.createPackage()