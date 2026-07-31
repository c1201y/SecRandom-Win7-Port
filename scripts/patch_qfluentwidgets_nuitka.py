"""在 Nuitka 编译前修补 qfluentwidgets 所有槽函数签名问题。

Nuitka 编译后信号-槽调用约定严格：信号发射参数时，槽函数必须能接收。
PySide2 解释模式下可容忍不匹配，但 Nuitka 会抛 TypeError。
本脚本：
1. 将所有被信号连接且不接收参数的方法改为接收 *args；
2. 将 qfluentwidgets 内所有无参 lambda 改为接收 *_args；
3. Pivot/Segmented 系列：itemClicked 改为发射 self（控件对象），替代 bool 哨兵值。
"""
import pathlib
import re
import sys

LAMBDA_PATTERN = re.compile(r"\.connect\(\s*lambda\s*:")


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
        m = re.match(r"^(\s+)def (\w+)\(self\)(?:\s*->\s*[^:]+)?\s*:", line)
        if not m:
            continue
        indent, name = m.group(1), m.group(2)
        if name.startswith("__") and name.endswith("__"):
            continue
        if name not in connected_methods:
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
            f"{indent}item = args[0] if args and hasattr(args[0], 'property') else self.sender()"
        )

    new_text, n = pat.subn(repl, text)
    if n:
        py.write_text(new_text, encoding="utf-8")
    return n


def patch_lambdas(py: pathlib.Path) -> int:
    """将信号连接的无参 lambda 改为接收 *_args。

    PySide2 解释模式下无参 lambda 连接带参信号会自动截断参数；
    Nuitka 编译后的 lambda 无法内省参数数量，信号发射参数时会抛
    TypeError: <lambda>() takes 0 positional arguments but 1 was given。
    """
    text = py.read_text(encoding="utf-8", errors="replace")
    new_text, n = LAMBDA_PATTERN.subn(".connect(lambda *_args:", text)
    if n:
        py.write_text(new_text, encoding="utf-8")
    return n


def patch_pivot_signal(py: pathlib.Path) -> int:
    """Pivot/Segmented*Item：让 itemClicked 发射 self（控件对象）而非 bool 哨兵。

    qfluentwidgets 的 PivotItem.itemClicked 声明为 Signal(bool)，点击时
    emit(True)。原版槽用 self.sender() 反查控件，但 Nuitka 打包环境下
    sender() 可能返回 None。改为发射 self 后，槽直接使用信号参数即可，
    完全不依赖 sender()。
    """
    if py.name not in ("pivot.py", "segmented_widget.py"):
        return 0
    text = py.read_text(encoding="utf-8", errors="replace")
    orig = text
    text = text.replace(
        "itemClicked = Signal(bool)",
        "itemClicked = Signal(object)",
    )
    text = re.sub(
        r"self\.clicked\.connect\(lambda(?:\s*\*_args)?: self\.itemClicked\.emit\(True\)\)",
        "self.clicked.connect(lambda *_args: self.itemClicked.emit(self))",
        text,
    )
    if text != orig:
        py.write_text(text, encoding="utf-8")
    return 1 if text != orig else 0


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


def patch_project_methods(project_root: pathlib.Path) -> int:
    """修复 app/ 源码中被信号连接的无参方法。

    与 patch_file 相同思路：'.connect(self.method)' 连接的方法如果声明为
    'def method(self):'，Nuitka 编译后信号发射参数时会抛 TypeError。
    将这类方法改为接收 *args（不影响原方法体逻辑）。
    """
    total = 0
    files = 0
    app_dir = project_root / "app"
    for py in sorted(app_dir.rglob("*.py")):
        if "__pycache__" in str(py):
            continue
        n = patch_file(py)
        if n:
            print(f"Method-fixed {py.relative_to(project_root)}: {n} method(s)")
            total += n
            files += 1
    print(f"Method fix done. {files} files, {total} method(s).")
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
            k = patch_lambdas(py)
            m = patch_sender_usage(py)
            p = patch_pivot_signal(py)
            if n or k or m or p:
                print(f"Patched {py.relative_to(base)}: "
                      f"{n} method(s), {k} lambda(s), {m} sender fix, {p} pivot signal")
                patched_files += 1
                total += n + k + m + p
    print(f"Done. {patched_files} files, {total} patches.")

    project_root = pathlib.Path(__file__).resolve().parent.parent
    patch_project_lambdas(project_root)
    patch_project_methods(project_root)


if __name__ == "__main__":
    main()
