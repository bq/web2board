# -*- mode: python -*-
import pprint
import sys
import os
import zipfile

from libs.PathsManager import PathsManager

sys.path.append(os.getcwd())
from libs import utils

block_cipher = None

zipData = utils.findFiles("scons", ["*", "**/*"])
with zipfile.ZipFile(PathsManager.RES_SCONS_ZIP_PATH, "w") as z:
    for zipFilePath in zipData:
        z.write(zipFilePath)

a = Analysis(['src/scons.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=None,
             hiddenimports=['UserList', 'UserString', 'ConfigParser'],
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
a.datas += utils.findFilesForPyInstaller("Test/resources", ["*", "**/*"])

# a.datas += utils.findFilesForPyInstaller("scons", ["*", "**/*"])

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='scons',
          debug=False,
          strip=None,
          upx=True,
          console=True)
