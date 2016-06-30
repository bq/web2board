import sys

import inspect
import os
import platform
from os.path import join
import shutil


platform_to_folder = dict(Linux="linux", Windows="windows", Darwin="darwin")

modulePath = os.path.abspath(os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename))
os.chdir(modulePath)
resPath = os.path.abspath(os.path.normpath(join(modulePath, os.pardir, os.pardir, "res")))
srcPath = os.path.abspath(os.path.normpath(join(modulePath, os.pardir)))

resPlatformPath = join(resPath, platform_to_folder[platform.system()])
resCommonPath = join(resPath, "common")

srcResPath = join(srcPath, "res")

sys.path += [srcPath]


if "removeFolder" in sys.argv:
    if os.path.exists(srcResPath):
        shutil.rmtree(srcResPath)
if not os.path.exists(srcResPath):
    os.makedirs(srcResPath)

from libs import utils

utils.copytree(resCommonPath, srcResPath, force_copy=True)
utils.copytree(resPlatformPath, srcResPath, force_copy=True)