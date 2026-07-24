from app.tools.settings_access import readme_settings_async
from app.common.safety.password import is_configured as password_is_configured
from app.page_building.security_window import create_verify_password_window
from loguru import logger


def should_require_password(op: str) -> bool:
    if not password_is_configured():
        logger.debug(f"操作无需验证（未配置密码）：{op}")
        return False

    # 特殊处理：切换安全总开关本身需要验证
    if op == "toggle_safety":
        logger.debug(f"操作需验证（切换安全总开关）：{op}")
        return True

    if not readme_settings_async("basic_safety_settings", "safety_switch"):
        logger.debug(f"操作无需验证（安全总开关关闭）：{op}")
        return False

    key_map = {
        "show_hide_floating_window": "show_hide_floating_window_switch",
        "restart": "restart_switch",
        "exit": "exit_switch",
        "set_totp": "safety_switch",
        "bind_usb": "safety_switch",
        "unbind_usb": "safety_switch",
        "toggle_totp": "safety_switch",
        "toggle_usb": "safety_switch",
        "change_verification_process": "safety_switch",
        "toggle_show_hide_floating_window_switch": "safety_switch",
        "toggle_restart_switch": "safety_switch",
        "toggle_exit_switch": "safety_switch",
        "open_settings": "open_settings_switch",
        "toggle_open_settings_switch": "safety_switch",
        "roll_call_start": "safety_switch",
        "roll_call_reset": "safety_switch",
        "lottery_start": "safety_switch",
        "lottery_reset": "safety_switch",
        "quick_draw": "safety_switch",
    }
    k = key_map.get(op)
    if not k:
        logger.debug(f"操作需验证（默认受控）：{op}")
        return True
    ok = bool(readme_settings_async("basic_safety_settings", k))
    logger.debug(f"操作需验证：{op} -> {ok}")
    return ok


def require_and_run(op: str, parent, func, on_preview=None):
    if not should_require_password(op):
        func()
        return
    logger.debug(f"触发验证窗口：{op}")
    create_verify_password_window(
        on_verified=func, on_preview=on_preview, operation_type=op
    )
