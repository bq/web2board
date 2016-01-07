# -*- mode: python -*-
import os
import sys

sys.path.append(os.getcwd())
import libs.utils as utils

block_cipher = None

a = Analysis(['serialMonitor.py'],
             pathex=[os.getcwd()],
             hiddenimports=['libs.LoggingUtils'],
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
          console=False,
          icon=os.getcwd() + os.sep + 'res/Web2board.ico')

app = BUNDLE(exe,
             name='SerialMonitor',
             icon='res\web2board.icns',
             bundle_identifier=None
             )
