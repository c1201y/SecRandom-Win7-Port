# CORE MODULES - SecRandom

**Domain:** Application foundation and lifecycle
**Parent:** `app/`

---

## OVERVIEW

Core application infrastructure: window management, initialization, fonts, single-instance enforcement, and URL handling.

---

## STRUCTURE

```
core/
├── window_manager.py          # Central window coordinator (~34KB)
│   # Manages all windows, navigation, lifecycle
├── app_init.py               # Application initialization
│   # Startup sequence, draw count calculation
├── font_manager.py           # Font and DPI management
│   # HiDPI scaling, custom font loading
├── single_instance.py        # Single instance enforcement
│   # Socket-based locking, IPC for second instance
├── url_handler_setup.py      # URL protocol registration
│   # Custom URL scheme handler
├── cs_ipc_handler_setup.py   # C# IPC setup
│   # .NET interop initialization
└── utils.py                  # Core utilities
```

---

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add window type | `window_manager.py` | Register in WindowManager class |
| Modify startup | `app_init.py` | AppInitializer class |
| Fix HiDPI issues | `font_manager.py` | configure_dpi_scale() |
| Change single-instance | `single_instance.py` | Socket/port locking |
| Add URL handler | `url_handler_setup.py` | Protocol registration |
| .NET interop init | `cs_ipc_handler_setup.py` | C# bridge setup |

---

## KEY SYMBOLS

| Symbol | File | Purpose |
|--------|------|---------|
| WindowManager | window_manager.py | Central window lifecycle manager |
| AppInitializer | app_init.py | Application startup coordinator |
| configure_dpi_scale | font_manager.py | HiDPI and font setup |
| check_single_instance | single_instance.py | Prevent multiple app instances |
| create_url_handler | url_handler_setup.py | URL protocol handler |

---

## CONVENTIONS

### Window Registration
```python
# In window_manager.py, add to __init__ or create method
self.some_window = SomeWindow()
self.some_window.closed.connect(self._on_window_closed)
```

### Startup Sequence
1. Single instance check
2. Sentry/PostHog init
3. Font/DPI configuration
4. WindowManager creation
5. Main window show

### URL Handling
- Custom scheme: `secrandom://`
- Handled in `url_handler_setup.py`
- Security verification in `app/common/IPC_URL/security_verifier.py`

---

## ANTI-PATTERNS

### NEVER
- **Create windows outside WindowManager** - Always use WM
- **Skip single instance check** - Required for data integrity
- **Import view/ from core/** - Core is below view in hierarchy

### ALWAYS
- **Connect closed signal** for cleanup
- **Log startup errors** via logger before UI ready
- **Handle platform differences** (Windows vs Linux)

---

## UNIQUE ASPECTS

### WindowManager Complexity
- 34KB file - handles all window coordination
- Manages navigation, z-order, and cleanup
- Coordinates between main/settings/secondary windows

### Single Instance Strategy
- Socket-based on Linux
- Named mutex on Windows
- Sends URL to existing instance

### Font Management
- Custom font loading from `data/font/`
- HiDPI awareness for 4K displays
- Qt font database registration

### .NET Integration
- Initializes pythonnet runtime
- Loads assemblies from `data/dlls/`
- Required for Windows-specific features
