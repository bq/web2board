# -*- mode: python -*-
import os
import sys
import os

sys.path.append(os.getcwd())
import libs.utils as utils
from libs.PathsManager import PathsManager

pathEx = os.getcwd()
block_cipher = None

a = Analysis(["src" + os.sep + 'web2board.py'],
             pathex=[pathEx],
             binaries=None,
             datas=None,
             hiddenimports=['libs.LoggingUtils', 'libs.WSCommunication.Hubs', 'UserList', 'UserString', 'ConfigParser'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += utils.find_files_for_pyinstaller("platformio", ["*", "**/*"])
a.datas += utils.find_files_for_pyinstaller("res", ["*", "**/*"])
a.datas += utils.find_files_for_pyinstaller("Test/resources", ["*", "**/*"])

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
