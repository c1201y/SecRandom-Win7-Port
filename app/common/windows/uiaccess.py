from __future__ import annotations
import os
import sys
import ctypes
from subprocess import list2cmdline

from loguru import logger

# Only import wintypes on Windows to avoid import errors on other platforms
if os.name == "nt":
    from ctypes import wintypes
else:
    # Create a dummy wintypes module for non-Windows platforms
    # NOTE: These dummy types are ONLY for import compatibility and type hints.
    # They should NEVER be instantiated at runtime because:
    # 1. All functions using wintypes check _is_windows() first and return early
    # 2. The dummy types lack ctypes-specific attributes like .value
    # This design is safe because non-Windows code paths never reach wintypes usage
    class _DummyWinTypes:
        DWORD = int
        BOOL = bool
        HWND = int
        LPCWSTR = str
        UINT = int

    wintypes = _DummyWinTypes()

from app.tools.path_utils import get_data_path

_uiaccess_dll = None
_user32 = None
_kernel32 = None

UIACCESS_RESTART_ENV = "SECRANDOM_RESTART_UIACCESS"
ELEVATE_RESTART_ENV = "SECRANDOM_RESTART_ELEVATED"
UIACCESS_RESTART_ARG = "--secrandom-uiaccess"
UIACCESS_RESTART_COUNT_ENV = "SECRANDOM_UIACCESS_RESTART_COUNT"


def _is_windows() -> bool:
    return os.name == "nt"


def _get_kernel32():
    global _kernel32
    if _kernel32 is not None:
        return _kernel32
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.ProcessIdToSessionId.argtypes = [
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    _kernel32.ProcessIdToSessionId.restype = wintypes.BOOL
    return _kernel32


def _get_user32():
    global _user32
    if _user32 is not None:
        return _user32
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    try:
        fn = _user32.SetWindowBand
        fn.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.DWORD]
        fn.restype = wintypes.BOOL
    except Exception:
        pass
    _user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    _user32.SetWindowPos.restype = wintypes.BOOL
    return _user32


def _get_uiaccess_dll():
    global _uiaccess_dll
    if _uiaccess_dll is not None:
        return _uiaccess_dll
    dll_path = get_data_path("dlls", "uiaccess.dll")
    _uiaccess_dll = ctypes.WinDLL(str(dll_path), use_last_error=True)

    _uiaccess_dll.IsUIAccess.argtypes = []
    _uiaccess_dll.IsUIAccess.restype = wintypes.BOOL

    _uiaccess_dll.StartUIAccessProcess.argtypes = [
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.DWORD,
    ]
    _uiaccess_dll.StartUIAccessProcess.restype = wintypes.BOOL

    return _uiaccess_dll


def is_uiaccess_process() -> bool:
    if not _is_windows():
        return False
    try:
        dll = _get_uiaccess_dll()
        return bool(dll.IsUIAccess())
    except Exception:
        return False


def start_uiaccess_process(cmd_list: list[str]) -> int:
    if not _is_windows():
        return 0
    if not cmd_list:
        return 0

    try:
        kernel32 = _get_kernel32()
        pid = wintypes.DWORD(os.getpid())
        session = wintypes.DWORD(0)
        if not kernel32.ProcessIdToSessionId(pid, ctypes.byref(session)):
            err = ctypes.get_last_error()
            logger.debug("获取 SessionId 失败: {}", err)
            return 0

        cmd_line = list2cmdline(list(cmd_list))

        dll = _get_uiaccess_dll()
        out_pid = wintypes.DWORD(0)
        ctypes.set_last_error(0)
        ok = bool(
            dll.StartUIAccessProcess(
                None,
                cmd_line,
                0,
                ctypes.byref(out_pid),
                session.value,
            )
        )
        if not ok:
            err = ctypes.get_last_error()
            logger.debug("启动 UIAccess 进程失败: {}", err)
            return 0

        logger.debug("已启动 UIAccess 进程: pid={}", int(out_pid.value))
        return int(out_pid.value)
    except Exception as e:
        logger.debug("启动 UIAccess 进程异常: {}", e)
        return 0


def ensure_uiaccess_for_current_process() -> bool:
    if not _is_windows():
        return False
    if is_uiaccess_process():
        return False

    try:
        kernel32 = _get_kernel32()
        pid = wintypes.DWORD(os.getpid())
        session = wintypes.DWORD(0)
        if not kernel32.ProcessIdToSessionId(pid, ctypes.byref(session)):
            err = ctypes.get_last_error()
            logger.debug("获取 SessionId 失败: {}", err)
            return False

        if getattr(sys, "frozen", False):
            cmd_list = [sys.executable] + (sys.argv[1:] if sys.argv else [])
        else:
            argv = list(sys.argv) if sys.argv else []
            if argv:
                cmd_list = [sys.executable] + argv
            else:
                cmd_list = [sys.executable]

        return bool(start_uiaccess_process(cmd_list))
    except Exception as e:
        logger.debug("启动 UIAccess 进程异常: {}", e)
        return False


def set_window_band_uiaccess(hwnd: int) -> bool:
    if not _is_windows():
        return False
    if not hwnd:
        return False
    if not is_uiaccess_process():
        return False

    try:
        user32 = _get_user32()
        h = wintypes.HWND(hwnd)
        hwnd_topmost = wintypes.HWND(-1)

        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040
        flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
        return bool(user32.SetWindowPos(h, hwnd_topmost, 0, 0, 0, 0, flags))
    except Exception:
        return False


def start_elevated_process(cmd_list: list[str], cwd: str | None = None) -> bool:
    if not _is_windows():
        return False
    if not cmd_list:
        return False
    executable = str(cmd_list[0] or "").strip()
    if not executable:
        return False

    params = list2cmdline(list(cmd_list[1:])) if len(cmd_list) > 1 else ""
    directory = str(cwd) if cwd else None
    try:
        shell32 = ctypes.windll.shell32
        shell32.ShellExecuteW.argtypes = [
            wintypes.HWND,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            ctypes.c_int,
        ]
        shell32.ShellExecuteW.restype = wintypes.HINSTANCE
        rc = int(shell32.ShellExecuteW(None, "runas", executable, params, directory, 1))
        if rc <= 32:
            logger.debug("请求管理员启动失败: rc={}", rc)
            return False
        return True
    except Exception as e:
        logger.debug("请求管理员启动异常: {}", e)
        return False
