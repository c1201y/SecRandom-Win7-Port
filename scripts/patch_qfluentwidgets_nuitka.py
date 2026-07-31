"""在 Nuitka 编译前修补 qfluentwidgets 所有槽函数签名问题。

Nuitka 编译后信号-槽调用约定严格：信号发射参数时，槽函数必须能接收。
PySide2 解释模式下可容忍不匹配，但 Nuitka 会抛 TypeError。
本脚本将所有被信号连接且不接收参数的方法改为接收 *args。
"""
import pathlib
import re
import sys


def patch_file(py: pathlib.Path) -> int:
    """修补单个文件，返回修改的方法数。"""
    text = py.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    connected_methods = set()
    for line in lines:
        m = re.search(r"\.connect\(self\.(\w+)\)", line)
        if m:
            connected_methods.add(m.group(1))

    if not connected_methods:
        return 0

    count = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(\s+)def (\w+)\(self\)\s*:", line)
        if not m:
            continue
        indent, name = m.group(1), m.group(2)
        if name not in connected_methods or name.startswith("__"):
            continue
        lines[i] = f"{indent}def {name}(self, *args):"
        count += 1

    if count:
        py.write_text("\n".join(lines), encoding="utf-8")
    return count


def main() -> None:
    total = 0
    patched_files = 0
    search_roots = [pathlib.Path(p) for p in sys.path if p]
    for root in search_roots:
        base = root / "qfluentwidgets"
        if not base.exists():
            continue
        for py in sorted(base.rglob("*.py")):
            if "__pycache__" in str(py):
                continue
            n = patch_file(py)
            if n:
                print(f"Patched {py.relative_to(base)}: {n} method(s)")
                patched_files += 1
                total += n
    print(f"Done. {patched_files} files, {total} methods patched.")


if __name__ == "__main__":
    main()
