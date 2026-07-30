# PROJECT KNOWLEDGE BASE - SecRandom

**Generated:** 2026-07-30
**Project:** SecRandom - 公平随机抽取系统 (Fair Random Selection System)
**Stack:** Python 3.8.10 + PySide2 + PySide2-Fluent-Widgets
**Win7:** ✅ 已适配 Windows 7 (改动见下文 Win7 Port 章节)
**License:** GPLv3
**Language:** 中文回复
**Comments:** 中文注释

---

## SESSION SUMMARY (2026-07-30)

### Fixes Applied
| # | Issue | Root Cause | Fix | Files |
|---|-------|-----------|-----|-------|
| 1 | 引导页深色模式白底 | GuideWindow 未监听 `qconfig.themeChanged` | 连接 themeChanged 信号，`_apply_current_theme` 设置窗口/底栏 background-color | `app/view/guide/guide_window.py` |
| 2 | 设置窗口关闭后泄漏 800MB+ | `closeEvent` 执行 `event.ignore(); hide()`，窗口及所有子页面滞留在内存 | `closeEvent` 改为 `event.accept(); self.deleteLater()`，断开全局 SettingsSignals 引用 | `app/view/settings/settings.py` |
| 3 | WindowManager 持有已关闭窗口引用 | `_window_instances` dict 条目未清理 | SettingsWindow 新增 `windowClosed` 信号，WindowManager 连接并清空引用 | `app/core/window_manager.py` |
| 4 | 引导页内存泄漏 | `WA_DeleteOnClose` 未设置，themeChanged 未断开 | 设置 `WA_DeleteOnClose`，`closeEvent` 中断开 themeChanged | `app/view/guide/guide_window.py` |
| 5 | PyInstaller 构建后 data/ 目录不全 | spec 后处理用 `if not target.exists()` 跳过已存在目录，导致字体/assets 缺失 | 改为先 `rmtree` 再 `copytree`，确保增量构建也覆盖完整 | `Secrandom.spec` |
| 6 | `build_pyinstaller.py` 编码崩溃 | `capture_output=True` + `encoding="utf-8"` 遇非 UTF-8 字节抛出 `UnicodeDecodeError` | 直接调用 PyInstaller 命令行绕过（脚本待修复） | `build_pyinstaller.py` |

### Verification
- ✅ 三项修改（GuideWindow、SettingsWindow、WindowManager）均通过导入测试
- ✅ 字体加载（HarmonyOS_Sans_SC_Medium.ttf、FluentSystemIcons-Filled.ttf）在打包版中正常工作
- ✅ 数据文件完整性确认：`data/assets/`、`data/font/`、`data/dlls/` 均正确包含
- ✅ 打包版从运行到 UI 显示无报错

### Known Remaining Issues
| Issue | Impact | Workaround |
|-------|--------|------------|
| pythonnet 不可用（未安装 `clr`） | C# IPC 回退 | Expected on dev machines without .NET SDK |
| TTS 初始化失败 `(-2147200966, ...)` | 语音播报不可用 | Expected on this machine (Win10) |
| `build_pyinstaller.py` 编码问题 | 脚本不能直接运行 | 手动 `python -m PyInstaller Secrandom.spec --clean --noconfirm` |

---

## OVERVIEW

Desktop GUI application for educational random selection with "fair" algorithms. Uses dynamic weighting to ensure all participants get equal chances over time. Built with PySide2 (Qt5) using Microsoft's Fluent Design System.

---

## WIN7 PORT (Python 3.8.10)

### Changes Made

#### pyproject.toml
- `requires-python` changed from `>=3.9,<3.11` to `>=3.8,<3.11`
- Dependency version pins for Python 3.8 compatibility:

| Package | Change | Reason |
|---------|--------|--------|
| `numpy` | `<1.25` | numpy 1.25+ dropped cp38 |
| `aiohttp` | `<3.10` | aiohttp 3.10+ dropped cp38 |
| `pillow` | `<11` | pillow 11+ dropped cp38 |
| `pythonnet` | `<4.0.0` | Python 3.8 会自动选最新兼容版本（如 3.0.5） |
| `sentry-sdk` | `<2.0` | sentry-sdk 2.0+ dropped cp38 |

#### Known Limitations (gracefully handled)
| Feature | Issue | Fallback |
|---------|-------|----------|
| .NET IPC (C#) | 用户已安装 .NET 8.0 Runtime | 正常工作 |
| Win10 Toast | `win10toast` uses Win10 API | Falls back to `plyer` notification |
| QWebEngineView | Chromium may not work on Win7 | Falls back to `QTextBrowser` |
| user32.SetWindowBand | Win11+ only | Wrapped in try/except (dead code) |

#### Third-party package versions needed for Python 3.8
When using pip to install, pin these transitive dependencies:
- `urllib3>=1.26,<2.0`
- `idna>=2.5,<3`
- `charset-normalizer>=2,<3`
- `requests>=2.25,<2.32`
- `yarl<1.10`
- `frozenlist<1.5`
- `multidict<6`
- `comtypes<1.4`
- `soundfile<0.12`
- `qrcode<7.4`
- `aiosignal<1.4`
- `posthog<3.0`

Recommended install command:
```
pip install "urllib3>=1.26,<2.0" "idna>=2.5,<3" "charset-normalizer>=2,<3" "requests>=2.25,<2.32" "yarl<1.10" "frozenlist<1.5" "multidict<6" "comtypes<1.4" "soundfile<0.12" "qrcode<7.4" "aiosignal<1.4" "posthog>=1.0,<3.0"
```

#### Regenerating uv.lock
After changing `requires-python`, the existing `uv.lock` is stale. Delete it and regenerate:
```bash
uv lock --python-version 3.8
```
Or if you don't use uv, delete `uv.lock` and use `pip install -e .` with Python 3.8.

---

## STRUCTURE

```
.
├── app/                    # Main application package
│   ├── common/            # Shared business logic (lottery, roll_call, history, etc.)
│   ├── core/              # Application core (window_manager, app_init, fonts)
│   ├── view/              # UI layer (main/, settings/, another_window/)
│   ├── tools/             # Utilities (config, paths, settings, themes)
│   ├── Language/          # i18n system (modules/, obtain_language.py)
│   └── page_building/     # Window/page construction utilities
├── config/                # Runtime configs (settings.json, secrets.json)
├── data/                  # Runtime data (dlls/, font/, history/, list/)
├── logs/                  # Application logs
├── resources/             # Static assets (icons, screenshots, docs)
├── scripts/               # Utility scripts (language import/export)
├── vendors/               # Vendored deps (pythonnet-stub-generator)
├── main.py                # Entry point
└── pyproject.toml         # Project config
```

---

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add lottery feature | `app/common/lottery/` | lottery_manager.py, lottery_utils.py |
| Add roll call feature | `app/common/roll_call/` | roll_call_manager.py, roll_call_utils.py |
| Modify UI windows | `app/view/` | main/, settings/, another_window/ |
| Change core behavior | `app/core/` | window_manager.py, app_init.py |
| Add settings option | `app/tools/settings_*.py` | Accessors and defaults |
| Update translations | `app/Language/modules/` | Per-feature translation modules |
| Build/packaging | Root build_*.py | Nuitka + PyInstaller scripts |
| .NET interop | `app/common/IPC_URL/` | C# IPC handler for Windows features |

---

## CODE MAP

### Entry Points
- `main.py` - Application bootstrap (sentry, posthog, window manager)

### Core Modules
| Symbol | Type | File | Role |
|--------|------|------|------|
| WindowManager | Class | `app/core/window_manager.py` | Central window lifecycle |
| AppInitializer | Class | `app/core/app_init.py` | App startup logic |
| configure_dpi_scale | Function | `app/core/font_manager.py` | HiDPI handling |

### Common Domains
| Domain | Manager | Utils | History |
|--------|---------|-------|---------|
| Lottery | `lottery_manager.py` | `lottery_utils.py` | `lottery_history.py` |
| Roll Call | `roll_call_manager.py` | `roll_call_utils.py` | `roll_call_history.py` |
| Fair Draw | `fair_draw/` | - | `weight_utils.py` |

---

## CONVENTIONS

### Code Style
- **Ruff** for linting (configured in pyproject.toml)
- **Pre-commit** hooks enabled (.pre-commit-config.yaml)
- Ignored rules: F405, E722, E501, B012, F403, C901, B007, F841, C416, C414, E402

### Imports
- Absolute imports preferred: `from app.tools.config import ...`
- Star imports used (F403 ignored): `from app.tools.variable import *`

### Architecture
- **MVP-like pattern:** view/ (UI) → common/ (logic) → tools/ (infra)
- Managers handle domain logic (lottery_manager.py, etc.)
- Utils for pure functions (lottery_utils.py, etc.)
- Settings split: `_access.py` (read), `_default.py` (defaults), `_default_storage.py` (schema)

### Naming
- Files: snake_case.py
- Classes: PascalCase
- Functions/vars: snake_case
- UI files: descriptive (roll_call.py, lottery.py)

---

## ANTI-PATTERNS (THIS PROJECT)

### DO NOT
- **Use PyInstaller directly** - Use Nuitka for production builds (configured in build_nuitka.py)
- **Commit uv.lock changes unnecessarily** - Lock file is tracked but regenerate only when deps change
- **Modify vendors/ without documenting** - Vendored code must keep original LICENSE
- **Use Python 3.13.6+** - Strictly pinned to 3.13.5 in pyproject.toml

### NEVER
- **Import from tests/** - No test directory exists (tests are minimal)
- **Use relative imports** - Always use absolute `from app.xxx import ...`
- **Commit .venv/** - Already gitignored but worth reinforcing

### ALWAYS
- **Add translations** - Update `app/Language/modules/` when adding UI text
- **Use settings accessors** - Read via `app.tools.settings_access`, defaults in `settings_default`
- **Handle platform differences** - Windows (pywin32) vs Linux (pulsectl) deps marked in pyproject.toml

---

## UNIQUE STYLES

### .NET Interop
Heavy use of pythonnet for Windows features:
- `app/common/IPC_URL/csharp_ipc_handler.py` - C# IPC communication
- `data/dlls/` - .NET DLLs (protobuf, Newtonsoft.Json, etc.)
- `vendors/pythonnet-stub-generator/` - Modified stub generator

### Weight Algorithm
Fair selection uses dynamic weighting:
- `app/common/fair_draw/avg_gap_protection.py` - Gap protection logic
- `app/common/history/weight_utils.py` - Weight calculation
- Uses "average difference protection" to ensure fairness over time

### UI System
- **Fluent Design:** PySide6-Fluent-Widgets for modern Windows look
- **Theme support:** `app/tools/theme_loader.py`, `app/view/settings/theme_management/`
- **Floating window:** `app/view/floating_window/levitation.py`

### i18n Pattern
Translation system uses module-per-feature:
- `app/Language/modules/guide.py` - Guide translations
- `app/Language/modules/basic_settings.py` - Settings translations
- Loaded via `app/Language/obtain_language.py`

---

## COMMANDS

```bash
# Development (use uv)
uv sync                          # Install deps
uv run python main.py           # Run app

# Linting
ruff check .                     # Check
ruff check --fix .               # Auto-fix

# Build (choose one)
python build_nuitka.py          # Production build (Nuitka)
python build_pyinstaller.py     # Debug build (PyInstaller)

# Scripts
python scripts/import_crowdin_language.py  # Import translations
python scripts/export_zh_cn_language.py    # Export source strings
```

---

## NOTES

### Platform Differences
- **Windows:** Full features (UI access, USB binding, WMI, pycaw audio)
- **Linux:** Limited features (no pywin32, pulsectl for audio)
- **Both:** Core random selection works identically

### Configuration Files
- `config/settings.json` - User preferences
- `config/secrets.json` - Encrypted secrets
- `config/behind_scenes.json` - Hidden settings

### Data Directories
- `data/list/` - Student/prize lists (Excel files)
- `data/history/` - Draw history (JSON)
- `data/font/` - Custom fonts
- `data/dlls/` - .NET assemblies (Windows only)

### Gotchas
- Python version is **EXACTLY** 3.13.5 - don't upgrade
- Entry point is `main.py` at root, not a console script
- Lock file `uv.lock` is tracked (unusual but intentional)
- .NET DLLs required for Windows features (camera, USB binding)
- Sentry + PostHog telemetry initialized in main.py

### Sentry 日志级别与上报行为

Sentry 通过 `LoguruIntegration` 接入，配置在 `main.py:62-66`：
- `event_level=LoggingLevels.ERROR.value` — 只有 ERROR 级别以上才触发 Sentry 事件
- `before_send` 过滤器在 `app/tools/config.py:81-137`，会丢弃没有堆栈信息的 ERROR 事件

**关键规则：选择正确的日志级别来控制是否上报 Sentry**

| 日志方法 | 级别 | 有堆栈? | Sentry 行为 | 适用场景 |
|----------|------|---------|-------------|----------|
| `logger.exception()` | ERROR | ✅ 有 | **上报** | 真正的 bug，需要修复 |
| `logger.error()` | ERROR | ❌ 无 | **不上报**（被 before_send 过滤） | 预期错误，不需要上报但需要记录 |
| `logger.warning()` | WARNING | ❌ 无 | **不上报**（低于 event_level） | 预期的降级状态 |

**实际应用：**
- 网络超时、连接失败等**预期故障** → 用 `logger.warning()` 或 `logger.error()`
- 代码逻辑错误、未处理异常等**真正 bug** → 用 `logger.exception()`
- `before_send` 中还可以按异常类型过滤（如网络异常类型），作为额外防御层

### Vendored Dependencies
- `vendors/pythonnet-stub-generator/` - MIT licensed, modified for .NET 9.0
- Keep original LICENSE.md when updating

---

## SUBDIRECTORY GUIDES

| Directory | Guide |
|-----------|-------|
| `app/common/` | See `app/common/AGENTS.md` |
| `app/view/` | See `app/view/AGENTS.md` |
| `app/core/` | See `app/core/AGENTS.md` |
