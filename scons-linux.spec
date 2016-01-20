# -*- mode: python -*-
import sys
import os

sys.path.append(os.getcwd())
from libs import utils
originalWorkingPath = os.getcwd()

from libs.PathsManager import PathsManager

os.chdir(os.path.join(os.getcwd(), os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH)))

a = Analysis([os.path.join(os.getcwd(), os.path.dirname(PathsManager.SCONS_EXECUTABLE_PATH), 'sconsScript.py')],
             pathex=[os.getcwd()],
             hiddenimports=['UserList', 'UserString', 'ConfigParser'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

# a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
# a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])

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
