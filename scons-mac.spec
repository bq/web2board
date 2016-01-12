# -*- mode: python -*-
import sys
import os

sys.path.append(os.getcwd())
from libs import utils
from libs.PathsManager import PathsManager

pathEx = os.getcwd()

a = Analysis([PathsManager.EXTERNAL_RESOURCES_PATH + os.sep +'sconsScript.py'],
             pathex=[pathEx],
             hiddenimports=['UserList', 'UserString', 'ConfigParser'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])

# a.datas += utils.findFilesForPyInstaller("Test/resources", ["*", "**/*"])
# a.datas += utils.findFilesForPyInstaller("scons", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sconsScript',
          debug=False,
          strip=None,
          upx=True,
          console=True)
