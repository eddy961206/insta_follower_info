# -*- mode: python ; coding: utf-8 -*-

my_program_name = "린치핀 인스타 팔로워 추출 프로그램 v1.1"


a = Analysis(
    ["insta_follower_gui.py"],
    pathex=[],
    binaries=[],
    datas=[('build/assets/frame0/*', 'build/assets/frame0'), ('instagram.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['_pycache_', 'venv', '.git', '.gitignore', '.cursorignore','test', '인스타_설정정보.ini'],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=my_program_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='instagram.ico'
    )
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=my_program_name,
)
