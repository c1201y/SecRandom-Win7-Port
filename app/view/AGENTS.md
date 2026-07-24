# VIEW LAYER - SecRandom

**Domain:** UI components and windows
**Parent:** `app/`

---

## OVERVIEW

PySide6-based UI layer using PySide6-Fluent-Widgets (Microsoft Fluent Design). Organized by window type and feature area.

---

## STRUCTURE

```
view/
├── main/                      # Main window pages
│   ├── window.py             # Main window container
│   ├── roll_call.py          # Roll call (点名) page
│   ├── lottery.py            # Lottery (抽奖) page
│   ├── quick_draw_animation.py
│   └── camera_preview.py     # Camera preview widget
├── settings/                  # Settings window
│   ├── settings.py           # Settings container
│   ├── basic_settings.py
│   ├── extraction_settings/   # Draw-specific settings
│   ├── voice_settings/
│   ├── notification_settings/
│   ├── list_management/       # Student/prize list editors
│   ├── history/               # History viewers
│   ├── theme_management/      # Theme customization
│   └── more_settings/         # Advanced settings
├── another_window/            # Dialogs and secondary windows
│   ├── student/               # Student import dialogs
│   ├── prize/                 # Prize import dialogs
│   ├── security/              # Password/TOTP dialogs
│   ├── usb/                   # USB binding dialogs
│   └── ...
├── floating_window/           # Floating quick-draw window
│   └── levitation.py
├── guide/                     # First-run guide
│   └── pages.py
├── tray/                      # System tray icon
│   └── tray.py
└── components/                # Shared UI components
    ├── checkable_combo_box.py
    └── center_flow_layout.py
```

---

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Modify main UI | `main/` | roll_call.py, lottery.py for draw pages |
| Add setting | `settings/` | Create page in appropriate subdir, register in settings.py |
| Add dialog | `another_window/` | Create folder for feature area |
| Modify floating window | `floating_window/` | levitation.py for quick draw |
| Add tray feature | `tray/` | tray.py for system tray menu |
| Reuse component | `components/` | Shared widgets used across windows |

---

## CONVENTIONS

### Widget Pattern
```python
class SomeSettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        # Setup layout and widgets
        pass

    def _load_settings(self):
        # Load from settings_access
        pass
```

### Fluent Design
- Use `qfluentwidgets` components (CardWidget, SettingCard, etc.)
- Follow light/dark theme automatically
- Use `app.tools.theme_loader` for custom themes

### Settings Page Structure
```python
# In settings.py, register new page:
self.addSubInterface(
    page_instance,
    icon,
    self.tr("Page Title"),
    NavigationItemPosition.SCROLL
)
```

### Dialog Pattern
- Inherit from `Dialog` or `MessageBox` from qfluentwidgets
- Modal dialogs for data entry
- Non-modal for informational windows

---

## ANTI-PATTERNS

### NEVER
- **Import common/ directly** - Go through managers
- **Access config files directly** - Use settings_access
- **Hardcode strings** - Use Language modules for i18n
- **Block main thread** - Use workers for long operations

### ALWAYS
- **Wrap in try/except** for user-facing operations
- **Update status bar** for long operations
- **Validate input** before closing dialogs
- **Refresh parent** after dialog closes with changes

---

## UNIQUE ASPECTS

### Fluent Widgets
- Uses `PySide6-Fluent-Widgets` library (not stock Qt)
- Custom theme support via `app/tools/theme_loader`
- Card-based settings layout

### Window Management
- Central `WindowManager` in `app/core/` controls all windows
- Single instance enforcement
- URL protocol handling for deep links

### i18n Integration
- All UI text via `self.tr()` (Qt translation)
- Source strings in `app/Language/modules/`
- Loaded at runtime based on settings

### Page Building
- `app/page_building/` provides templates
- `main_window_page.py`, `settings_window_page.py` - base classes
- Consistent styling across windows
