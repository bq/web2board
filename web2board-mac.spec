# -*- mode: python -*-
import os
import sys
import os

sys.path.append(os.getcwd())
import libs.utils as utils
from libs.PathsManager import PathsManager

pathEx = os.getcwd()

a = Analysis([PathsManager.EXECUTABLE_PATH + os.sep + 'web2board.py'],
             pathex=[pathEx],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("res", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("Test/resources", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='web2board',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon=PathsManager.RES_ICO_PATH)

app = BUNDLE(exe,
             name='web2board.app',
             icon= 'res' + os.sep + 'web2board.icns',
             bundle_identifier=None,
             info_plist={
                 'CFBundleURLTypes': [
                     {
                         'CFBundleURLName': 'bitbloq.bq.com',
                         'CFBundleURLSchemes': 'web2board'
                     }
                 ],
                 'PyOptions': {
                     'argv_emulation': True
                 }
             }, )
