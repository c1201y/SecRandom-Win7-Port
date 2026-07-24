from typing import Tuple
from typing import Optional, Callable, TypeVar, Any
from functools import wraps
from loguru import logger
from PySide2.QtCore import Qt, QRunnable
from PySide2.QtWidgets import QWidget


T = TypeVar("T")


def log_exception(func: Callable[..., T]) -> Callable[..., T]:
    """装饰器：捕获异常并记录日志

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = func.__name__
            logger.exception(f"{func_name} 执行失败: {e}", exc_info=True)
            return None

    return wrapper


def activate_window(window: QWidget) -> bool:
    """激活窗口，使其显示并置顶

    Args:
        window: 要激活的窗口

    Returns:
        bool: 是否激活成功
    """
    if window is None:
        logger.warning("尝试激活空窗口")
        return False

    try:
        window.show()
        window.raise_()
        if not (window.windowFlags() & Qt.WindowDoesNotAcceptFocus):
            window.activateWindow()
        return True
    except Exception as e:
        logger.exception(f"激活窗口失败: {e}", exc_info=True)
        return False


def safe_close_window(window: Optional[QWidget]) -> bool:
    """安全关闭窗口

    Args:
        window: 要关闭的窗口

    Returns:
        bool: 是否关闭成功
    """
    if window is None:
        return True

    try:
        window.close()
        window.deleteLater()
        return True
    except Exception as e:
        logger.exception(f"关闭窗口失败: {e}", exc_info=True)
        return False


class FunctionRunnable(QRunnable):
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(*self.args, **self.kwargs)


def safe_execute(
    func: Callable[..., T],
    *args: Any,
    error_message: str = "操作失败",
    **kwargs: Any,
) -> Tuple[bool, Optional[T]]:
    """安全执行函数，捕获异常并记录日志

    Args:
        func: 要执行的函数
        *args: 位置参数
        error_message: 错误消息
        **kwargs: 关键字参数

    Returns:
        tuple: (是否成功, 函数执行结果)
    """
    try:
        return True, func(*args, **kwargs)
    except Exception as e:
        logger.exception(f"{error_message}: {e}", exc_info=True)
        return False, None
