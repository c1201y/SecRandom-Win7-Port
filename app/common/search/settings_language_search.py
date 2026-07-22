from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import importlib

from app.Language.obtain_language import get_content_name_async

try:
    from pypinyin import Style, lazy_pinyin
except Exception:
    Style = None
    lazy_pinyin = None


def _compact_text(text: str) -> str:
    s = str(text or "").lower()
    out = []
    for ch in s:
        if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff"):
            out.append(ch)
    return "".join(out)


def _to_pinyin(text: str) -> str:
    if lazy_pinyin is None or Style is None:
        return ""
    parts = lazy_pinyin(str(text or ""), style=Style.NORMAL, errors=lambda x: [x])
    return _compact_text("".join(parts))


def _to_pinyin_initials(text: str) -> str:
    if lazy_pinyin is None or Style is None:
        return ""
    parts = lazy_pinyin(str(text or ""), style=Style.FIRST_LETTER, errors=lambda x: [x])
    return _compact_text("".join(parts))


def _subsequence_positions(needle: str, haystack: str) -> Optional[List[int]]:
    n = str(needle or "")
    h = str(haystack or "")
    if not n or not h:
        return None
    pos = []
    j = 0
    for i, ch in enumerate(h):
        if j < len(n) and ch == n[j]:
            pos.append(i)
            j += 1
            if j >= len(n):
                return pos
    return None


def _score_fuzzy_match(query: str, target: str) -> int:
    q = str(query or "")
    t = str(target or "")
    if not q or not t:
        return 0

    if q == t:
        return 4000
    if t.startswith(q):
        return 3000 - max(0, len(t) - len(q))
    if q in t:
        return 2000 + min(40, t.count(q)) * 5

    pos = _subsequence_positions(q, t)
    if not pos:
        return 0

    span = pos[-1] - pos[0] + 1
    gaps = max(0, span - len(q))
    score = 1000 - gaps
    if score <= 0:
        return 1
    return score


def get_default_settings_route_map() -> Dict[str, Dict[str, Any]]:
    return {
        "basic_settings": {"page_route": "settings_basic"},
        "list_management": {"page_route": "settings_list", "pivot": "list_management"},
        "roll_call_list": {"page_route": "settings_list", "pivot": "list_management"},
        "lottery_list": {"page_route": "settings_list", "pivot": "list_management"},
        "roll_call_table": {"page_route": "settings_list", "pivot": "roll_call_table"},
        "lottery_table": {"page_route": "settings_list", "pivot": "lottery_table"},
        "extraction_settings": {
            "page_route": "settings_extraction",
            "pivot": "roll_call_settings",
        },
        "roll_call_settings": {
            "page_route": "settings_extraction",
            "pivot": "roll_call_settings",
        },
        "quick_draw_settings": {
            "page_route": "settings_extraction",
            "pivot": "quick_draw_settings",
        },
        "lottery_settings": {
            "page_route": "settings_extraction",
            "pivot": "lottery_settings",
        },
        "face_detector_settings": {
            "page_route": "settings_extraction",
            "pivot": "face_detector_settings",
        },
        "floating_window_management": {"page_route": "settings_floating"},
        "notification_settings": {
            "page_route": "settings_notification",
            "pivot": "roll_call_notification_settings",
        },
        "roll_call_notification_settings": {
            "page_route": "settings_notification",
            "pivot": "roll_call_notification_settings",
        },
        "quick_draw_notification_settings": {
            "page_route": "settings_notification",
            "pivot": "quick_draw_notification_settings",
        },
        "lottery_notification_settings": {
            "page_route": "settings_notification",
            "pivot": "lottery_notification_settings",
        },
        "safety_settings": {"page_route": "settings_safety"},
        "basic_safety_settings": {"page_route": "settings_safety"},
        "linkage_settings": {"page_route": "settings_linkage"},
        "voice_settings": {
            "page_route": "settings_voice",
            "pivot": "basic_voice_settings",
        },
        "basic_voice_settings": {
            "page_route": "settings_voice",
            "pivot": "basic_voice_settings",
        },
        "specific_announcements": {
            "page_route": "settings_voice",
            "pivot": "specific_announcements",
        },
        "theme_management": {"page_route": "settings_theme"},
        "history": {"page_route": "settings_history", "pivot": "history_management"},
        "history_management": {
            "page_route": "settings_history",
            "pivot": "history_management",
        },
        "roll_call_history_table": {
            "page_route": "settings_history",
            "pivot": "roll_call_history_table",
        },
        "lottery_history_table": {
            "page_route": "settings_history",
            "pivot": "lottery_history_table",
        },
        "more_settings": {"page_route": "settings_more", "pivot": "fair_draw"},
        "fair_draw_settings": {"page_route": "settings_more", "pivot": "fair_draw"},
        "shortcut_settings": {
            "page_route": "settings_more",
            "pivot": "shortcut_settings",
        },
        "music_settings": {"page_route": "settings_more", "pivot": "music_settings"},
        "page_management": {"page_route": "settings_more", "pivot": "page_management"},
        "sidebar_tray_management": {
            "page_route": "settings_more",
            "pivot": "sidebar_tray_management",
        },
        "sidebar_management_window": {
            "page_route": "settings_more",
            "pivot": "sidebar_tray_management",
        },
        "tray_management": {
            "page_route": "settings_more",
            "pivot": "sidebar_tray_management",
        },
        "behind_scenes_settings": {
            "page_route": "settings_more",
            "pivot": "behind_scenes_settings",
        },
        "update": {"page_route": "settings_update"},
        "about": {"page_route": "settings_about"},
    }


def _infer_theme_management_pivot(second_key: str) -> str:
    k = str(second_key or "")
    background_keys = {
        "background",
        "main_window_background",
        "settings_window_background",
        "notification_floating_window_background",
        "select_background_image",
        "clear_background_image",
        "select_background_image_dialog",
        "image_files",
        "all_files",
        "preview_default",
        "preview_no_image",
        "preview_load_failed",
    }
    installed_keys = {
        "installed",
        "reload_themes",
        "uninstall",
        "current_version",
        "no_themes_installed",
        "in_use",
        "update",
    }

    if k in background_keys or k.startswith("background_") or k.endswith("_background"):
        return "background"
    if k in installed_keys or k.startswith("apply_") or k.startswith("cancel_"):
        return "installed"
    return "market"


def _resolve_entry_pivot(var_name: str, second_key: str, route: Dict[str, Any]) -> Any:
    pivot_map = route.get("pivot_map")
    if isinstance(pivot_map, dict):
        if second_key in pivot_map:
            return pivot_map.get(second_key)
    pivot = route.get("pivot")
    if var_name == "theme_management":
        return _infer_theme_management_pivot(second_key)
    return pivot


def build_settings_language_search_index(
    route_map: Optional[Dict[str, Dict[str, Any]]] = None,
    modules_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    if route_map is None:
        route_map = get_default_settings_route_map()

    if modules_dir is None:
        app_dir = Path(__file__).resolve().parents[2]
        modules_dir = app_dir / "Language" / "modules"

    index: List[Dict[str, Any]] = []

    for path in sorted(modules_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue

        try:
            module = importlib.import_module(f"app.Language.modules.{path.stem}")
        except Exception:
            continue

        for var_name, value in vars(module).items():
            if not isinstance(value, dict):
                continue

            if "ZH_CN" not in value and "EN_US" not in value:
                continue

            route = route_map.get(var_name)
            if not route:
                continue

            extracted = extract_language_strings(value)
            title_strings = extracted.get("title") or []
            for second_key, strings in extracted.items():
                if second_key == "title":
                    continue

                search_blob = (
                    " ".join(s for s in (list(title_strings) + list(strings)) if s)
                    .strip()
                    .lower()
                )
                if not search_blob:
                    continue

                try:
                    module_title = get_content_name_async(var_name, "title")
                except Exception:
                    module_title = var_name

                try:
                    item_title = get_content_name_async(var_name, second_key)
                except Exception:
                    item_title = second_key

                search_compact = _compact_text(search_blob)
                search_pinyin = _to_pinyin(search_blob)
                search_pinyin_initials = _to_pinyin_initials(search_blob)

                index.append(
                    {
                        "first": var_name,
                        "second": second_key,
                        "page_route": route.get("page_route"),
                        "pivot": _resolve_entry_pivot(var_name, second_key, route),
                        "search": search_blob,
                        "search_compact": search_compact,
                        "search_pinyin": search_pinyin,
                        "search_pinyin_initials": search_pinyin_initials,
                        "display": f"{module_title} - {item_title}",
                    }
                )

    return index


def search_settings_language_index(
    index: List[Dict[str, Any]], query: str, limit: int = 12
) -> List[Dict[str, Any]]:
    q_raw = str(query or "").strip()
    if not q_raw:
        return []

    q_compact = _compact_text(q_raw)
    if not q_compact:
        return []

    query_tokens = [_compact_text(t) for t in q_raw.split() if _compact_text(t)]

    scored = []
    for entry in index or []:
        best = 0
        candidates = [
            entry.get("search_compact") or _compact_text(entry.get("search") or ""),
            entry.get("search_pinyin") or "",
            entry.get("search_pinyin_initials") or "",
        ]

        for c in candidates:
            s = _score_fuzzy_match(q_compact, c)
            if s > best:
                best = s

        if len(query_tokens) > 1:
            token_sum = 0
            for token in query_tokens:
                token_best = 0
                for c in candidates:
                    ts = _score_fuzzy_match(token, c)
                    if ts > token_best:
                        token_best = ts
                if token_best <= 0:
                    token_sum = 0
                    break
                token_sum += token_best
            if token_sum > 0:
                best = max(best, 800 + token_sum // len(query_tokens))

        if best <= 0:
            continue

        scored.append((best, entry))

    scored.sort(key=lambda x: (-x[0], x[1].get("display") or ""))
    return [e for _, e in scored[: int(limit or 12)]]


def extract_language_strings(language_dict: Dict[str, Any]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for _, content in (language_dict or {}).items():
        if not isinstance(content, dict):
            continue
        for second_key, entry in content.items():
            if second_key not in result:
                result[second_key] = []
            collect_strings_recursive(entry, result[second_key])
    return result


def collect_strings_recursive(obj: Any, out_list: List[str]) -> None:
    if obj is None:
        return
    if isinstance(obj, str):
        out_list.append(obj)
        return
    if isinstance(obj, (int, float, bool)):
        return
    if isinstance(obj, list):
        for it in obj:
            collect_strings_recursive(it, out_list)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            collect_strings_recursive(v, out_list)
