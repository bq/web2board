# -*- mode: python -*-
import os
import sys
import zipfile

sys.path.append(os.getcwd())
import libs.utils as utils
from libs.PathsManager import PathsManager
from Scripts import TestRunner

hidden_imports = ['libs.LoggingUtils', 'libs.WSCommunication.Hubs', 'UserList', 'UserString', 'ConfigParser']
hidden_imports.extend(TestRunner.get_module_string('Test/**/test*.py'))
print hidden_imports

print os.getcwd()
block_cipher = None

a = Analysis(['src' + os.sep + 'web2board.py'],
             pathex=[os.getcwd()],
             hiddenimports=hidden_imports,
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

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
