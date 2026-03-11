# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, copy_metadata, collect_all, collect_submodules

# Collect data files from packages
datas = []
datas += collect_data_files('reuse')
datas += collect_data_files('fosslight_util')
datas += copy_metadata('Jinja2')

# Collect chardet and binaryornot to fix mypyc module issues
datas_chardet, binaries_chardet, hiddenimports_chardet = collect_all('chardet')
datas += datas_chardet

datas_binaryornot, binaries_binaryornot, hiddenimports_binaryornot = collect_all('binaryornot')
datas += datas_binaryornot

# Add template file
datas += [('src/fosslight_prechecker/templates/default_template.jinja2', '.')]

# Add license files
datas += [('LICENSE', 'LICENSES')]
datas += [('LICENSES/LicenseRef-3rd_party_licenses.txt', 'LICENSES')]

# Collect binaries
binaries = []
binaries += binaries_chardet
binaries += binaries_binaryornot

# Collect hidden imports including all chardet submodules
hiddenimports = ['pkg_resources.extern']
hiddenimports += hiddenimports_chardet
hiddenimports += hiddenimports_binaryornot
hiddenimports += collect_submodules('chardet')
hiddenimports += collect_submodules('binaryornot')
hiddenimports += [
    'chardet.universaldetector',
    'chardet.detector',
    'chardet.pipeline',
    'chardet.pipeline.orchestrator',
]

a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
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
    a.binaries,
    a.datas,
    [],
    name='cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
