# -*- mode: python -*-
import os
import sys
import zipfile

sys.path.append(os.getcwd())
import libs.utils as utils
from libs.PathsManager import PathsManager

block_cipher = None
zipData = utils.findFiles("scons", ["*", "**/*"])
zipData = utils.findFiles("scons", ["*", "**/*"])
with zipfile.ZipFile(PathsManager.RES_SCONS_ZIP_PATH, "w") as z:
    for zipFilePath in zipData:
        z.write(zipFilePath)

a = Analysis(['src/web2board.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=None,
             hiddenimports=['libs.LoggingUtils', 'libs.WSCommunication.Hubs'],
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
a.datas += utils.findFilesForPyInstaller(".", ["scons.exe"])
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='web2board',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=os.getcwd() + os.sep + 'res/Web2board.ico')
