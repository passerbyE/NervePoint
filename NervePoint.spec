# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

# 取得專案根目錄
spec_root = os.path.abspath(SPECPATH)

datas = [
    (os.path.join(spec_root, '.data'), '.data'),  # 包含資料夾
]

# 如果有 assets 資料夾，也包含進去
assets_path = os.path.join(spec_root, 'assets')
if os.path.exists(assets_path):
    datas.append((assets_path, 'assets'))

binaries = []
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'google.generativeai',
    'google.genai',
    'google.ai.generativelanguage',
    'google.api_core',
]

# 收集 PyQt6 所有模組
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 收集 google.generativeai 所有模組
tmp_ret = collect_all('google.generativeai')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    [os.path.join(spec_root, 'script', 'NervePoint.py')],
    pathex=[spec_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='NervePoint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = 不顯示終端視窗，True = 顯示（方便除錯）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'assets', 'app.ico') if os.path.exists(os.path.join(spec_root, 'assets', 'app.ico')) else None,
)
