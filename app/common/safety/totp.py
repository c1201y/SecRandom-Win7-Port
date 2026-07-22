from __future__ import annotations
import pyotp
from loguru import logger

from app.tools.path_utils import (
    get_config_path,
    get_settings_path,
)
from app.common.safety.secure_store import read_secrets, write_secrets

try:
    from Cryptodome.Cipher import AES
except Exception:
    try:
        from Crypto.Cipher import AES
    except Exception:
        AES = None


def _secrets_path():
    return get_settings_path("secrets.json")


def _legacy_path():
    return get_config_path("security", "secrets.json")


def _read():
    return read_secrets()


def _write(d):
    write_secrets(d)


def is_configured():
    d = _read()
    rec = d.get("totp")
    ok = isinstance(rec, dict) and bool(rec.get("secret"))
    logger.debug(f"TOTP已配置：{ok}")
    return ok


def generate_secret():
    return pyotp.random_base32()


def set_totp(
    secret: str | None, issuer: str = "SecRandom", account: str = "user"
) -> str:
    if not secret:
        secret = generate_secret()
    d = _read()
    d["totp"] = {"secret": secret, "issuer": issuer, "account": account}
    _write(d)
    totp = pyotp.TOTP(secret)
    logger.debug("TOTP设置已保存")
    return totp.provisioning_uri(name=account, issuer_name=issuer)


def verify(code: str, window: int = 1) -> bool:
    d = _read()
    rec = d.get("totp")
    if not rec:
        return False
    secret = rec.get("secret")
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    try:
        ok = bool(totp.verify(code, valid_window=window))
        logger.debug(f"TOTP验证结果：{ok}")
        return ok
    except Exception:
        logger.warning("TOTP验证异常")
        return False


# 使用 secure_store 统一读写
