from __future__ import annotations

from typing import Any, Dict, Optional

from app.tools.settings_access import readme_settings_async, update_settings
from app.tools.settings_access import get_safe_font_size


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _get_overrides_map(settings_group: str) -> Dict[str, Any]:
    return _safe_dict(readme_settings_async(settings_group, "overrides", {}))


def get_list_specific_setting(
    base_settings_group: str,
    list_settings_group: str,
    list_name: Optional[str],
    key: str,
    default: Any = None,
) -> Any:
    if not list_name:
        return readme_settings_async(base_settings_group, key, default)

    overrides = _get_overrides_map(list_settings_group)
    list_overrides = _safe_dict(overrides.get(list_name))
    if key in list_overrides:
        return list_overrides.get(key)

    return readme_settings_async(base_settings_group, key, default)


def set_list_specific_setting(
    list_settings_group: str, list_name: str, key: str, value: Any
) -> None:
    if not list_name:
        return

    overrides = _get_overrides_map(list_settings_group)
    list_overrides = _safe_dict(overrides.get(list_name))
    list_overrides[key] = value
    overrides[list_name] = list_overrides
    update_settings(list_settings_group, "overrides", overrides)


def set_list_specific_setting_with_global_fallback(
    base_settings_group: str,
    list_settings_group: str,
    list_name: str,
    key: str,
    value: Any,
) -> None:
    if not list_name:
        return

    global_value = readme_settings_async(base_settings_group, key, None)

    overrides = _get_overrides_map(list_settings_group)
    list_overrides = _safe_dict(overrides.get(list_name))

    if value == global_value:
        if key in list_overrides:
            list_overrides.pop(key, None)
    else:
        list_overrides[key] = value

    if list_overrides:
        overrides[list_name] = list_overrides
    else:
        overrides.pop(list_name, None)

    update_settings(list_settings_group, "overrides", overrides)


def clear_list_specific_overrides(list_settings_group: str, list_name: str) -> None:
    if not list_name:
        return

    overrides = _get_overrides_map(list_settings_group)
    if list_name not in overrides:
        return
    overrides.pop(list_name, None)
    update_settings(list_settings_group, "overrides", overrides)


def get_safe_font_size_list_specific(
    base_settings_group: str,
    list_settings_group: str,
    list_name: Optional[str],
    key: str,
    default_size: int = 12,
) -> int:
    if not list_name:
        return get_safe_font_size(base_settings_group, key, default_size)

    value = get_list_specific_setting(
        base_settings_group,
        list_settings_group,
        list_name,
        key,
        default_size,
    )
    try:
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        elif isinstance(value, (int, float)):
            value = int(value)
        if value <= 0 or value > 200:
            return default_size
        return value
    except Exception:
        return default_size


def read_roll_call_setting(
    list_name: Optional[str], key: str, default: Any = None
) -> Any:
    return get_list_specific_setting(
        "roll_call_settings",
        "roll_call_list_specific_settings",
        list_name,
        key,
        default,
    )


def set_roll_call_setting_override(list_name: str, key: str, value: Any) -> None:
    set_list_specific_setting_with_global_fallback(
        "roll_call_settings",
        "roll_call_list_specific_settings",
        list_name,
        key,
        value,
    )


def read_quick_draw_setting(
    list_name: Optional[str], key: str, default: Any = None
) -> Any:
    return get_list_specific_setting(
        "quick_draw_settings",
        "quick_draw_list_specific_settings",
        list_name,
        key,
        default,
    )


def set_quick_draw_setting_override(list_name: str, key: str, value: Any) -> None:
    set_list_specific_setting_with_global_fallback(
        "quick_draw_settings",
        "quick_draw_list_specific_settings",
        list_name,
        key,
        value,
    )


def read_lottery_setting(
    list_name: Optional[str], key: str, default: Any = None
) -> Any:
    return get_list_specific_setting(
        "lottery_settings", "lottery_list_specific_settings", list_name, key, default
    )


def set_lottery_setting_override(list_name: str, key: str, value: Any) -> None:
    set_list_specific_setting_with_global_fallback(
        "lottery_settings",
        "lottery_list_specific_settings",
        list_name,
        key,
        value,
    )
