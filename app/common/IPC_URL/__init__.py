"""
URL和IPC混合体模块 - 跨平台通用实现
支持Windows和Linux系统的URL协议注册和IPC通信

主要功能：
1. URL协议注册管理（跨平台）
2. IPC进程间通信
3. 命令行参数处理
4. 多实例检测和管理

快速开始：
    from app.common.IPC_URL import URLIPCHandler

    # 创建处理器
    handler = URLIPCHandler("MyApp", "myapp")

    # 注册协议
    handler.register_url_protocol()

    # 启动IPC服务器
    handler.start_ipc_server()

    # 注册消息处理器
    def handle_url(payload):
        print(f"收到URL: {payload.get('url', '')}")
        return {"status": "success"}

    handler.register_message_handler('url', handle_url)

详细文档请参考：
- README.md: 完整的使用文档
- QUICK_START.md: 快速开始指南
- example_usage.py: 使用示例
"""

from .url_ipc_handler import URLIPCHandler
from .protocol_manager import ProtocolManager
from .url_command_handler import URLCommandHandler
from .security_verifier import (
    SecurityVerifier,
    SimplePasswordVerifier,
    DynamicPasswordVerifier,
    CompositeVerifier,
)

__version__ = "1.0.0"
__author__ = "SecRandom Team"
__description__ = "跨平台URL协议注册和IPC通信处理器"

__all__ = [
    "URLIPCHandler",
    "ProtocolManager",
    "URLCommandHandler",
    "SecurityVerifier",
    "SimplePasswordVerifier",
    "DynamicPasswordVerifier",
    "CompositeVerifier",
    "__version__",
    "__author__",
    "__description__",
]
