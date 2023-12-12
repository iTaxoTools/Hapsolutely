# -*- mode: python ; coding: utf-8 -*-

from os import environ

NAME = environ.get('APP_NAME', None)
ICON = environ.get('APP_ICON_ICNS', None)
SCRIPT = environ.get('APP_SCRIPT', None)
IDENTIFIER = environ.get('APP_IDENTIFIER', None)
ENTITLEMENTS = environ.get('APP_ENTITLEMENTS', None)

# Code must be signed manually after building
CODESIGN_IDENTITY = None


block_cipher = None

a = Analysis([SCRIPT],
             pathex=[],
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
          [],
          exclude_binaries=True,
          name=NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch='universal2',
          codesign_identity=CODESIGN_IDENTITY,
          entitlements_file=ENTITLEMENTS,
          icon=ICON)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=NAME)
app = BUNDLE(coll,
             name=f'{NAME}.app',
             icon=ICON,
             bundle_identifier=IDENTIFIER)
