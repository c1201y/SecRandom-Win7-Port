"""将ZH_CN语言字典导出为JSON文件供外部使用。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from app.tools.language_manager import get_simple_language_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将ZH_CN语言包导出到JSON文件。")
    parser.add_argument(
        "-o",
        "--output",
        help="导出JSON的目标文件。默认为scripts/zh_cn_language.json",
        type=Path,
        default=None,
    )
    return parser.parse_args()


def export_language(language_code: str, destination: Path) -> None:
    manager = get_simple_language_manager()
    languages = manager.get_all_languages()
    language_data = languages.get(language_code)

    if language_data is None:
        raise RuntimeError(f"未找到语言 {language_code}；可用语言：{sorted(languages)}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(language_data, handle, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_args()
    default_path = Path(__file__).resolve().parent / "zh_cn_language.json"
    target_path = args.output or default_path

    print(f"正在将ZH_CN资源导出到 {target_path}")
    export_language("ZH_CN", target_path)
    print("导出完成。")


if __name__ == "__main__":
    main()
