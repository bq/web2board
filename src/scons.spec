# -*- mode: python -*-

block_cipher = None
import libs.utils as utils

hidenInports = utils.findModulesForPyInstaller("SCons", ["*", "**/*"])
hidenInports += utils.findModulesForPyInstaller("platformio", ["*", "**/*"])
hidenInports += ["UserList", 'UserString', 'SCons', 'json', "SCons.compat"]

a = Analysis(['scons.py'],
             pathex=['C:\\Users\\jorgarira\\SoftwareProjects\\web2board\\src'],
             binaries=None,
             datas=None,
             hiddenimports=hidenInports,
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

a.datas += utils.findFilesForPyInstaller("platformio", ["*", "**/*"])
a.datas += utils.findFilesForPyInstaller("sconsBase", ["*", "**/*"])

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
