"""PyInstaller spec leveraging shared packaging utilities."""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

from packaging_utils import (
    ADDITIONAL_HIDDEN_IMPORTS,
    collect_data_includes,
    collect_language_modules,
    collect_view_modules,
    normalize_hidden_imports,
)

block_cipher = None

base_datas = [(str(item.source), item.target) for item in collect_data_includes()]

try:
    qfluentwidgets_datas = collect_data_files("qfluentwidgets")
except Exception as exc:
    print(f"Warning: unable to collect qfluentwidgets data: {exc}")
    qfluentwidgets_datas = []

# 收集numpy的数据文件和动态库
try:
    numpy_datas = collect_data_files("numpy")
    numpy_libs = collect_dynamic_libs("numpy")
except Exception as exc:
    print(f"Warning: unable to collect numpy data: {exc}")
    numpy_datas = []
    numpy_libs = []

all_datas = base_datas + qfluentwidgets_datas + numpy_datas

language_hiddenimports = collect_language_modules()
view_hiddenimports = collect_view_modules()

# 收集numpy的所有子模块
try:
    numpy_hiddenimports = collect_submodules("numpy")
except Exception as exc:
    print(f"Warning: unable to collect numpy submodules: {exc}")
    numpy_hiddenimports = []

all_hiddenimports = normalize_hidden_imports(
    language_hiddenimports + view_hiddenimports + ADDITIONAL_HIDDEN_IMPORTS + numpy_hiddenimports
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=numpy_libs,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

import sys

# 根据平台设置不同的EXE名称
exename = "SecRandom"
if sys.platform == "linux":
    # 在Linux上，EXE会创建一个无扩展名的文件，为避免与COLLECT目录冲突，添加.bin扩展名
    exename = "SecRandom.bin"

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=exename,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="resources/secrandom-icon-paper.ico",
)

# 创建目录模式输出（onedir模式）
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SecRandom",
)
