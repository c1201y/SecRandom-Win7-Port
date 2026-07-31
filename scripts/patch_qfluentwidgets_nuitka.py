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


def patch_sender_usage(py: pathlib.Path) -> int:
    """修复依赖 self.sender() 的槽函数。

    Nuitka 打包环境下 QObject.sender() 可能返回 None。
    将 'item = self.sender()' 改为优先使用信号发射的参数 args[0]。
    """
    if py.name != "pivot.py":
        return 0
    text = py.read_text(encoding="utf-8", errors="replace")
    pat = re.compile(
        r"def _onItemClicked\(self,\s*\*args\):\n(\s*)item = self\.sender\(\)"
        r"|def _onItemClicked\(self,\s*item=None\):\n(\s*)item = self\.sender\(\)"
    )

    def repl(m):
        indent = m.group(1) or m.group(2)
        return (
            "def _onItemClicked(self, *args):\n"
            f"{indent}item = args[0] if args else self.sender()"
        )

    new_text, n = pat.subn(repl, text)
    if n:
        py.write_text(new_text, encoding="utf-8")
    return n


LAMBDA_PATTERN = re.compile(r"\.connect\(\s*lambda\s*:")


def patch_project_lambdas(project_root: pathlib.Path) -> int:
    """修复 app/ 源码中信号连接的无参 lambda。

    PySide2 解释模式下连接无参 lambda 到带参信号会自动截断参数；
    Nuitka 编译后的 lambda 无法内省参数数量，信号发射参数时会抛
    TypeError: <lambda>() takes 0 positional arguments but 1 was given。
    将所有 '.connect(lambda: ...)' 改为 '.connect(lambda *_args: ...)'。
    """
    total = 0
    files = 0
    app_dir = project_root / "app"
    for py in sorted(app_dir.rglob("*.py")):
        if "__pycache__" in str(py):
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        new_text = LAMBDA_PATTERN.sub(".connect(lambda *_args:", text)
        if new_text != text:
            py.write_text(new_text, encoding="utf-8")
            n = len(LAMBDA_PATTERN.findall(text))
            print(f"Lambda-fixed {py.relative_to(project_root)}: {n} lambda(s)")
            total += n
            files += 1
    print(f"Lambda fix done. {files} files, {total} lambda(s).")
    return total


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
            m = patch_sender_usage(py)
            if n or m:
                print(f"Patched {py.relative_to(base)}: {n} method(s), {m} sender fix")
                patched_files += 1
                total += n + m
    print(f"Done. {patched_files} files, {total} methods patched.")

    project_root = pathlib.Path(__file__).resolve().parent.parent
    patch_project_lambdas(project_root)


if __name__ == "__main__":
    main()
