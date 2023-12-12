# -*- mode: python ; coding: utf-8 -*-

from os import environ

NAME = environ.get('APP_NAME', None)
FILENAME = environ.get('APP_FILENAME', None)
ICON = environ.get('APP_ICON_ICO', None)
SCRIPT = environ.get('APP_SCRIPT', None)


block_cipher = None

# Could also use pyinstaller's Entrypoint()
a = Analysis([SCRIPT],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=FILENAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon=ICON)
