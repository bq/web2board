# -*- mode: python -*-
import os
import sys
sys.path.append(os.getcwd())
import libs.utils as utils

block_cipher = None


a = Analysis(['serialMonitor.py'],
             pathex=[os.getcwd()],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='serialMonitor',
          debug=False,
          strip=None,
          upx=True,
          console=True )
