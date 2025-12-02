# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from plotly (includes plotly.min.js and other resources)
plotly_datas = collect_data_files('plotly')

# Collect data files from endaq (which also uses plotly for plotting)
endaq_datas = collect_data_files('endaq')

# Combine all data files
all_datas = plotly_datas + endaq_datas

# Collect all submodules to ensure everything is included
hidden_imports = collect_submodules('plotly') + collect_submodules('endaq')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WE-DAVIS',
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
    icon='resources\\icons\\app_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WE-DAVIS',
)
