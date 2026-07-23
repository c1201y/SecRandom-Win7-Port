"""
PyInstaller 打包脚本
用于构建 SecRandom 的独立可执行文件
"""

import subprocess
import sys
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from packaging_utils import (
    ADDITIONAL_HIDDEN_IMPORTS,
    collect_data_includes,
    collect_language_modules,
    collect_view_modules,
    normalize_hidden_imports,
)

# 导入项目配置信息
sys.path.insert(0, str(Path(__file__).parent))
from app.tools.variable import APPLY_NAME, VERSION, APP_DESCRIPTION, AUTHOR, WEBSITE

# 导入deb包构建工具
from packaging_utils_deb import DebBuilder

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
SPEC_FILE = PROJECT_ROOT / "Secrandom.spec"


def _print_packaging_summary() -> None:
    """Log a quick overview of the data and modules that will be bundled."""

    data_includes = collect_data_includes()
    hidden_imports = normalize_hidden_imports(
        collect_language_modules() + collect_view_modules() + ADDITIONAL_HIDDEN_IMPORTS
    )

    print("\nSelected data includes ({} entries):".format(len(data_includes)))
    for item in data_includes:
        kind = "dir " if item.is_dir else "file"
        print(f"  - {kind} {item.source} -> {item.target}")

    print("\nHidden imports ({} modules):".format(len(hidden_imports)))
    for name in hidden_imports:
        print(f"  - {name}")


def build_deb() -> None:
    """构建deb包"""
    if sys.platform != "linux":
        return

    print("\n" + "=" * 60)
    print("开始构建deb包...")
    print("=" * 60)

    try:
        # 使用DebBuilder构建deb包
        DebBuilder.build_from_pyinstaller(
            project_root=PROJECT_ROOT,
            app_name=APPLY_NAME,
            version=VERSION,
            description=APP_DESCRIPTION,
            author=AUTHOR,
            website=WEBSITE,
        )
        print("=" * 60)

    except Exception as e:
        print(f"构建deb包失败: {e}")
        sys.exit(1)


def main():
    """执行 PyInstaller 打包"""
    print("=" * 60)
    print("开始使用 PyInstaller + uv 打包 SecRandom")
    print("=" * 60)

    if not SPEC_FILE.exists():
        print("\nSecrandom.spec 不存在，请先生成或恢复该文件。")
        sys.exit(1)

    _print_packaging_summary()

    # 使用uv run执行PyInstaller命令
    cmd = ["uv", "run", "-m", "PyInstaller", "Secrandom.spec", "--clean", "--noconfirm"]

    # 打印命令
    print("\n执行命令:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)

    # 执行打包
    try:
        result = subprocess.run(
            cmd,
            check=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print("\n" + "=" * 60)
        print("PyInstaller打包成功！")
        print("=" * 60)

        # 构建deb包（仅在Linux平台）
        build_deb()

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"打包失败: {e}")
        print(f"返回码: {e.returncode}")
        if e.stdout:
            print(f"标准输出:\n{e.stdout}")
        if e.stderr:
            print(f"错误输出:\n{e.stderr}")
        print("=" * 60)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"发生意外错误: {e}")
        import traceback

        traceback.print_exc()
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
