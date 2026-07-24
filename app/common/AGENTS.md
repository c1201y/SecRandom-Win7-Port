# COMMON MODULES - SecRandom

**Domain:** Shared business logic across features
**Parent:** `app/`

---

## OVERVIEW

Common business logic modules used by the UI layer. Each feature domain (lottery, roll_call) has its own subdirectory with manager + utils + history pattern.

---

## STRUCTURE

```
common/
├── lottery/              # Lottery draw logic
│   ├── lottery_manager.py
│   └── lottery_utils.py
├── roll_call/            # Roll call (点名) logic
│   ├── roll_call_manager.py
│   └── roll_call_utils.py
├── fair_draw/            # Fair selection algorithms
│   └── avg_gap_protection.py
├── history/              # Draw history & weight tracking
│   ├── lottery_history.py
│   ├── roll_call_history.py
│   ├── weight_utils.py
│   └── file_utils.py
├── IPC_URL/              # C# IPC communication (Windows)
│   └── csharp_ipc_handler.py
├── data/                 # Data list management
├── display/              # Result display logic
├── extraction/           # Excel extraction utilities
├── camera_preview_backend/  # Camera integration
├── voice/                # TTS (text-to-speech)
├── music/                # Background music player
├── notification/         # System notifications
├── safety/               # Security features (password, USB, TOTP)
├── search/               # Settings search
├── shortcut/             # Global keyboard shortcuts
└── windows/              # Windows-specific helpers
```

---

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add lottery mode | `lottery/` | Manager handles draw logic, utils for pure functions |
| Add roll call mode | `roll_call/` | Same pattern as lottery |
| Modify fair algorithm | `fair_draw/` | Gap protection and weight logic |
| Read/write history | `history/` | JSON file operations, weight calculations |
| Windows .NET features | `IPC_URL/` | C# interop via pythonnet |
| Handle Excel import | `extraction/` | Excel parsing utilities |
| Camera integration | `camera_preview_backend/` | Device detection, preview workers |
| Voice announcements | `voice/` | Edge TTS, local TTS support |

---

## CONVENTIONS

### Domain Pattern
Each feature follows this structure:
```
feature_name/
├── __init__.py
├── feature_manager.py      # Main logic coordinator
├── feature_utils.py        # Pure helper functions
└── (optional) submodules/
```

### Manager Responsibilities
- Coordinate draw/selection process
- Handle state management
- Call history tracking
- Interface with UI layer

### Utils Responsibilities
- Pure functions (no side effects)
- Data transformations
- Calculations (weights, probabilities)
- Validation logic

### History Pattern
- Separate history module per feature
- JSON file storage in `data/history/`
- Weight tracking for fair selection

---

## ANTI-PATTERNS

### NEVER
- **Import UI components** into common/ - common should be UI-agnostic
- **Access settings directly** - Use `app.tools.settings_access`
- **Mix manager and utils** - Keep pure functions in utils

### ALWAYS
- **Add history entry** when draw completes
- **Use weight_utils** for fair selection calculations
- **Handle exceptions** in managers, not utils

---

## UNIQUE ASPECTS

### Fair Selection Algorithm
- `fair_draw/avg_gap_protection.py` - Core fairness logic
- `history/weight_utils.py` - Dynamic weight calculations
- Protects against over-selection using average gap threshold

### .NET Interop (Windows)
- `IPC_URL/csharp_ipc_handler.py` - Python ↔ C# communication
- Requires DLLs in `data/dlls/`
- Used for advanced Windows features (camera control, etc.)

### Data Flow
```
UI (view/) → Manager (common/*/manager.py) → Utils → History
```
