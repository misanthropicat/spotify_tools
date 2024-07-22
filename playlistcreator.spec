# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
from PyInstaller.utils.hooks import collect_data_files

path = os.path.abspath(".")

a = Analysis(
    ['src\\main.py', 'src\\components.py', 'src\\playlist_creator.py', 'src\\utils.py'],
    pathex=[path],
    binaries=[],
    datas=[('.env', '.')],
    hiddenimports=[],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
splash = Splash(
    'src\\data\\splash_win.gif',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    splash,
    splash.binaries,
    name='playlistcreator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\data\\app_icon.ico'],
)
