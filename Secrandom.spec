"""PyInstaller spec leveraging shared packaging utilities."""

import shutil
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

from packaging_utils import (
    ADDITIONAL_HIDDEN_IMPORTS,
    PROJECT_ROOT,
    DATA_DIR,
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

all_datas = base_datas + qfluentwidgets_datas

language_hiddenimports = collect_language_modules()
view_hiddenimports = collect_view_modules()

all_hiddenimports = normalize_hidden_imports(
    language_hiddenimports + view_hiddenimports + ADDITIONAL_HIDDEN_IMPORTS
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SecRandom",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="data\\assets\\icon\\secrandom-icon-paper.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SecRandom",
)

# =====================================================
# 后处理：将 data 目录（静态资源）复制到 exe 同级目录
# 应用运行时从 sys.executable.parent 读取数据文件
# =====================================================
DIST_DIR = Path(SPEC).parent / "dist" / "SecRandom"
for item in [DATA_DIR]:
    target = DIST_DIR / item.name
    if not target.exists():
        print(f"Copying {item} -> {target}")
        shutil.copytree(item, target, symlinks=False, dirs_exist_ok=True)
