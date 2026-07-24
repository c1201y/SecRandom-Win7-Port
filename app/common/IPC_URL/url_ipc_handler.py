"""
URL和IPC混合处理器 - 跨平台通用实现
"""

from __future__ import annotations
import json
import socket
import threading
from multiprocessing.connection import Client, Listener
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import os
from loguru import logger
from urllib.parse import urlparse, parse_qs

from .protocol_manager import ProtocolManager
from .url_command_handler import URLCommandHandler
from .security_verifier import SimplePasswordVerifier


class URLIPCHandler:
    """URL和IPC混合处理器"""

    def __init__(
        self,
        app_name: str,
        protocol_name: str,
        password: str = None,
        ipc_name: str | None = None,
    ):
        """
        初始化URL IPC处理器

        Args:
            app_name: 应用程序名称
            protocol_name: 自定义协议名称（不含://）
            password: 可选的密码验证
        """
        self.app_name = app_name
        self.protocol_name = protocol_name
        self.ipc_name = self._normalize_ipc_name(
            ipc_name or self._build_ipc_name(app_name, protocol_name)
        )
        self.protocol_manager = ProtocolManager(app_name, protocol_name)
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.message_handlers: Dict[str, Callable] = {}
        self._listener: Optional[Listener] = None

        # 初始化命令处理器
        self.command_handler = URLCommandHandler()

        # 初始化安全验证器
        self.security_verifier = None
        if password:
            self.security_verifier = SimplePasswordVerifier(password)

    def register_url_protocol(self) -> bool:
        """
        注册URL协议

        Returns:
            注册成功返回True，失败返回False
        """
        try:
            return self.protocol_manager.register_protocol()
        except Exception as e:
            logger.exception(f"注册URL协议失败: {e}")
            return False

    def unregister_url_protocol(self) -> bool:
        """
        注销URL协议

        Returns:
            注销成功返回True，失败返回False
        """
        try:
            return self.protocol_manager.unregister_protocol()
        except Exception as e:
            logger.exception(f"注销URL协议失败: {e}")
            return False

    def is_protocol_registered(self) -> bool:
        """
        检查URL协议是否已注册

        Returns:
            已注册返回True，未注册返回False
        """
        return self.protocol_manager.is_protocol_registered()

    def start_ipc_server(self, port: int = 0) -> bool:
        """
        启动IPC服务器

        Args:
            port: 端口号，0表示自动分配

        Returns:
            启动成功返回True，失败返回False
        """
        if self.is_running:
            return True

        try:
            address, family = self._get_ipc_address_for_name(self.ipc_name)
            authkey = None

            if family == "AF_UNIX":
                try:
                    Path(address).unlink(missing_ok=True)
                except Exception:
                    pass

            self._listener = Listener(address=address, family=family, authkey=authkey)

            self.is_running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            return True
        except Exception as e:
            self.is_running = False
            self._listener = None
            winerror = getattr(e, "winerror", None)
            if os.name == "nt" and winerror in (5, 183):
                logger.warning(f"启动IPC服务器失败: {e}")
            else:
                logger.exception(f"启动IPC服务器失败: {e}")
            return False

    def stop_ipc_server(self):
        """停止IPC服务器"""
        self.is_running = False
        try:
            if self._listener is not None:
                self._listener.close()
        except Exception:
            pass
        finally:
            self._listener = None

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1)
            self.server_thread = None

        try:
            address, family = self._get_ipc_address_for_name(self.ipc_name)
            if family == "AF_UNIX":
                Path(address).unlink(missing_ok=True)
        except Exception:
            pass

    def _run_server(self):
        """运行IPC服务器"""
        if self._listener is None:
            return

        try:
            while self.is_running and self._listener is not None:
                try:
                    conn = self._listener.accept()
                except (OSError, EOFError):
                    break

                client_thread = threading.Thread(
                    target=self._handle_connection, args=(conn,), daemon=True
                )
                client_thread.start()
        except Exception as e:
            if self.is_running:
                logger.exception(f"IPC服务器错误: {e}")

    def _handle_connection(self, conn):
        try:
            if hasattr(conn, "_recv") and hasattr(conn, "_send"):
                data = self._recv_line_from_conn(conn)
            else:
                data = conn.recv_bytes()
            if not data:
                return

            message = json.loads(data.decode("utf-8").strip())
            response = self._process_message(message)
            response_bytes = (
                json.dumps(response, ensure_ascii=False).encode("utf-8") + b"\n"
            )
            if hasattr(conn, "_send"):
                self._send_line_to_conn(conn, response_bytes)
            else:
                conn.send_bytes(response_bytes)
        except EOFError:
            return
        except Exception as e:
            logger.exception(f"处理IPC消息错误: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _recv_line_from_conn(self, conn, max_bytes: int = 262144) -> bytes:
        buf = bytearray()
        try:
            recv = getattr(conn, "_recv", None)
            if recv is None:
                return b""

            while len(buf) < max_bytes:
                try:
                    chunk = recv(1)
                except EOFError:
                    break
                if not chunk:
                    break
                buf += chunk
                if chunk == b"\n":
                    break
        except Exception:
            return b""

        return bytes(buf)

    def _send_line_to_conn(self, conn, data: bytes) -> None:
        send = getattr(conn, "_send", None)
        if send is None:
            raise RuntimeError("IPC连接不支持原始发送")
        send(data)

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        message_type = message.get("type", "")
        payload = message.get("payload", {})

        logger.debug(f"收到消息 - 类型: {message_type}, 负载: {payload}")

        if message_type == "ping":
            return {"success": True, "type": "ping", "result": "pong"}

        if message_type in self.message_handlers:
            try:
                result = self.message_handlers[message_type](payload)
                response = {"success": True, "type": message_type, "result": result}
                logger.debug(f"消息处理成功 - 类型: {message_type}, 结果: {result}")
                return response
            except Exception as e:
                error_response = {
                    "success": False,
                    "type": message_type,
                    "error": str(e),
                }
                logger.exception(f"消息处理失败 - 类型: {message_type}, 错误: {e}")
                return error_response

        if message_type == "url":
            result = self._handle_url_message(payload)
            logger.debug(f"URL消息处理结果: {result}")
            return result

        unknown_response = {
            "success": False,
            "type": message_type,
            "error": f"未知的消息类型: {message_type}",
        }
        logger.warning(f"未知消息类型: {message_type}")
        return unknown_response

    def _handle_url_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理URL消息"""
        url = payload.get("url", "")
        if not url:
            logger.warning("URL消息缺少URL参数")
            return {"success": False, "error": "缺少URL参数"}

        logger.debug(f"处理URL消息: {url}")

        # 验证URL
        verification = payload.get("verification", {})
        if self.security_verifier:
            logger.debug(f"进行安全验证: {verification}")
            if not self.security_verifier.verify(verification):
                logger.warning(f"URL安全验证失败: {url}")
                return {"success": False, "error": "安全验证失败"}
            logger.debug("安全验证通过")

        # 处理URL命令
        try:
            logger.debug(f"执行URL命令: {url}")
            result = self.command_handler.handle_url_command(url)
            logger.info(f"URL命令执行成功: {url}, 结果: {result}")
            return {"success": True, "result": result}
        except Exception as e:
            logger.exception(f"URL命令执行失败: {url}, 错误: {e}")
            return {"success": False, "error": str(e)}

    def register_message_handler(self, message_type: str, handler: Callable):
        """
        注册消息处理器

        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self.message_handlers[message_type] = handler

    def send_ipc_message(
        self, port: int, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        发送IPC消息

        Args:
            port: 目标端口
            message: 消息内容

        Returns:
            响应内容，失败返回None
        """
        return self.send_ipc_message_by_name(message)

    def send_ipc_message_by_name(
        self,
        message: Dict[str, Any],
        target_ipc_name: str | None = None,
        timeout: float = 5.0,
    ) -> Optional[Dict[str, Any]]:
        try:
            target_name = self._normalize_ipc_name(target_ipc_name or self.ipc_name)
            address, family = self._get_ipc_address_for_name(target_name)
            request_bytes = (
                json.dumps(message, ensure_ascii=False).encode("utf-8") + b"\n"
            )
            response_data = self._send_stream_request(
                address=address,
                family=family,
                request_bytes=request_bytes,
                timeout=timeout,
            )

            if not response_data:
                return None
            return json.loads(response_data.decode("utf-8").strip())
        except Exception as e:
            logger.exception(f"发送IPC消息失败: {e}")
            return None

    def _send_stream_request(
        self, address: str, family: str, request_bytes: bytes, timeout: float
    ) -> Optional[bytes]:
        if os.name == "nt":
            conn = Client(address=address, family=family, authkey=None)
            try:
                conn.send_bytes(request_bytes)
                response = conn.recv_bytes()
                return response or None
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        if family != "AF_UNIX":
            raise RuntimeError(f"不支持的IPC family: {family}")

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(max(0.1, float(timeout)))
            sock.connect(address)
            sock.sendall(request_bytes)
            sock_file = sock.makefile("rb")
            try:
                response = sock_file.readline()
            finally:
                sock_file.close()
            return response or None
        finally:
            try:
                sock.close()
            except Exception:
                pass

    def send_ipc_message_to_app(
        self,
        target_app_name: str,
        target_protocol_name: str,
        message: Dict[str, Any],
        timeout: float = 5.0,
    ) -> Optional[Dict[str, Any]]:
        target_name = self._build_ipc_name(target_app_name, target_protocol_name)
        return self.send_ipc_message_by_name(
            message, target_ipc_name=target_name, timeout=timeout
        )

    def _get_authkey(self, ipc_name: str | None = None) -> bytes:
        return self._normalize_ipc_name(ipc_name or self.ipc_name).encode("utf-8")

    def _build_ipc_name(self, app_name: str, protocol_name: str) -> str:
        return f"{app_name}.{protocol_name}"

    def _normalize_ipc_name(self, ipc_name: str) -> str:
        value = str(ipc_name or "").strip()
        if not value:
            value = "ipc"
        value = value.replace(" ", "_").replace("/", "_").replace("\\", "_")
        value = value.replace(":", "_")
        return value

    def _get_ipc_address_for_name(self, ipc_name: str) -> tuple[str, str]:
        name = self._normalize_ipc_name(ipc_name)
        if os.name == "nt":
            return rf"\\.\pipe\{name}", "AF_PIPE"

        socket_path = Path("/tmp") / f"{name}.sock"
        return str(socket_path), "AF_UNIX"

    def _get_config_dir(self) -> Path:
        return Path.home() / ".config" / self.app_name

    def _save_ipc_config(self, address: str, family: str):
        config_dir = self._get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "ipc_config.json"
        config = {"address": address, "family": family}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _load_ipc_config(self) -> Optional[Dict[str, Any]]:
        config_file = self._get_config_dir() / "ipc_config.json"
        if not config_file.exists():
            return None
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                value = json.load(f)
                return value if isinstance(value, dict) else None
        except Exception:
            return None

    def _save_port_config(self, port: int):
        """保存端口配置"""
        config_dir = self._get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "ipc_config.json"
        config = {"port": port}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_port_config(self) -> Optional[int]:
        """加载端口配置"""
        config_file = self._get_config_dir() / "ipc_config.json"

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("port")
            except Exception as e:
                logger.exception(f"加载端口配置失败: {e}")

        return None

    def handle_url_args(self, url: str) -> Dict[str, Any]:
        """
        处理URL参数

        Args:
            url: URL字符串

        Returns:
            解析后的参数
        """
        logger.debug(f"处理URL参数: {url}")

        try:
            parsed = urlparse(url)

            # 检查协议是否匹配
            if parsed.scheme != self.protocol_name:
                logger.warning(
                    f"协议不匹配 - 期望: {self.protocol_name}, 实际: {parsed.scheme}"
                )
                return {"success": False, "error": f"不匹配的协议: {parsed.scheme}"}

            # 解析查询参数
            params = parse_qs(parsed.query)

            # 扁平化参数值（parse_qs返回的是列表）
            flat_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

            result = {
                "success": True,
                "path": parsed.path,
                "params": flat_params,
                "action": parsed.path.lstrip("/"),
            }
            logger.debug(f"URL参数解析成功: {result}")
            return result

        except Exception as e:
            logger.exception(f"URL参数解析失败: {url}, 错误: {e}")
            return {"success": False, "error": str(e)}

    def execute_url_command(
        self, url: str, verification: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        执行URL命令（带安全验证）

        Args:
            url: URL命令
            verification: 验证信息

        Returns:
            执行结果
        """
        logger.debug(f"执行URL命令: {url}")

        # 验证URL
        if self.security_verifier:
            verification = verification or {}
            logger.debug(f"进行安全验证: {verification}")
            if not self.security_verifier.verify(verification):
                logger.warning(f"安全验证失败: {url}")
                return {"success": False, "error": "安全验证失败"}
            logger.debug("安全验证通过")

        # 执行命令
        try:
            result = self.command_handler.handle_url_command(url)
            logger.info(f"URL命令执行成功: {url}, 结果: {result}")
            return {"success": True, "result": result}
        except Exception as e:
            logger.exception(f"URL命令执行失败: {url}, 错误: {e}")
            return {"success": False, "error": str(e)}

    def get_available_commands(self) -> Dict[str, Any]:
        """
        获取可用命令列表

        Returns:
            可用命令列表
        """
        return self.command_handler.get_available_commands()
