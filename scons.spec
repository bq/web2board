# -*- mode: python -*-
import sys
import os

sys.path.append(os.path.join(os.getcwd()))
from libs import utils

originalWorkingPath = os.getcwd()
from libs.PathsManager import PathsManager

PathsManager.logRelevantEnvironmentalPaths()
block_cipher = None
os.chdir(os.path.join(os.getcwd(), os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH)))

a = Analysis([os.path.join(os.getcwd(), os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH), 'sconsScript.py')],
             pathex=[os.getcwd()],
             binaries=None,
             datas=None,
             hiddenimports=['UserList', 'UserString', 'ConfigParser', 'json'],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

a.datas += utils.findFilesForPyInstaller(os.path.join(originalWorkingPath, "platformio"), ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller(os.path.join(originalWorkingPath, PathsManager.RES_PATH), ["*", "**/*"])


print a.datas
# a.datas += utils.findFilesForPyInstaller("Test/resources", ["*", "**/*"])
# a.datas += utils.findFilesForPyInstaller("scons", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='sconsScript',
          debug=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sconsScript')
