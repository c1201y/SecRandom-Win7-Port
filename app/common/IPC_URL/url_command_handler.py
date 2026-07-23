# ==================================================
# URL和IPC命令处理器
# ==================================================
from __future__ import annotations
from typing import Dict, Any, Optional, Callable, List
from loguru import logger
from PySide2.QtCore import QObject, Signal
from urllib.parse import urlparse


# ==================================================
# 命令处理器类
# ==================================================
class URLCommandHandler(QObject):
    """URL和IPC命令处理器

    处理所有通过URL和IPC发送的命令，包括：
    - 打开设置页面
    - 切换主界面页面
    - 执行托盘功能
    - 安全验证
    """

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

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.security_verifier = None
        self.secure_commands: List[str] = []

        logger.debug(f"初始化URLCommandHandler - main_window: {main_window}")

        # 定义所有支持的命令映射
        self.command_map = {
            # 点名控制命令
            "roll_call/quick_draw": self._handle_roll_call_quick_draw,
            "roll_call/start": self._handle_roll_call_start,
            "roll_call/stop": self._handle_roll_call_stop,
            "roll_call/reset": self._handle_roll_call_reset,
            "roll_call/set_count": self._handle_roll_call_set_count,
            "roll_call/set_group": self._handle_roll_call_set_group,
            "roll_call/set_gender": self._handle_roll_call_set_gender,
            "roll_call/set_list": self._handle_roll_call_set_list,
            # 抽奖控制命令
            "lottery/start": self._handle_lottery_start,
            "lottery/stop": self._handle_lottery_stop,
            "lottery/reset": self._handle_lottery_reset,
            "lottery/set_count": self._handle_lottery_set_count,
            "lottery/set_pool": self._handle_lottery_set_pool,
            "lottery/set_range": self._handle_lottery_set_range,
            "lottery/set_gender": self._handle_lottery_set_gender,
            "lottery/set_list": self._handle_lottery_set_list,
            # 托盘功能命令
            "tray/toggle": self._handle_tray_toggle,
            "tray/settings": self._handle_tray_settings,
            "tray/float": self._handle_tray_float,
            "tray/restart": self._handle_tray_restart,
            "tray/exit": self._handle_tray_exit,
            # 窗口控制命令
            "window/main": self._handle_window_main,
            "window/settings": self._handle_window_settings,
            "window/float": self._handle_window_float,
            "window/timer": self._handle_window_timer,
            # 数据获取命令（只读）
            "data/roll_call_list": self._handle_get_roll_call_list,
            "data/lottery_list": self._handle_get_lottery_list,
            "data/roll_call_history": self._handle_get_roll_call_history,
            "data/lottery_history": self._handle_get_lottery_history,
        }

        # 设置页面映射
        self.settings_page_map = {
            "basic": "basicSettingsInterface",
            "list": "listManagementInterface",
            "extraction": "extractionSettingsInterface",
            "floating": "floatingWindowManagementInterface",
            "notification": "notificationSettingsInterface",
            "safety": "safetySettingsInterface",
            "custom": "customSettingsInterface",
            "voice": "voiceSettingsInterface",
            "history": "historyInterface",
            "more": "moreSettingsInterface",
            "update": "updateInterface",
            "about": "aboutInterface",
        }

        # 主页面映射
        self.main_page_map = {
            "roll": "roll_call_page",
            "lottery": "lottery_page",
            "history": "history_page",
        }

        logger.debug("URL命令处理器初始化完成")

    def set_security_verifier(self, verifier):
        """设置安全验证器"""
        self.security_verifier = verifier
        logger.debug("安全验证器已设置")

    def handle_url_command(
        self, url: str, require_verification: bool = True
    ) -> Dict[str, Any]:
        """处理URL命令

        Args:
            url: 完整的URL，如 secrandom://settings/basic
            require_verification: 是否需要验证

        Returns:
            处理结果字典
        """
        logger.debug(f"处理URL命令: {url}")
        try:
            logger.debug(f"收到URL命令: {url}")

            # 解析URL
            command, params = self._parse_url(url)
            logger.debug(f"解析URL命令 - 命令: {command}, 参数: {params}")

            # 检查是否需要验证
            if require_verification and self._requires_verification(command):
                logger.debug(f"命令需要验证: {command}")
                return self._request_verification(command, params)

            # 执行命令
            result = self._execute_command(command, params)
            logger.debug(f"URL命令执行成功: {command}, 结果: {result}")
            return result

        except Exception as e:
            logger.exception(f"URL命令处理失败: {e}")
            return {
                "status": "error",
                "message": f"命令处理失败: {str(e)}",
                "command": url,
            }

    def handle_ipc_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理IPC命令

        Args:
            message: IPC消息字典

        Returns:
            处理结果字典
        """
        try:
            command_type = message.get("type", "")
            payload = message.get("payload", {})

            logger.debug(f"收到IPC命令: {command_type}")

            if command_type == "url":
                url = payload.get("url", "")
                require_verification = payload.get("require_verification", True)
                return self.handle_url_command(url, require_verification)

            elif command_type == "direct":
                command = payload.get("command", "")
                params = payload.get("params", {})
                require_verification = payload.get("require_verification", True)

                if require_verification and self._requires_verification(command):
                    return self._request_verification(command, params)

                return self._execute_command(command, params)

            else:
                return {
                    "status": "error",
                    "message": f"不支持的命令类型: {command_type}",
                }

        except Exception as e:
            logger.exception(f"IPC命令处理失败: {e}")
            return {"status": "error", "message": f"IPC命令处理失败: {str(e)}"}

    def _parse_url(self, url: str) -> tuple:
        """解析URL

        Args:
            url: 完整的URL

        Returns:
            (命令, 参数字典) 元组
        """
        logger.debug(f"解析URL: {url}")

        parsed = urlparse(url)
        query = parsed.query or ""

        if parsed.scheme and parsed.scheme.lower() == "secrandom":
            if parsed.netloc and parsed.path:
                full_path = f"{parsed.netloc}{parsed.path}"
            elif parsed.netloc:
                full_path = parsed.netloc
            else:
                full_path = parsed.path

            command = full_path.lstrip("/")
            params = {"args": [], "full_url": f"secrandom://{command}"}

            if query:
                params["query"] = self._parse_query_string(query)
                params["full_url"] = f"{params['full_url']}?{query}"
        else:
            raw = url
            raw_no_scheme = raw
            if raw.lower().startswith("secrandom://"):
                raw_no_scheme = raw[len("secrandom://") :]

            path = (
                raw_no_scheme.split("?")[0] if "?" in raw_no_scheme else raw_no_scheme
            )
            command = path

            params = {"args": [], "full_url": f"secrandom://{raw_no_scheme}"}

            if "?" in raw_no_scheme:
                q = raw_no_scheme.split("?", 1)[1]
                params["query"] = self._parse_query_string(q)

        logger.debug(f"URL解析结果 - 命令: {command}, 参数: {params}")
        return command, params

    def _parse_query_string(self, query: str) -> Dict[str, Any]:
        """解析查询字符串"""
        logger.debug(f"解析查询字符串: {query}")
        if not query:
            logger.debug("查询字符串为空")
            return {}

        params = {}
        for pair in query.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                params[key] = value
        logger.debug(f"查询字符串解析结果: {params}")
        return params

    def _requires_verification(self, command: str) -> bool:
        """检查命令是否需要验证"""
        from app.tools.settings_access import readme_settings_async
        from app.common.safety.password import is_configured as password_is_configured

        if command.startswith("data/"):
            logger.debug(f"命令无需验证（数据只读）：{command}")
            return False

        # 未配置密码则不需要验证
        if not password_is_configured():
            logger.debug(f"命令无需验证（未配置密码）：{command}")
            return False

        # 检查安全总开关
        if not readme_settings_async("basic_safety_settings", "safety_switch"):
            logger.debug(f"命令无需验证（安全总开关关闭）：{command}")
            return False

        if command in (self.secure_commands or []):
            logger.debug(f"命令需验证（自定义受控命令）：{command}")
            return True

        # 命令到操作类型的映射
        command_to_op = {
            "tray/settings": "open_settings",
            "tray/float": "show_hide_floating_window",
            "window/main": None,
            "window/settings": "open_settings",
            "window/float": "show_hide_floating_window",
            "window/timer": None,
            "tray/restart": "restart",
            "tray/exit": "exit",
            "roll_call/quick_draw": None,
            "roll_call/start": None,
            "roll_call/reset": None,
            "lottery/start": None,
            "lottery/reset": None,
        }

        # 操作类型到开关的映射
        op_to_switch = {
            "open_settings": "open_settings_switch",
            "show_hide_floating_window": "show_hide_floating_window_switch",
            "restart": "restart_switch",
            "exit": "exit_switch",
            "roll_call_start": "safety_switch",
            "roll_call_reset": "safety_switch",
            "lottery_start": "safety_switch",
            "lottery_reset": "safety_switch",
            "quick_draw": "safety_switch",
        }

        # 获取操作类型
        op = command_to_op.get(command, None)
        if op is None:
            logger.debug(f"命令无需验证（默认放行）：{command}")
            return False

        # 获取对应的开关
        switch = op_to_switch.get(op)
        if not switch:
            logger.debug(f"命令需验证（默认受控）：{command}")
            return True

        # 检查开关状态
        requires = bool(readme_settings_async("basic_safety_settings", switch))
        logger.debug(
            f"检查命令是否需要验证 - 命令: {command}, 操作: {op}, 开关: {switch}, 结果: {requires}"
        )
        return requires

    def _resolve_settings_page(
        self, command: str, params: Dict[str, Any]
    ) -> Optional[str]:
        if command == "tray/settings":
            return "basicSettingsInterface"

        if command == "settings":
            args = (params or {}).get("args", []) or []
            if not args or (args and args[0] == ""):
                return "basicSettingsInterface"
            page_name = args[0]
            return self.settings_page_map.get(page_name)

        if command.startswith("settings/"):
            name = command.split("/", 1)[1]
            return self.settings_page_map.get(name)

        return None

    def _get_op_and_switch(self, command: str) -> tuple[str, Optional[str]]:
        command_to_op = {
            "tray/settings": "open_settings",
            "tray/float": "show_hide_floating_window",
            "window/main": None,
            "window/settings": "open_settings",
            "window/float": "show_hide_floating_window",
            "window/timer": None,
            "tray/restart": "restart",
            "tray/exit": "exit",
            "roll_call/quick_draw": "quick_draw",
            "roll_call/start": "roll_call_start",
            "roll_call/reset": "roll_call_reset",
            "lottery/start": "lottery_start",
            "lottery/reset": "lottery_reset",
        }

        op_to_switch = {
            "open_settings": "open_settings_switch",
            "show_hide_floating_window": "show_hide_floating_window_switch",
            "restart": "restart_switch",
            "exit": "exit_switch",
            "roll_call_start": "safety_switch",
            "roll_call_reset": "safety_switch",
            "lottery_start": "safety_switch",
            "lottery_reset": "safety_switch",
            "quick_draw": "safety_switch",
        }

        op = command_to_op.get(command, command)
        return op, op_to_switch.get(op)

    def _get_linkage_verification_policy(self, kind: str) -> Dict[str, bool]:
        from app.tools.settings_access import readme_settings_async

        is_non_class_time = False
        try:
            if kind == "roll_call":
                from app.common.roll_call.roll_call_manager import _is_non_class_time

                is_non_class_time = bool(_is_non_class_time())
            elif kind == "lottery":
                from app.common.lottery.lottery_manager import _is_non_class_time

                is_non_class_time = bool(_is_non_class_time())
        except Exception:
            is_non_class_time = False

        verification_required = bool(
            readme_settings_async("linkage_settings", "verification_required")
        )

        return {
            "is_non_class_time": is_non_class_time,
            "verification_required": verification_required,
        }

    def _request_verification(
        self, command: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """请求验证"""
        logger.debug(f"请求验证 - 命令: {command}, 参数: {params}")
        from app.tools.settings_access import readme_settings_async

        op, switch = self._get_op_and_switch(command)
        switch_enabled = (
            bool(readme_settings_async("basic_safety_settings", switch))
            if switch
            else None
        )

        # 创建验证窗口
        from app.page_building.security_window import create_verify_password_window

        def execute_command():
            """验证通过后执行命令"""
            try:
                result = self._execute_command(command, params)
                logger.debug(f"验证后执行命令完成: {command}, 结果: {result}")
                return result
            except Exception as e:
                logger.exception(f"验证后执行命令失败: {command}, 错误: {e}")

        def preview_settings():
            page = self._resolve_settings_page(command, params)
            if page:
                self.showSettingsPreviewRequested.emit(page)

        # 调用验证窗口
        create_verify_password_window(
            on_verified=execute_command,
            on_preview=preview_settings if op == "open_settings" else None,
            operation_type=op,
        )

        return {
            "success": False,
            "error": "需要验证",
            "requires_verification": True,
            "command": command,
            "params": params,
            "operation_type": op,
            "safety_setting_key": switch,
            "safety_setting_enabled": switch_enabled,
            "message": "此命令需要安全验证",
        }

    def _execute_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行命令"""
        logger.debug(f"执行命令: {command}, 参数: {params}")
        try:
            # 查找命令处理器
            handler = self.command_map.get(command)
            if handler:
                logger.debug(f"找到命令处理器 - 命令: {command}")
                try:
                    result = handler(params)
                    logger.debug(f"命令执行成功: {command}, 结果: {result}")
                    return result
                except Exception as e:
                    logger.exception(f"命令执行失败: {command}, 错误: {e}")
                    return {
                        "status": "error",
                        "message": f"命令执行失败: {str(e)}",
                        "command": command,
                    }

            # 尝试模糊匹配
            matched_command = self._fuzzy_match_command(command)
            if matched_command:
                handler = self.command_map.get(matched_command)
                if handler:
                    logger.debug(f"模糊匹配到命令: {matched_command}")
                    try:
                        result = handler(params)
                        logger.debug(
                            f"模糊匹配命令执行成功: {matched_command}, 结果: {result}"
                        )
                        return result
                    except Exception as e:
                        logger.exception(
                            f"模糊匹配命令执行失败: {matched_command}, 错误: {e}"
                        )
                        return {
                            "status": "error",
                            "message": f"命令执行失败: {str(e)}",
                            "command": command,
                        }

            # 未找到匹配命令
            logger.warning(f"未知的命令: {command}")
            return {
                "status": "error",
                "message": f"未知命令: {command}",
                "available_commands": list(self.command_map.keys()),
            }

        except Exception as e:
            logger.exception(f"命令执行失败: {e}")
            return {
                "status": "error",
                "message": f"命令执行失败: {str(e)}",
                "command": command,
            }

    def _fuzzy_match_command(self, command: str) -> Optional[str]:
        """模糊匹配命令"""
        logger.debug(f"模糊匹配命令: {command}")
        available_commands = list(self.command_map.keys())

        # 精确匹配
        if command in available_commands:
            logger.debug(f"精确匹配到命令: {command}")
            return command

        # 前缀匹配
        for cmd in available_commands:
            if cmd.startswith(command):
                logger.debug(f"前缀匹配到命令: {cmd} (输入: {command})")
                return cmd

        # 后缀匹配
        for cmd in available_commands:
            if cmd.endswith(command):
                logger.debug(f"后缀匹配到命令: {cmd} (输入: {command})")
                return cmd

        # 包含匹配
        for cmd in available_commands:
            if command in cmd:
                logger.debug(f"包含匹配到命令: {cmd} (输入: {command})")
                return cmd

        logger.debug(f"未匹配到命令: {command}")
        return None

    # ==================================================
    # 具体命令处理器
    # ==================================================

    def _handle_basic_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理基础设置"""
        logger.debug("打开基础设置页面")
        self.showSettingsRequested.emit("basicSettingsInterface")
        return {
            "status": "success",
            "message": "基础设置页面已打开",
            "page": "basicSettingsInterface",
        }

    def _handle_list_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理列表管理设置"""
        logger.debug("打开列表管理设置页面")
        self.showSettingsRequested.emit("listManagementInterface")
        return {
            "status": "success",
            "message": "列表管理设置页面已打开",
            "page": "listManagementInterface",
        }

    def _handle_extraction_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理抽取设置"""
        logger.debug("打开抽取设置页面")
        self.showSettingsRequested.emit("extractionSettingsInterface")
        return {
            "status": "success",
            "message": "抽取设置页面已打开",
            "page": "extractionSettingsInterface",
        }

    def _handle_floating_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理浮窗设置"""
        logger.debug("打开浮窗设置页面")
        self.showSettingsRequested.emit("floatingWindowManagementInterface")
        return {
            "status": "success",
            "message": "浮窗设置页面已打开",
            "page": "floatingWindowManagementInterface",
        }

    def _handle_notification_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理通知设置"""
        logger.debug("打开通知设置页面")
        self.showSettingsRequested.emit("notificationSettingsInterface")
        return {
            "status": "success",
            "message": "通知设置页面已打开",
            "page": "notificationSettingsInterface",
        }

    def _handle_safety_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理安全设置"""
        logger.debug("打开安全设置页面")
        self.showSettingsRequested.emit("safetySettingsInterface")
        return {
            "status": "success",
            "message": "安全设置页面已打开",
            "page": "safetySettingsInterface",
        }

    def _handle_custom_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理自定义设置"""
        logger.debug("打开自定义设置页面")
        self.showSettingsRequested.emit("customSettingsInterface")
        return {
            "status": "success",
            "message": "自定义设置页面已打开",
            "page": "customSettingsInterface",
        }

    def _handle_voice_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理语音设置"""
        logger.debug("打开语音设置页面")
        self.showSettingsRequested.emit("voiceSettingsInterface")
        return {
            "status": "success",
            "message": "语音设置页面已打开",
            "page": "voiceSettingsInterface",
        }

    def _handle_history_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理历史记录设置"""
        logger.debug("打开历史记录设置页面")
        self.showSettingsRequested.emit("historyInterface")
        return {
            "status": "success",
            "message": "历史记录设置页面已打开",
            "page": "historyInterface",
        }

    def _handle_more_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理更多设置"""
        logger.debug("打开更多设置页面")
        self.showSettingsRequested.emit("moreSettingsInterface")
        return {
            "status": "success",
            "message": "更多设置页面已打开",
            "page": "moreSettingsInterface",
        }

    def _handle_update_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理更新设置"""
        logger.debug("打开更新设置页面")
        self.showSettingsRequested.emit("updateInterface")
        return {
            "status": "success",
            "message": "更新设置页面已打开",
            "page": "updateInterface",
        }

    def _handle_about_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理关于设置"""
        logger.debug("打开关于设置页面")
        self.showSettingsRequested.emit("aboutInterface")
        return {
            "status": "success",
            "message": "关于设置页面已打开",
            "page": "aboutInterface",
        }

    def _handle_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理设置命令"""
        args = params.get("args", [])

        # 如果 args 为空或者 args 中的第一个元素为空字符串，默认打开基本设置页面
        if not args or (args and args[0] == ""):
            # 默认打开基本设置页面
            logger.debug("打开设置界面 - 基本设置")
            self.showSettingsRequested.emit("basicSettingsInterface")
            return {"status": "success", "message": "设置界面已打开"}

        # 处理特定的设置页面
        page_name = args[0]
        logger.debug(f"打开设置页面: {page_name}")

        # 映射设置页面名称
        page_mapping = {
            "basic": "basicSettingsInterface",
            "list": "listManagementInterface",
            "extraction": "extractionSettingsInterface",
            "floating": "floatingWindowManagementInterface",
            "notification": "notificationSettingsInterface",
            "safety": "safetySettingsInterface",
            "voice": "voiceSettingsInterface",
            "history": "historyInterface",
            "more": "moreSettingsInterface",
            "update": "updateInterface",
            "about": "aboutInterface",
        }

        if page_name in page_mapping:
            mapped_page = page_mapping[page_name]
            logger.debug(f"切换到设置页面: {mapped_page}")
            self.showSettingsRequested.emit(mapped_page)
            return {
                "status": "success",
                "message": f"设置页面 '{page_name}' 已打开",
                "page": mapped_page,
            }
        else:
            logger.warning(f"未知的设置页面: {page_name}")
            return {
                "status": "error",
                "message": f"不支持的设置页面: {page_name}",
                "available_pages": list(page_mapping.keys()),
            }

    def _handle_roll_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理抽人功能"""
        logger.debug("切换到抽人页面")
        self.showMainPageRequested.emit("roll_call_page")
        return {
            "status": "success",
            "message": "已切换到抽人页面",
            "page": "roll_call_page",
        }

    def _handle_roll_call_quick_draw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求执行闪抽")
        policy = self._get_linkage_verification_policy("roll_call")
        if policy.get("is_non_class_time") and not policy.get("verification_required"):
            return {
                "status": "error",
                "message": "当前时间在非上课时间段内，禁止抽取",
                **policy,
            }
        self.rollCallActionRequested.emit("quick_draw", params or {})
        return {"status": "success", "message": "已请求执行闪抽", **policy}

    def _handle_roll_call_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求开始点名")
        policy = self._get_linkage_verification_policy("roll_call")
        if policy.get("is_non_class_time") and not policy.get("verification_required"):
            return {
                "status": "error",
                "message": "当前时间在非上课时间段内，禁止抽取",
                **policy,
            }
        self.rollCallActionRequested.emit("start", params or {})
        return {"status": "success", "message": "已请求开始点名", **policy}

    def _handle_roll_call_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求停止点名")
        self.rollCallActionRequested.emit("stop", params or {})
        return {"status": "success", "message": "已请求停止点名"}

    def _handle_roll_call_reset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求重置点名记录")
        policy = self._get_linkage_verification_policy("roll_call")
        if policy.get("is_non_class_time") and not policy.get("verification_required"):
            return {
                "status": "error",
                "message": "当前时间在非上课时间段内，禁止重置",
                **policy,
            }
        self.rollCallActionRequested.emit("reset", params or {})
        return {"status": "success", "message": "已请求重置点名记录", **policy}

    def _handle_roll_call_set_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        raw = query.get("count") or query.get("value") or query.get("draw_count")
        try:
            count = int(raw)
        except Exception:
            return {"status": "error", "message": "参数无效: count"}
        if count <= 0:
            return {"status": "error", "message": "参数无效: count"}
        self.rollCallActionRequested.emit(
            "set_count", {"count": count, **(params or {})}
        )
        return {"status": "success", "message": "已请求设置点名人数", "count": count}

    def _handle_roll_call_set_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        group = query.get("group") or query.get("value") or query.get("text")
        index = query.get("index") or query.get("group_index")
        payload: Dict[str, Any] = {"group": group, "index": index}
        self.rollCallActionRequested.emit("set_group", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置点名小组/范围", **payload}

    def _handle_roll_call_set_gender(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        gender = query.get("gender") or query.get("value") or query.get("text")
        index = query.get("index") or query.get("gender_index")
        payload: Dict[str, Any] = {"gender": gender, "index": index}
        self.rollCallActionRequested.emit("set_gender", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置点名性别", **payload}

    def _handle_roll_call_set_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        class_name = (
            query.get("class_name")
            or query.get("class")
            or query.get("name")
            or query.get("className")
            or query.get("value")
            or query.get("text")
        )
        index = query.get("index")
        payload: Dict[str, Any] = {"class_name": class_name, "index": index}
        self.rollCallActionRequested.emit("set_list", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置点名名单", **payload}

    def _handle_lottery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理抽奖功能"""
        logger.debug("URLCommandHandler._handle_lottery: 切换到抽奖页面")
        logger.debug(
            "URLCommandHandler._handle_lottery: 发出 showMainPageRequested 信号，参数: 'lottery_page'"
        )
        self.showMainPageRequested.emit("lottery_page")
        return {
            "status": "success",
            "message": "已切换到抽奖页面",
            "page": "lottery_page",
        }

    def _handle_lottery_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求开始抽奖")
        policy = self._get_linkage_verification_policy("lottery")
        if policy.get("is_non_class_time") and not policy.get("verification_required"):
            return {
                "status": "error",
                "message": "当前时间在非上课时间段内，禁止抽取",
                **policy,
            }
        self.lotteryActionRequested.emit("start", params or {})
        return {"status": "success", "message": "已请求开始抽奖", **policy}

    def _handle_lottery_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求停止抽奖")
        self.lotteryActionRequested.emit("stop", params or {})
        return {"status": "success", "message": "已请求停止抽奖"}

    def _handle_lottery_reset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("请求重置抽奖记录")
        policy = self._get_linkage_verification_policy("lottery")
        if policy.get("is_non_class_time") and not policy.get("verification_required"):
            return {
                "status": "error",
                "message": "当前时间在非上课时间段内，禁止重置",
                **policy,
            }
        self.lotteryActionRequested.emit("reset", params or {})
        return {"status": "success", "message": "已请求重置抽奖记录", **policy}

    def _handle_lottery_set_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        raw = query.get("count") or query.get("value") or query.get("draw_count")
        try:
            count = int(raw)
        except Exception:
            return {"status": "error", "message": "参数无效: count"}
        if count <= 0:
            return {"status": "error", "message": "参数无效: count"}
        self.lotteryActionRequested.emit(
            "set_count", {"count": count, **(params or {})}
        )
        return {"status": "success", "message": "已请求设置抽奖数量", "count": count}

    def _handle_lottery_set_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        pool_name = (
            query.get("pool_name")
            or query.get("pool")
            or query.get("name")
            or query.get("poolName")
            or query.get("value")
            or query.get("text")
        )
        index = query.get("index")
        payload: Dict[str, Any] = {"pool_name": pool_name, "index": index}
        self.lotteryActionRequested.emit("set_pool", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置抽奖奖池", **payload}

    def _handle_lottery_set_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        value = query.get("range") or query.get("value") or query.get("text")
        index = query.get("index") or query.get("range_index")
        payload: Dict[str, Any] = {"range": value, "index": index}
        self.lotteryActionRequested.emit("set_range", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置抽奖范围", **payload}

    def _handle_lottery_set_gender(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        value = query.get("gender") or query.get("value") or query.get("text")
        index = query.get("index") or query.get("gender_index")
        payload: Dict[str, Any] = {"gender": value, "index": index}
        self.lotteryActionRequested.emit("set_gender", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置抽奖性别", **payload}

    def _handle_lottery_set_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        class_name = (
            query.get("class_name")
            or query.get("class")
            or query.get("name")
            or query.get("className")
            or query.get("value")
            or query.get("text")
        )
        index = query.get("index")
        payload: Dict[str, Any] = {"class_name": class_name, "index": index}
        self.lotteryActionRequested.emit("set_list", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置抽奖点名名单", **payload}

    def _resolve_window_action(self, query: Dict[str, Any]) -> str:
        raw = (
            query.get("action")
            or query.get("mode")
            or query.get("op")
            or query.get("do")
            or ""
        )
        action = str(raw).strip().lower()
        if action in ("toggle", "switch"):
            return "toggle"
        if action in ("show", "open", "1", "true", "yes", "on"):
            return "show"
        if action in ("hide", "close", "0", "false", "no", "off"):
            return "hide"
        visible = query.get("visible")
        if visible is not None:
            v = str(visible).strip().lower()
            if v in ("1", "true", "yes", "on"):
                return "show"
            if v in ("0", "false", "no", "off"):
                return "hide"
        return "toggle"

    def _handle_window_main(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        action = self._resolve_window_action(query)
        page = (
            query.get("page")
            or query.get("page_name")
            or query.get("name")
            or query.get("value")
        )
        page_name = None
        if isinstance(page, str) and page.strip():
            raw = page.strip()
            page_name = self.main_page_map.get(raw, raw)

        payload: Dict[str, Any] = {"action": action}
        if page_name:
            payload["page"] = page_name

        self.windowActionRequested.emit("main", {**payload, **(params or {})})
        result: Dict[str, Any] = {
            "status": "success",
            "message": "已请求主窗口操作",
            "action": action,
        }
        if page_name:
            result["page"] = page_name
        return result

    def _handle_window_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        action = self._resolve_window_action(query)
        page = (
            query.get("page")
            or query.get("page_name")
            or query.get("name")
            or query.get("value")
        )
        preview = query.get("preview")
        is_preview = False
        if preview is not None:
            v = str(preview).strip().lower()
            is_preview = v in ("1", "true", "yes", "on")
        payload: Dict[str, Any] = {
            "action": action,
            "page": page,
            "is_preview": is_preview,
        }
        self.windowActionRequested.emit("settings", {**payload, **(params or {})})
        return {"status": "success", "message": "已请求设置窗口操作", **payload}

    def _handle_window_float(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        action = self._resolve_window_action(query)
        self.windowActionRequested.emit("float", {"action": action, **(params or {})})
        return {"status": "success", "message": "已请求浮窗操作", "action": action}

    def _handle_window_timer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = (params or {}).get("query", {}) or {}
        action = self._resolve_window_action(query)
        self.windowActionRequested.emit("timer", {"action": action, **(params or {})})
        return {
            "status": "success",
            "message": "已请求计时器窗口操作",
            "action": action,
        }

    def _handle_main_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理主窗口命令"""
        args = params.get("args", [])
        if args:
            page = args[0]
            if page in self.main_page_map:
                page_name = self.main_page_map[page]
                self.showMainPageRequested.emit(page_name)
                return {
                    "status": "success",
                    "message": f"已切换到{page}页面",
                    "page": page_name,
                }

        # 默认显示主窗口
        self.showMainPageRequested.emit("main_window")
        return {"status": "success", "message": "主窗口已显示", "page": "main_window"}

    def _handle_tray_toggle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理托盘切换"""
        logger.debug("切换主窗口显示状态")
        self.showTrayActionRequested.emit("toggle_main_window")
        return {"status": "success", "message": "主窗口显示状态已切换"}

    def _handle_tray_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理托盘设置"""
        logger.debug("打开设置界面")
        self.showSettingsRequested.emit("basicSettingsInterface")
        return {"status": "success", "message": "设置界面已打开"}

    def _handle_tray_float(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理托盘浮窗"""
        logger.debug("切换浮窗显示状态")
        self.showTrayActionRequested.emit("float")
        return {"status": "success", "message": "浮窗显示状态已切换"}

    def _handle_tray_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理托盘重启"""
        logger.debug("执行重启操作")
        self.showTrayActionRequested.emit("restart")
        return {"status": "success", "message": "应用重启中..."}

    def _handle_tray_exit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理托盘退出"""
        logger.debug("执行退出操作")
        self.showTrayActionRequested.emit("exit")
        return {"status": "success", "message": "应用退出中..."}

    def _handle_get_roll_call_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取点名名单（只读）"""
        from app.common.data.list import get_student_list

        query = params.get("query", {}) or {}
        class_name = (
            query.get("class_name")
            or query.get("class")
            or query.get("name")
            or query.get("className")
        )

        if not class_name:
            return {
                "status": "error",
                "message": "缺少参数: class_name",
            }

        student_list = get_student_list(class_name)
        return {
            "status": "success",
            "message": "点名名单获取成功",
            "class_name": class_name,
            "data": student_list,
        }

    def _handle_get_lottery_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取抽奖名单（只读）"""
        from app.common.data.list import get_pool_list

        query = params.get("query", {}) or {}
        pool_name = (
            query.get("pool_name")
            or query.get("pool")
            or query.get("name")
            or query.get("poolName")
        )

        if not pool_name:
            return {
                "status": "error",
                "message": "缺少参数: pool_name",
            }

        pool_list = get_pool_list(pool_name)
        return {
            "status": "success",
            "message": "抽奖名单获取成功",
            "pool_name": pool_name,
            "data": pool_list,
        }

    def _handle_get_roll_call_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取点名历史记录（只读）"""
        from app.common.history.history_reader import get_roll_call_history_data

        query = params.get("query", {}) or {}
        class_name = (
            query.get("class_name")
            or query.get("class")
            or query.get("name")
            or query.get("className")
        )

        if not class_name:
            return {
                "status": "error",
                "message": "缺少参数: class_name",
            }

        history_data = get_roll_call_history_data(class_name)
        return {
            "status": "success",
            "message": "点名历史记录获取成功",
            "class_name": class_name,
            "data": history_data,
        }

    def _handle_get_lottery_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取抽奖历史记录（只读）"""
        from app.common.history.history_reader import get_lottery_history_data

        query = params.get("query", {}) or {}
        pool_name = (
            query.get("pool_name")
            or query.get("pool")
            or query.get("name")
            or query.get("poolName")
        )

        if not pool_name:
            return {
                "status": "error",
                "message": "缺少参数: pool_name",
            }

        history_data = get_lottery_history_data(pool_name)
        return {
            "status": "success",
            "message": "抽奖历史记录获取成功",
            "pool_name": pool_name,
            "data": history_data,
        }

    def register_command(
        self,
        command: str,
        handler: Callable,
        description: str = "",
        require_verification: bool = False,
    ):
        """
        注册自定义命令

        Args:
            command: 命令名称
            handler: 命令处理器函数
            description: 命令描述
            require_verification: 是否需要验证
        """
        logger.debug(
            f"注册自定义命令 - 命令: {command}, 需要验证: {require_verification}"
        )
        self.command_map[command] = handler
        if require_verification:
            self.secure_commands.append(command)
        logger.debug(f"注册自定义命令: {command}")

    def unregister_command(self, command: str):
        """注销自定义命令"""
        logger.debug(f"注销自定义命令: {command}")
        if command in self.command_map:
            del self.command_map[command]
            if command in self.secure_commands:
                self.secure_commands.remove(command)
            logger.debug(f"注销自定义命令: {command}")
        else:
            logger.warning(f"尝试注销不存在的命令: {command}")

    def get_available_commands(self) -> List[Dict[str, Any]]:
        """获取可用命令列表"""
        logger.debug("获取可用命令列表")
        commands = []
        for name, handler in self.command_map.items():
            commands.append(
                {
                    "name": name,
                    "description": getattr(handler, "__doc__", "无描述") or "无描述",
                    "handler": handler.__name__
                    if hasattr(handler, "__name__")
                    else str(handler),
                }
            )
        logger.debug(f"可用命令数量: {len(commands)}")
        return commands

    def verify_and_execute(
        self, command: str, params: Dict[str, Any], verification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证并执行命令"""
        logger.debug(
            f"验证并执行命令 - 命令: {command}, 参数: {params}, 验证数据: {verification_data}"
        )

        if not self.security_verifier:
            logger.exception("安全验证器未配置")
            return {"success": False, "error": "安全验证器未配置"}

        # 执行安全验证
        logger.debug("执行安全验证")
        verification_result = self.security_verifier.verify(verification_data)
        if not verification_result["success"]:
            logger.warning(f"安全验证失败: {verification_result}")
            return verification_result

        logger.debug("安全验证通过，执行命令")
        # 执行命令
        result = self._execute_command(command, params)
        logger.debug(f"验证并执行命令完成 - 命令: {command}, 结果: {result}")
        return result
