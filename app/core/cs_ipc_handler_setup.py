from loguru import logger


def create_cs_ipc_handler():
    """
    初始化 C# IPC 处理器

    Returns:
        CSharpIPCHandler: C# IPC处理器实例，如果创建失败返回None
    """
    global cs_ipc_handler
    try:
        from app.common.IPC_URL.csharp_ipc_handler import CSharpIPCHandler

        cs_ipc_handler = CSharpIPCHandler()
        cs_ipc_handler.start_ipc_client()

        logger.debug("C# IPC 处理器初始化完成")
        return cs_ipc_handler
    except Exception as e:
        logger.exception(f"初始化 C# IPC 处理器失败: {e}")
        return None
