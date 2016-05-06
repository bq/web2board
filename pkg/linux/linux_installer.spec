# -*- mode: python -*-

block_cipher = None

a = Analysis(['linux_installer.py'],
             pathex=['../../src'],
             binaries=None,
             datas=[("web2boar.deb", ".")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='linux_installer',
          debug=False,
          strip=False,
          upx=True,
          console=True)
