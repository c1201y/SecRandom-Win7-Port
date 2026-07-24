"""
URL处理工具 - 处理应用启动时的URL参数
"""

import argparse
import os
import socket
import threading
from loguru import logger
from typing import Optional, Dict, Any
from PySide2.QtCore import QObject, Signal
from app.common.IPC_URL import URLIPCHandler
from app.common.IPC_URL.url_command_handler import URLCommandHandler
from app.tools.settings_access import get_settings_signals


class URLHandler(QObject):
    """URL参数处理器"""

    # 信号定义
    showSettingsRequested = Signal(str)  # 请求显示设置页面
    showSettingsPreviewRequested = Signal(str)  # 请求以预览模式显示设置页面
    showMainPageRequested = Signal(str)  # 请求显示主页面
    showTrayActionRequested = Signal(str)  # 请求执行托盘操作
    rollCallActionRequested = Signal(str, object)  # 点名页控制请求
    lotteryActionRequested = Signal(str, object)  # 抽奖页控制请求
    windowActionRequested = Signal(
        str, object
    )  # 窗口显示隐藏请求（主窗口/设置窗口/浮窗）

    def __init__(self, app_name: str = "SecRandom", protocol_name: str = "secrandom"):
        """
        初始化URL处理器

        Args:
            app_name: 应用程序名称
            protocol_name: 自定义协议名称
        """
        super().__init__()
        self.app_name = app_name
        self.protocol_name = protocol_name
        self.url_ipc_handler = URLIPCHandler(app_name, protocol_name)
        self.command_handler = URLCommandHandler()
        self._ipc_listener_connected = False

        # 连接信号
        self.command_handler.showSettingsRequested.connect(
            self.showSettingsRequested.emit
        )
        self.command_handler.showSettingsPreviewRequested.connect(
            self.showSettingsPreviewRequested.emit
        )
        self.command_handler.showMainPageRequested.connect(
            self.showMainPageRequested.emit
        )
        self.command_handler.showTrayActionRequested.connect(
            self.showTrayActionRequested.emit
        )
        self.command_handler.rollCallActionRequested.connect(
            self.rollCallActionRequested.emit
        )
        self.command_handler.lotteryActionRequested.connect(
            self.lotteryActionRequested.emit
        )
        self.command_handler.windowActionRequested.connect(
            self.windowActionRequested.emit
        )
        self._setup_ipc_setting_listener()

    def _setup_ipc_setting_listener(self) -> None:
        if self._ipc_listener_connected:
            return
        try:
            get_settings_signals().settingChanged.connect(self._on_setting_changed)
            self._ipc_listener_connected = True
        except Exception as e:
            logger.exception(f"连接设置变更监听失败: {e}")

    def _on_setting_changed(self, first_level_key: str, second_level_key: str, value):
        if first_level_key != "basic_settings" or second_level_key != "url_protocol":
            return
        try:
            desired = bool(value)
            if desired:
                logger.debug("URL协议开关已开启，准备注册URL协议并启动IPC服务器")
                logger.debug(
                    f"URL协议当前注册状态: {self.url_ipc_handler.is_protocol_registered()}"
                )

                if self._start_ipc_server_if_allowed():
                    logger.debug("IPC服务器已启用")
                else:
                    logger.warning("IPC服务器未启用")
            else:
                logger.debug("URL协议开关已关闭，准备停止IPC服务器并注销URL协议")
                self._stop_ipc_server()
                logger.debug("IPC服务器已停止")
                logger.debug(
                    f"URL协议当前注册状态: {self.url_ipc_handler.is_protocol_registered()}"
                )
        except Exception as e:
            logger.exception(f"处理URL协议设置变更失败: {e}")

    def _probe_existing_ipc_server(self, timeout: float = 0.5) -> bool:
        result = {"ok": False}

        def _worker():
            try:
                address, family = self.url_ipc_handler._get_ipc_address_for_name(
                    self.url_ipc_handler.ipc_name
                )
                if os.name == "nt":
                    with open(address, "r+b", buffering=0):
                        result["ok"] = True
                    return

                if family != "AF_UNIX":
                    return

                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                try:
                    sock.settimeout(max(0.1, float(timeout)))
                    sock.connect(address)
                    result["ok"] = True
                finally:
                    try:
                        sock.close()
                    except Exception:
                        pass
            except Exception:
                return

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout=max(0.0, float(timeout)))
        return bool(result["ok"])

    def _start_ipc_server_if_allowed(self) -> bool:
        if not self.url_ipc_handler.is_protocol_registered():
            logger.debug("URL协议未注册，跳过IPC服务器启动")
            return False

        if self.url_ipc_handler.start_ipc_server():
            self.url_ipc_handler.register_message_handler(
                "url", self._handle_ipc_url_message
            )
            return True
        if self._probe_existing_ipc_server():
            logger.debug("检测到IPC服务器已存在，跳过启动")
            return True
        return False

    def _stop_ipc_server(self) -> None:
        try:
            self.url_ipc_handler.stop_ipc_server()
        except Exception as e:
            logger.exception(f"停止IPC服务器失败: {e}")

    def parse_command_line_args(self) -> Optional[Dict[str, Any]]:
        """
        解析命令行参数

        Returns:
            如果有URL参数则返回解析结果，否则返回None
        """
        parser = argparse.ArgumentParser(description=f"{self.app_name} URL Handler")
        parser.add_argument("--url", type=str, help="URL参数")

        # 解析已知的参数，忽略未知参数
        known_args, unknown_args = parser.parse_known_args()

        if known_args.url:
            return self.url_ipc_handler.handle_url_args(known_args.url)

        return None

    def handle_command_line_args(self, args: list) -> Optional[Dict[str, Any]]:
        """
        处理命令行参数

        Args:
            args: 命令行参数列表

        Returns:
            如果有URL参数则返回解析结果，否则返回None
        """
        for arg in args:
            if str(arg).lower().startswith("secrandom://"):
                return self.handle_url(arg)
        return None

    def handle_url(self, url: str) -> Dict[str, Any]:
        """
        处理URL

        Args:
            url: URL字符串

        Returns:
            处理结果
        """
        logger.debug(f"URLHandler.handle_url: 处理URL: {url}")

        # 解析URL，获取动作类型
        from urllib.parse import urlparse

        parsed = urlparse(url)

        # 修复URL解析逻辑：对于 secrandom://settings/list 这样的URL，settings 是 netloc，而不是 path 的一部分
        # 我们需要将 netloc 和 path 结合起来，才能得到完整的动作类型
        if parsed.netloc and parsed.path:
            # 这是一个带有 netloc 的URL，如 secrandom://settings/list
            full_path = f"{parsed.netloc}{parsed.path}"
        elif parsed.netloc:
            # 这是一个只有 netloc 的URL，如 secrandom://settings
            full_path = parsed.netloc
        else:
            # 这是一个只有 path 的URL，如 secrandom:///lottery
            full_path = parsed.path

        logger.debug(f"URLHandler.handle_url: 解析URL完整路径: {full_path}")

        # 根据完整路径类型直接发出信号
        if "settings" in full_path:
            # 这是一个设置页面URL，发出 showSettingsRequested 信号
            logger.debug("URLHandler.handle_url: 发出 showSettingsRequested 信号")
        elif "lottery" in full_path:
            # 这是一个抽奖页面URL，发出 showMainPageRequested 信号
            logger.debug(
                "URLHandler.handle_url: 发出 showMainPageRequested 信号，参数: 'lottery_page'"
            )
            self.showMainPageRequested.emit("lottery_page")
        elif "rollcall" in full_path:
            # 这是一个点名页面URL，发出 showMainPageRequested 信号
            logger.debug(
                "URLHandler.handle_url: 发出 showMainPageRequested 信号，参数: 'roll_call_page'"
            )
            self.showMainPageRequested.emit("roll_call_page")

        # 调用 command_handler.handle_url_command(url) 处理URL
        result = self.command_handler.handle_url_command(url)
        logger.debug(f"URLHandler.handle_url: 处理结果: {result}")
        return result

    def handle_url_startup(self, url: str) -> Dict[str, Any]:
        """
        处理URL启动

        Args:
            url: URL字符串

        Returns:
            处理结果
        """
        # 直接使用URLCommandHandler处理URL
        return self.command_handler.handle_url_command(url)

    def check_single_instance(self) -> bool:
        """
        检查单实例

        Returns:
            如果是第一个实例返回True，否则返回False
        """
        if not self.url_ipc_handler.is_protocol_registered():
            logger.debug("URL协议未注册，跳过单实例IPC监听")
            return True

        return self._start_ipc_server_if_allowed()

    def _handle_ipc_url_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理IPC URL消息
        """
        url = payload.get("url", "")
        if url:
            return self.handle_url_startup(url)
        else:
            return {"success": False, "error": "缺少URL参数"}

    def send_url_to_existing_instance(self, url: str) -> bool:
        """
        发送URL到已存在的实例

        Args:
            url: URL字符串

        Returns:
            发送成功返回True，失败返回False
        """
        message = {"type": "url", "payload": {"url": url}}
        response = self.url_ipc_handler.send_ipc_message_by_name(message)
        return response is not None and response.get("success", False)


def handle_url_arguments() -> Optional[Dict[str, Any]]:
    """
    全局函数：处理URL参数

    Returns:
        如果有URL参数则返回处理结果，否则返回None
    """
    url_handler = URLHandler()

    # 解析命令行参数
    result = url_handler.parse_command_line_args()

    if result:
        # 检查是否是单实例
        if url_handler.check_single_instance():
            # 是第一个实例，直接处理URL
            return url_handler.handle_url_startup(result.get("url", ""))
        else:
            # 已有实例运行，发送URL到现有实例
            if url_handler.send_url_to_existing_instance(result.get("url", "")):
                return {
                    "success": True,
                    "message": "URL已发送到现有实例",
                    "url": result.get("url", ""),
                }
            else:
                return {"success": False, "error": "无法连接到现有实例"}

    return None
