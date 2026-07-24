import os
import base64
import hmac
import hashlib
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
    rec = d.get("password")
    ok = isinstance(rec, dict) and bool(rec.get("hash")) and bool(rec.get("salt"))
    logger.debug(f"密码已配置：{ok}")
    return ok


def set_password(plain: str):
    salt = os.urandom(16)
    iterations = 200000
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
    rec = {
        "algorithm": "pbkdf2_sha256",
        "iterations": iterations,
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": base64.b64encode(dk).decode("ascii"),
    }
    d = _read()
    d["password"] = rec
    _write(d)
    logger.debug("密码设置已保存")


def verify_password(plain: str) -> bool:
    d = _read()
    rec = d.get("password")
    if not rec:
        return False
    try:
        salt = base64.b64decode(rec.get("salt", ""))
        iterations = int(rec.get("iterations", 200000))
        expected = base64.b64decode(rec.get("hash", ""))
    except Exception:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
    ok = hmac.compare_digest(dk, expected)
    logger.debug(f"密码验证结果：{ok}")
    return ok


def clear_password():
    d = _read()
    if "password" in d:
        del d["password"]
    _write(d)
    logger.debug("已清除密码配置")


# 使用 secure_store 统一读写
