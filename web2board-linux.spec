# -*- mode: python -*-
import os
import sys
import zipfile

sys.path.append(os.getcwd())
import libs.utils as utils
from libs.PathsManager import PathsManager

block_cipher = None
print os.getcwd()

a = Analysis(['src' + os.sep + 'web2board.py'],
             pathex=[os.getcwd()],
             hiddenimports=['libs.LoggingUtils', 'libs.WSCommunication.Hubs'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("Test/resources", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='web2board',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=PathsManager.RES_ICO_PATH)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='web2board')
