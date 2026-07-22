"""
从Crowdin JSON导出文件导入翻译并合并到语言模块文件中。

使用方法：
    python scripts/import_crowdin_language.py path/to/EN_US.json
    python scripts/import_crowdin_language.py path/to/ZH_TW.json --dry-run

脚本将执行以下操作：
1. 解析Crowdin JSON文件（包含{identifier, translation, ...}的数组）
2. 从文件名中提取语言代码（例如，从EN_US.json中提取EN_US）
3. 扫描模块文件以查找每个文件中定义的实际变量名
4. 更新app/Language/modules/中的每个模块文件，添加新的语言条目
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

LANGUAGE_MODULES_DIR = ROOT_DIR / "app" / "Language" / "modules"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将Crowdin翻译导入到语言模块文件中。")
    parser.add_argument(
        "crowdin_file",
        type=Path,
        help="Crowdin JSON导出文件的路径（例如：EN_US.json）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="打印将要更改的内容但不修改文件",
    )
    return parser.parse_args()


def load_crowdin_json(path: Path) -> list[dict[str, Any]]:
    """加载Crowdin导出的JSON文件。"""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON文件应包含一个对象数组")
            return data
    except json.JSONDecodeError as e:
        print(f"错误：无法解析JSON文件 {path}: {e}")
        raise
    except Exception as e:
        print(f"错误：读取文件 {path} 时出现问题: {e}")
        raise


def extract_language_code(filename: str) -> str:
    """从文件名中提取语言代码（例如：从'EN_US.json'中提取'EN_US'）。"""
    stem = Path(filename).stem
    if not stem:
        raise ValueError(f"无效的文件名: {filename}")
    return stem.upper()


def scan_module_files() -> dict[str, tuple[Path, str]]:
    """
    扫描所有模块文件并提取定义语言字典的变量名。

    返回一个字典：{variable_name: (file_path, variable_name)}
    例如：{"set_prize_name": (Path(".../lottery_list.py"), "set_prize_name")}
    """
    var_to_file: dict[str, tuple[Path, str]] = {}

    var_pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", re.MULTILINE)

    if not LANGUAGE_MODULES_DIR.exists():
        print(f"错误：语言模块目录不存在: {LANGUAGE_MODULES_DIR}")
        return var_to_file

    for py_file in LANGUAGE_MODULES_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            for match in var_pattern.finditer(content):
                var_name = match.group(1)
                start = match.end() - 1
                # 扩大搜索范围以确保能找到语言定义
                search_end = min(start + 2000, len(content))
                if '"ZH_CN"' in content[start:search_end]:
                    var_to_file[var_name] = (py_file, var_name)
        except UnicodeDecodeError as e:
            print(f"警告：无法以UTF-8编码读取 {py_file}，可能是编码问题: {e}")
        except Exception as e:
            print(f"警告：读取 {py_file} 时出错：{e}")

    return var_to_file


def group_by_module(entries: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """
    按模块名对Crowdin条目进行分组。

    返回一个字典：{module_name: {dotted_key: translation}}
    例如：{"basic_settings": {"title.name": "基本设置", ...}}
    """
    modules: dict[str, dict[str, str]] = {}

    for i, entry in enumerate(entries):
        # 检查条目是否为字典
        if not isinstance(entry, dict):
            print(f"警告：条目 {i} 不是字典格式，跳过")
            continue

        identifier = entry.get("identifier", "")
        translation = entry.get("translation", "")

        # 跳过没有标识符或翻译的条目，但记录警告
        if not identifier:
            print(f"警告：条目 {i} 缺少标识符，跳过")
            continue

        if not translation:
            print(f"警告：条目 {i} 缺少翻译（标识符: {identifier}），跳过")
            continue

        parts = identifier.split(".")
        if len(parts) < 2:
            print(f"警告：条目 {i} 的标识符格式不正确: {identifier}，跳过")
            continue

        module_name = parts[0]
        key_path = ".".join(parts[1:])

        # 检查键路径是否为空
        if not key_path:
            print(f"警告：条目 {i} 的键路径为空: {identifier}，跳过")
            continue

        if module_name not in modules:
            modules[module_name] = {}
        modules[module_name][key_path] = translation

    return modules


def set_nested_value(d: dict, key_path: str, value: Any) -> None:
    """
    使用点表示法在字典中设置嵌套值。

    例如：set_nested_value(d, "title.name", "你好")
    设置 d["title"]["name"] = "你好"
    """
    keys = key_path.split(".")
    current = d

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            # 如果现有值不是字典，我们需要将其转换为字典
            # 但这可能会丢失原有数据，所以发出警告
            print(
                f"警告：将非字典值 '{current[key]}' 转换为字典以适应路径 '{key_path}'"
            )
            current[key] = {}
        current = current[key]

    final_key = keys[-1]
    current[final_key] = value


def build_language_dict(translations: dict[str, str]) -> dict[str, Any]:
    """
    从扁平的点分隔键构建嵌套字典。

    输入：{"title.name": "你好", "title.description": "世界"}
    输出：{"title": {"name": "你好", "description": "世界"}}
    """
    result: dict[str, Any] = {}
    for key_path, value in translations.items():
        set_nested_value(result, key_path, value)
    return result


def format_dict_as_python(d: dict, indent: int = 0) -> str:
    """将字典格式化为带有适当缩进的Python代码。"""
    lines = []
    prefix = "    " * indent
    inner_prefix = "    " * (indent + 1)

    lines.append("{")
    items = list(d.items())

    for i, (key, value) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""

        if isinstance(value, dict):
            nested = format_dict_as_python(value, indent + 1)
            lines.append(f'{inner_prefix}"{key}": {nested}{comma}')
        elif isinstance(value, str):
            escaped = (
                value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            lines.append(f'{inner_prefix}"{key}": "{escaped}"{comma}')
        elif isinstance(value, list):
            list_str = json.dumps(value, ensure_ascii=False)
            lines.append(f'{inner_prefix}"{key}": {list_str}{comma}')
        else:
            lines.append(f'{inner_prefix}"{key}": {repr(value)}{comma}')

    lines.append(f"{prefix}}}")
    return "\n".join(lines)


def update_module_file(
    module_path: Path,
    var_name: str,
    language_code: str,
    translations: dict[str, str],
    dry_run: bool = False,
) -> bool:
    """
    更新语言模块文件以包含新的语言。

    如果文件被修改（或在dry-run模式下会被修改），则返回True。
    """
    if not module_path.exists():
        print(f"警告：模块文件未找到：{module_path}")
        return False

    content = module_path.read_text(encoding="utf-8")

    lang_dict = build_language_dict(translations)

    # 检查模块中是否已存在该语言
    dict_pattern = rf"^{re.escape(var_name)}\s*=\s*\{{"
    match = re.search(dict_pattern, content, re.MULTILINE)

    if not match:
        print(f"警告：在 {module_path.name} 中未找到 '{var_name} = {{' 定义")
        return False

    # 检查语言代码是否已存在（更精确的检查）
    # 只在当前变量的作用域内查找
    dict_start = match.end() - 1
    brace_count = 0
    dict_end = -1
    in_string = False
    escape_next = False
    search_content = content[dict_start:]

    for i, char in enumerate(search_content):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                dict_end = i
                break

    # 在当前变量的字典范围内查找语言代码
    if dict_end > 0:
        var_content = search_content[:dict_end]
        lang_pattern = rf'"{language_code}":\s*\{{'
        if re.search(lang_pattern, var_content):
            print(
                f"  语言 '{language_code}' 已存在于 {module_path.name}:{var_name} 中，将更新现有翻译..."
            )
            # 调用更新函数而不是直接返回
            return update_existing_language(
                content,
                dict_start,
                dict_end,
                var_content,
                language_code,
                lang_dict,
                module_path,
                var_name,
                dry_run,
            )

    # 移除了可能导致问题的代码段
    # 这部分代码实际上没有被使用，而且可能会导致错误

    # 重新计算字典范围
    dict_start = match.end() - 1
    brace_count = 0
    dict_end = -1
    in_string = False
    escape_next = False

    for i, char in enumerate(content[dict_start:], start=dict_start):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                dict_end = i
                break

    if dict_end == -1:
        print(f"  警告：在 {module_path.name} 中找不到 {var_name} 的右大括号")
        return False

    formatted_dict = format_dict_as_python(lang_dict, indent=1)
    new_entry = f'    "{language_code}": {formatted_dict},\n'

    # 更稳健地处理逗号插入逻辑
    before_close = content[dict_start:dict_end]
    last_non_ws_idx = len(before_close) - 1
    while last_non_ws_idx >= 0 and before_close[last_non_ws_idx] in " \t\n\r":
        last_non_ws_idx -= 1

    # 检查最后一个非空白字符是否为逗号
    if (
        last_non_ws_idx >= 0
        and before_close[last_non_ws_idx] != ","
        and before_close[last_non_ws_idx] != "{"
    ):
        insert_comma_pos = dict_start + last_non_ws_idx + 1
        content = content[:insert_comma_pos] + "," + content[insert_comma_pos:]
        dict_end += 1
    # 如果字典是空的，不需要添加逗号
    elif last_non_ws_idx >= 0 and before_close[last_non_ws_idx] == "{":
        pass  # 空字典，不需要逗号

    new_content = content[:dict_end] + new_entry + content[dict_end:]

    if dry_run:
        print(f"将要添加 '{language_code}' 到 {module_path.name}:{var_name}")
        print(
            f"键: {list(translations.keys())[:5]}{'...' if len(translations) > 5 else ''}"
        )
        return True

    module_path.write_text(new_content, encoding="utf-8")
    print(f"已添加 '{language_code}' 到 {module_path.name}:{var_name}")
    return True


def update_existing_language(
    content,
    dict_start,
    dict_end,
    var_content,
    language_code,
    lang_dict,
    module_path,
    var_name,
    dry_run,
):
    """更新已存在的语言条目"""
    # 查找现有语言条目的位置
    lang_pattern = rf'"{language_code}"\s*:\s*\{{'
    lang_match = re.search(lang_pattern, var_content)

    if not lang_match:
        print(f"  无法定位现有语言条目 '{language_code}'")
        return False

    # 计算在完整文件中的绝对位置
    lang_start_in_var = lang_match.start()
    lang_start_abs = dict_start + lang_start_in_var

    # 查找语言字典的结束位置
    brace_count = 0
    lang_dict_end = -1
    in_string = False
    escape_next = False

    search_area = content[lang_start_abs:]

    for i, char in enumerate(search_area):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                lang_dict_end = lang_start_abs + i
                break

    if lang_dict_end == -1:
        print(f"  无法找到语言条目 '{language_code}' 的结束位置")
        return False

    # 格式化新的语言字典
    formatted_dict = format_dict_as_python(lang_dict, indent=1)
    new_lang_entry = f'    "{language_code}": {formatted_dict}'

    # 构造新内容
    # 找到语言条目后面的第一个逗号或大括号
    after_lang_end = lang_dict_end + 1
    while after_lang_end < len(content) and content[after_lang_end] in " \t\n\r":
        after_lang_end += 1

    # 检查下一个非空白字符是否是逗号
    if after_lang_end < len(content) and content[after_lang_end] == ",":
        # 包含逗号
        new_content = (
            content[:lang_start_abs] + new_lang_entry + content[after_lang_end:]
        )
    else:
        # 不包含逗号
        new_content = (
            content[:lang_start_abs] + new_lang_entry + content[lang_dict_end + 1 :]
        )

    if dry_run:
        print(f"将要更新 '{language_code}' 在 {module_path.name}:{var_name}")
        return True

    module_path.write_text(new_content, encoding="utf-8")
    print(f"已更新 '{language_code}' 在 {module_path.name}:{var_name}")
    return True


def main() -> None:
    try:
        args = parse_args()

        crowdin_file: Path = args.crowdin_file
        if not crowdin_file.exists():
            print(f"错误：文件未找到：{crowdin_file}")
            sys.exit(1)

        language_code = extract_language_code(crowdin_file.name)
        print(f"正在导入语言：{language_code}")
        print(f"源文件：{crowdin_file}")
        print(f"目标目录：{LANGUAGE_MODULES_DIR}")
        print()

        print("正在扫描模块文件...")
        var_to_file = scan_module_files()
        if not var_to_file:
            print("错误：未找到任何语言模块文件")
            sys.exit(1)

        print(
            f"找到 {len(var_to_file)} 个语言变量：{', '.join(sorted(var_to_file.keys()))}"
        )
        print()

        try:
            entries = load_crowdin_json(crowdin_file)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"错误：无法加载或解析JSON文件: {e}")
            sys.exit(1)

        print(f"已加载 {len(entries)} 个翻译条目")

        modules = group_by_module(entries)
        print(f"在Crowdin文件中找到 {len(modules)} 个标识符前缀")
        print()

        updated_count = 0
        unmatched_modules = []

        for module_name, translations in sorted(modules.items()):
            if module_name in var_to_file:
                file_path, var_name = var_to_file[module_name]
                try:
                    if update_module_file(
                        file_path, var_name, language_code, translations, args.dry_run
                    ):
                        updated_count += 1
                except Exception as e:
                    print(f"警告：更新模块 {module_name} 时出错: {e}")
                    continue
            else:
                unmatched_modules.append(module_name)

        print()
        if unmatched_modules:
            print(
                f"未匹配的Crowdin模块 ({len(unmatched_modules)}): {', '.join(sorted(unmatched_modules))}"
            )
            print("(这些标识符在模块文件中没有匹配的变量)")

        print()
        if args.dry_run:
            print(f"模拟运行完成。将更新 {updated_count} 个语言条目。")
        else:
            print(f"导入完成。已更新 {updated_count} 个语言条目。")

    except KeyboardInterrupt:
        print("\n操作被用户取消。")
        sys.exit(1)
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
