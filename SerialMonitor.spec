# -*- mode: python -*-
import sys
import os
sys.path.append(os.getcwd())
import libs.utils as utils

block_cipher = None

a = Analysis(['src\serialMonitor.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=None,
             hiddenimports=['libs.LoggingUtils'],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SerialMonitor',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon=os.getcwd() + os.sep + 'res/Web2board.ico')
