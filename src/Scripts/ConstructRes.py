import inspect
import os
import platform
from os.path import join

import shutil

from libs import utils


platformToFolder = dict(Linux="linux", Windows="windows", Darwin="darwin")


modulePath = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
os.chdir(modulePath)
resPath = os.path.normpath(join(modulePath, os.pardir, os.pardir, "res"))
srcPath = os.path.normpath(join(modulePath, os.pardir))

resPlatformPath = join(resPath, platformToFolder[platform.system()])
resCommonPath = join(resPath, "common")

srcResPath = join(srcPath, "res")

if os.path.exists(srcResPath):
    shutil.rmtree(srcResPath)

os.makedirs(srcResPath)

utils.copytree(resCommonPath, srcResPath, forceCopy=True)
utils.copytree(resPlatformPath, srcResPath, forceCopy=True)