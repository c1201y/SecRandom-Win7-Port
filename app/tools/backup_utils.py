from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from loguru import logger

from app.tools.path_utils import ensure_dir, get_data_path, get_path
from app.tools.settings_access import readme_settings_async, update_settings
from app.tools.variable import LOG_DIR, SPECIAL_VERSION


LAST_BACKUP_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
BACKUP_FILENAME_TIME_FORMAT = "%Y%m%d_%H%M%S"


@dataclass(frozen=True)
class BackupResult:
    file_path: Path
    exported_files: int
    created_at: datetime


def get_backup_dir() -> Path:
    backup_dir = get_data_path("backup")
    ensure_dir(backup_dir)
    return backup_dir


def list_backup_files() -> list[Path]:
    backup_dir = get_backup_dir()
    files = [p for p in backup_dir.glob("*.zip") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def get_backup_dir_size_bytes() -> int:
    total = 0
    for p in list_backup_files():
        try:
            total += p.stat().st_size
        except Exception:
            continue
    return total


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_backup_target_defs() -> list[tuple[str, str, Path]]:
    return [
        ("include_config", "config", get_path("config")),
        ("include_list", "list", get_data_path("list")),
        ("include_language", "Language", get_data_path("Language")),
        ("include_history", "history", get_data_path("history")),
        ("include_audio", "audio", get_data_path("audio")),
        ("include_cses", "CSES", get_data_path("CSES")),
        ("include_images", "images", get_data_path("images")),
        ("include_themes", "theme", get_data_path("themes")),
        ("include_logs", "logs", get_path(LOG_DIR)),
    ]


def is_backup_target_enabled(include_key: str) -> bool:
    enabled = readme_settings_async("backup", include_key)
    return True if enabled is None else bool(enabled)


def _dirs_to_backup() -> list[tuple[str, Path]]:
    return [
        (dir_name, dir_path)
        for include_key, dir_name, dir_path in get_backup_target_defs()
        if is_backup_target_enabled(include_key)
    ]


def _write_version_info(zipf: zipfile.ZipFile) -> None:
    version_info = {"software_name": "SecRandom", "version": SPECIAL_VERSION}
    zipf.writestr(
        "version.json", json.dumps(version_info, ensure_ascii=False, indent=2)
    )


def export_all_data_to_zip(target_zip_path: Path) -> int:
    target_zip_path.parent.mkdir(parents=True, exist_ok=True)

    exported_count = 0
    with zipfile.ZipFile(target_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        _write_version_info(zipf)
        for dir_name, dir_path in _dirs_to_backup():
            if not dir_path.exists():
                continue
            for file_path_obj in dir_path.rglob("*"):
                if not file_path_obj.is_file():
                    continue
                try:
                    arc_path = str(Path(dir_name) / file_path_obj.relative_to(dir_path))
                    zipf.write(str(file_path_obj), arc_path)
                    exported_count += 1
                except Exception as e:
                    logger.warning(f"添加文件到ZIP失败 {file_path_obj}: {e}")

    return exported_count


def create_backup_filename(kind: str) -> str:
    ts = datetime.now().strftime(BACKUP_FILENAME_TIME_FORMAT)
    safe_kind = (kind or "backup").strip().lower()
    return f"SecRandom_{SPECIAL_VERSION}_{safe_kind}_{ts}.zip"


def create_backup(
    kind: str = "manual", output_dir: Optional[Path] = None
) -> BackupResult:
    created_at = datetime.now()
    out_dir = output_dir or get_backup_dir()
    file_path = out_dir / create_backup_filename(kind)
    exported_files = export_all_data_to_zip(file_path)
    return BackupResult(
        file_path=file_path, exported_files=exported_files, created_at=created_at
    )


def prune_backups(max_count: int) -> list[Path]:
    try:
        max_count_int = int(max_count)
    except Exception:
        max_count_int = 16
    if max_count_int < 0:
        max_count_int = 16
    if max_count_int == 0:
        return []

    files = list_backup_files()
    to_delete = files[max_count_int:]
    deleted: list[Path] = []
    for p in to_delete:
        try:
            p.unlink(missing_ok=True)
            deleted.append(p)
        except Exception as e:
            logger.warning(f"删除旧备份失败 {p}: {e}")
    return deleted


def _parse_last_backup_time(value: object) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), LAST_BACKUP_TIME_FORMAT)
    except Exception:
        return None


def get_last_success_backup_time() -> Optional[datetime]:
    return _parse_last_backup_time(readme_settings_async("backup", "last_success_time"))


def set_last_success_backup(result: BackupResult) -> None:
    update_settings(
        "backup",
        "last_success_time",
        result.created_at.strftime(LAST_BACKUP_TIME_FORMAT),
    )
    update_settings("backup", "last_success_file", str(result.file_path))


def is_auto_backup_enabled() -> bool:
    enabled = readme_settings_async("backup", "auto_backup_enabled")
    return True if enabled is None else bool(enabled)


def get_auto_backup_interval_days() -> int:
    v = readme_settings_async("backup", "auto_backup_interval_days")
    try:
        days = int(v)
    except Exception:
        days = 7
    return max(1, days)


def get_auto_backup_max_count() -> int:
    v = readme_settings_async("backup", "auto_backup_max_count")
    try:
        c = int(v)
    except Exception:
        c = 16
    return max(0, c)


def is_backup_due(now: Optional[datetime] = None) -> bool:
    if not is_auto_backup_enabled():
        return False
    now_dt = now or datetime.now()
    last_dt = get_last_success_backup_time()
    if last_dt is None:
        return True
    interval_days = get_auto_backup_interval_days()
    return now_dt - last_dt >= timedelta(days=interval_days)


def get_last_success_backup_text() -> str:
    value = readme_settings_async("backup", "last_success_time")
    return "" if value is None else str(value)
