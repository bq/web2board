# -*- mode: python -*-
import sys
sys.path.append(os.getcwd())
import libs.utils as utils
block_cipher = None

a = Analysis(['test.py'],
             pathex=['C:\\SoftwareProjects\\web2board\\src'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])

print a.datas
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='test',
          debug=False,
          strip=None,
          upx=True,
          console=True )
