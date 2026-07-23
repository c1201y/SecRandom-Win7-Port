"""
SecRandom IPC URL 发送脚本

用途
- 向本机正在运行的 SecRandom 实例发送 URL（例如 SecRandom://settings）
- 通过“命名 IPC 通道”连接（Windows 命名管道 / Linux socket），无需端口

前提
- SecRandom 主程序已启动，并已启动 URL IPC 服务端

基本用法（Windows / Linux 通用）
- 发送打开设置页：
  python secrandom_ipc_send_url.py "SecRandom://settings"
- 发送切换页面：
  python secrandom_ipc_send_url.py "SecRandom://main/lottery"

使用 uv 运行（项目已配置 uv）
- uv run secrandom_ipc_send_url.py "SecRandom://settings"

参数说明
- url：要发送的 URL（大小写不敏感），例如：
  - SecRandom://settings
  - secrandom://settings/basic
  - SecRandom://tray/restart
- --ipc-name：目标通道名，默认 SecRandom.secrandom
  - Windows 对应：\\\\.\\pipe\\SecRandom.secrandom
  - Linux 对应：/tmp/SecRandom.secrandom.sock

返回与退出码
- 输出：打印服务端响应 JSON
- 退出码：
  - 0：success 为 true
  - 2：success 为 false（例如命令不支持/被拒绝/服务端返回失败）
  - 1：脚本运行异常（例如连接失败、序列化失败等）
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from multiprocessing.connection import Client


def _get_ipc_address(ipc_name: str) -> tuple[str, str]:
    if os.name == "nt":
        return rf"\\.\pipe\{ipc_name}", "AF_PIPE"
    return f"/tmp/{ipc_name}.sock", "AF_UNIX"


def send_url(url: str, ipc_name: str, timeout: float) -> dict:
    address, family = _get_ipc_address(ipc_name)
    authkey = ipc_name.encode("utf-8")

    message = {"type": "url", "payload": {"url": url}}

    try:
        conn = Client(address=address, family=family, authkey=authkey)
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ipc_not_found",
            "detail": f"IPC 通道不存在: {address}. 请确认 SecRandom 已运行且已启动 IPC 服务端。",
        }
    try:
        conn.send_bytes(json.dumps(message, ensure_ascii=False).encode("utf-8"))
        data = conn.recv_bytes()
        if not data:
            return {"success": False, "error": "empty_response"}
        return json.loads(data.decode("utf-8"))
    finally:
        conn.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Send SecRandom:// URL to running SecRandom via named IPC"
    )
    parser.add_argument(
        "url",
        type=str,
        help='URL to send, e.g. "SecRandom://settings" or "secrandom://rollcall"',
    )
    parser.add_argument(
        "--ipc-name",
        type=str,
        default="SecRandom.secrandom",
        help='Target IPC name, default: "SecRandom.secrandom"',
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Connect/read timeout seconds (best-effort; depends on OS IPC)",
    )

    args = parser.parse_args(argv)

    try:
        resp = send_url(args.url, ipc_name=args.ipc_name, timeout=args.timeout)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False, indent=2) + "\n")
        return 0 if resp.get("success") else 2
    except Exception as e:
        sys.stderr.write(f"IPC send failed: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
