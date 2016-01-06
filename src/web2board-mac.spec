# -*- mode: python -*-
import os
import sys

sys.path.append(os.getcwd())
import libs.utils as utils

block_cipher = None

pathEx = os.getcwd()

a = Analysis(['web2board.py'],
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
          console=False)

app = BUNDLE(exe,
             name='web2board.app',
             icon='res\web2board.icns',
             bundle_identifier=None,
             info_plist={
                 'CFBundleIconFile': 'res/web2board.icns',
                 'CFBundleURLTypes': [
                     {
                         'CFBundleURLName': 'bitbloq.bq.com',
                         'CFBundleURLSchemes': 'web2board'
                     }
                 ],
                 'PyOptions': {
                     'argv_emulation': True
                 }
             },
             )
