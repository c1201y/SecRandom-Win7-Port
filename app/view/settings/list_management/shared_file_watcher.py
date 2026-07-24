"""
共享文件系统监视器管理器
用于减少重复的文件系统监视器，优化内存使用
"""

from pathlib import Path
from PySide2.QtCore import QFileSystemWatcher, Signal, QObject
from typing import Dict, Set, Callable, Any
import weakref

from app.tools.path_utils import get_path


class SharedFileWatcherManager(QObject):
    """共享文件系统监视器管理器"""

    # 全局单例实例
    _instance = None

    # 信号：目录变化
    directory_changed = Signal(str)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        # 存储监视器和引用计数
        self._reference_counts: Dict[str, int] = {}
        self._callbacks: Dict[str, Set[Callable[[str], Any]]] = {}

        # 创建主监视器
        self._main_watcher = QFileSystemWatcher()
        self._main_watcher.directoryChanged.connect(self._on_directory_changed)

    @classmethod
    def instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_watcher(self, path: str, callback: Callable[[str], None]) -> bool:
        """
        添加文件系统监视器

        Args:
            path: 要监视的目录路径
            callback: 目录变化时的回调函数

        Returns:
            是否成功添加监视器
        """
        path_str = str(get_path(path).resolve())

        # 检查路径是否存在
        if not get_path(path_str).exists():
            return False

        # 增加引用计数
        if path_str in self._reference_counts:
            self._reference_counts[path_str] += 1
        else:
            self._reference_counts[path_str] = 1
            # 添加到主监视器
            self._main_watcher.addPath(path_str)

        # 存储回调函数
        if path_str not in self._callbacks:
            self._callbacks[path_str] = set()

        # 使用弱引用包装回调函数，避免内存泄漏
        if hasattr(callback, "__self__"):
            # 对于方法，使用弱引用
            weak_callback = weakref.WeakMethod(callback)
            self._callbacks[path_str].add(weak_callback)
        else:
            # 对于普通函数，直接存储
            self._callbacks[path_str].add(callback)

        return True

    def remove_watcher(self, path: str, callback: Callable[[str], None]) -> bool:
        """
        移除文件系统监视器

        Args:
            path: 要移除监视的目录路径
            callback: 要移除的回调函数

        Returns:
            是否成功移除监视器
        """
        path_str = str(get_path(path).resolve())

        if path_str not in self._reference_counts:
            return False

        # 移除回调函数
        if path_str in self._callbacks:
            # 根据回调类型使用相应的方式移除
            if hasattr(callback, "__self__"):
                # 对于方法，查找对应的弱引用
                for cb in list(self._callbacks[path_str]):
                    if isinstance(cb, weakref.WeakMethod) and cb() == callback:
                        self._callbacks[path_str].discard(cb)
                        break
            else:
                # 对于普通函数，直接移除
                self._callbacks[path_str].discard(callback)

        # 减少引用计数
        self._reference_counts[path_str] -= 1

        # 如果引用计数为0，完全移除监视器
        if self._reference_counts[path_str] <= 0:
            del self._reference_counts[path_str]
            if path_str in self._callbacks:
                del self._callbacks[path_str]
            self._main_watcher.removePath(path_str)
            return True

        return False

    def _on_directory_changed(self, path: str):
        """
        目录变化时的内部处理

        Args:
            path: 发生变化的目录路径
        """
        path_str = str(get_path(path).resolve())

        # 调用所有有效的回调函数
        if path_str in self._callbacks:
            for callback in list(self._callbacks[path_str]):
                try:
                    # 对于 WeakMethod，需要先解引用
                    if isinstance(callback, weakref.WeakMethod):
                        actual_callback = callback()
                        if actual_callback is not None:
                            actual_callback(path_str)
                    else:
                        callback(path_str)
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).error(
                        f"文件监视器回调函数执行失败: {e}"
                    )

        # 发出全局信号
        self.directory_changed.emit(path_str)

    def get_watched_paths(self) -> Set[str]:
        """获取当前正在监视的所有路径"""
        return set(self._reference_counts.keys())

    def get_reference_count(self, path: str) -> int:
        """获取指定路径的引用计数"""
        path_str = str(Path(path).resolve())
        return self._reference_counts.get(path_str, 0)

    def clear_all(self):
        """清除所有监视器"""
        self._reference_counts.clear()
        self._callbacks.clear()

        # 移除所有路径
        for path in list(self._main_watcher.directories()):
            self._main_watcher.removePath(path)


# 全局共享实例
_shared_watcher_manager = SharedFileWatcherManager()


def get_shared_file_watcher() -> SharedFileWatcherManager:
    """获取共享文件系统监视器管理器实例"""
    return _shared_watcher_manager
