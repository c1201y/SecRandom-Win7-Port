#!/usr/bin/env python3
"""
无视操作符，一律把 pyproject.toml 里 *所有* 可更新的依赖
改成当前环境下的最新版本号，然后 uv lock。
"""

import json
import subprocess
import tomlkit
import re
import shutil

PYPROJECT = "pyproject.toml"
# 如果想强制全部改成 >=，把 REWRITE_OP 设成 True
REWRITE_OP = False
NEW_OP = ">="  # 统一操作符

# 1. 拿到最新版本 map
uv_exe = shutil.which("uv")
if uv_exe is None:
    raise SystemExit(
        "`uv` executable not found in PATH. Install 'uv' or add it to PATH."
    )

latest = {
    pkg["name"]: pkg["latest_version"]
    for pkg in json.loads(
        subprocess.check_output(
            [uv_exe, "pip", "list", "--outdated", "--format=json"], text=True
        )
    )
}

# 2. 加载 toml
with open(PYPROJECT, encoding="utf-8") as f:
    doc = tomlkit.load(f)

# 3. 正则：把“包名+操作符+版本”拆成 3 组
spec_re = re.compile(r"^([A-Za-z0-9\-_]+)\s*([~>=^!]=?|===?)\s*(.+)$")


def bump_one_spec(spec: str) -> str:
    m = spec_re.match(spec.strip())
    if not m:
        return spec  # 无法解析，保持原样
    name, op, _ver = m.groups()
    if name not in latest:
        return spec  # 没有新版本
    new_op = NEW_OP if REWRITE_OP else op
    return f"{name}{new_op}{latest[name]}"


# 4. 遍历所有依赖字段（这里示范 dependencies 和 dev-dependencies）
for sect in ("dependencies", "dev-dependencies"):
    deps = doc["project"].get(sect, [])
    if not deps:
        continue
    new_deps = [bump_one_spec(d) for d in deps]
    if new_deps != deps:
        doc["project"][sect] = new_deps
        print(f"✅ 已更新 {sect}")

# 5. 写回 & 重新 lock
with open(PYPROJECT, "w", encoding="utf-8") as f:
    tomlkit.dump(doc, f)

subprocess.check_call([uv_exe, "lock"])
print("🎉 全部完成！")
