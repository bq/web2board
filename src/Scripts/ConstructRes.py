import sys

import inspect
import os
import platform
from os.path import join
import shutil



platformToFolder = dict(Linux="linux", Windows="windows", Darwin="darwin")

modulePath = os.path.abspath(os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename))
os.chdir(modulePath)
resPath = os.path.abspath(os.path.normpath(join(modulePath, os.pardir, os.pardir, "res")))
srcPath = os.path.abspath(os.path.normpath(join(modulePath, os.pardir)))

resPlatformPath = join(resPath, platformToFolder[platform.system()])
resCommonPath = join(resPath, "common")

srcResPath = join(srcPath, "res")

sys.path += [srcPath]

if os.path.exists(srcResPath):
    shutil.rmtree(srcResPath)

os.makedirs(srcResPath)

from libs import utils

utils.copytree(resCommonPath, srcResPath, forceCopy=True)
utils.copytree(resPlatformPath, srcResPath, forceCopy=True)