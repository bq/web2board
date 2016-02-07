# -*- mode: python -*-
import sys
import os

sys.path.append(os.getcwd())
from libs import utils
from libs.PathsManager import PathsManager

pathEx = os.getcwd()

a = Analysis([os.path.join(os.getcwd(), PathsManager.RES_PATH, 'sconsScript.py')],
             pathex=[pathEx],
             hiddenimports=['UserList', 'UserString', 'ConfigParser', 'json'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sconsScript',
          debug=False,
          strip=None,
          upx=True,
          console=True)
