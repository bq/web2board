#!/usr/bin/env python
import os
import sys
print os.getcwd()
sys.path.append(os.getcwd())

from libs.Packagers.Packager import Packager
from libs.LoggingUtils import initLogging

initLogging(__name__)

architectureInt = 64

if len(sys.argv) > 1:
    architectureInt = int(sys.argv[1])

architecture = Packager.ARCH_32 if architectureInt == 32 else Packager.ARCH_64
print "packaging for architecture: {}".format(architecture)
packager = Packager.constructCurrentPlatformPackager(architecture=architecture)
packager.createPackage()
