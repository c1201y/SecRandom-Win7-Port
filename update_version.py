import os
import re


def get_version_from_env():
    raw_version = os.getenv("VERSION", "v0.0.0")
    stripped_version = re.sub(r"^v", "", raw_version)

    pre_release_suffix = ""
    if "-" in stripped_version:
        _, pre_release_suffix = stripped_version.split("-", 1)
        pre_release_suffix = f"-{pre_release_suffix}"

    # 匹配数字版本部分，包括预发布版本标识符之前的部分
    numeric_version = re.search(
        r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?", stripped_version
    )
    if numeric_version:
        major = int(numeric_version.group(1))
        minor = int(numeric_version.group(2) or 0)
        patch = int(numeric_version.group(3) or 0)

        version_3 = f"{major}.{minor}.{patch}"
        original_version = f"v{version_3}{pre_release_suffix}"
    else:
        version_3 = "0.0.0"
        original_version = "v0.0.0"
    return original_version, version_3


def update_version_info(version):
    # 处理三位数字的版本号
    version_parts = version.split(".")
    # 确保有三位数字
    while len(version_parts) < 3:
        version_parts.append("0")
    # 只取前三位
    major, minor, patch = map(int, version_parts[:3])

    version_tuple = (major, minor, patch)
    version_str = f"{major}.{minor}.{patch}"

    with open("version_info.txt", "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"filevers=\(\d, \d, \d(?:, \d)?\)", f"filevers={version_tuple}", content
    )
    content = re.sub(
        r"prodvers=\(\d, \d, \d(?:, \d)?\)", f"prodvers={version_tuple}", content
    )
    content = re.sub(
        r"StringStruct\(u\'FileVersion\', u\'[^\']+\'\)",
        f"StringStruct(u'FileVersion', u'{version_str}')",
        content,
    )
    content = re.sub(
        r"StringStruct\(u\'ProductVersion\', u\'[^\']+\'\)",
        f"StringStruct(u'ProductVersion', u'{version_str}')",
        content,
    )

    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(content)


def update_config_py(version):
    with open("app/tools/variable.py", "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'^VERSION = "v?[^\"]+"', f'VERSION = "{version}"', content, flags=re.MULTILINE
    )
    with open("app/tools/variable.py", "w", encoding="utf-8") as f:
        f.write(content)


def update_iss_version(stripped_version):
    if os.path.exists("SRsetup.iss"):
        with open("SRsetup.iss", "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'#define MyAppVersion "[^"]+"',
            f'#define MyAppVersion "{stripped_version}"',
            content,
        )
        with open("SRsetup.iss", "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    original_version, version_3 = get_version_from_env()
    update_version_info(version_3)
    update_config_py(original_version)
    update_iss_version(version_3)
