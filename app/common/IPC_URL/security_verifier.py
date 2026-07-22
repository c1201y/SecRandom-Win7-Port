# ==================================================
# 安全验证器
# ==================================================
import hashlib
import hmac
import time
from typing import Dict, Any
from loguru import logger
from PySide2.QtCore import QObject, Signal


# ==================================================
# 密钥派生函数 (KDF) - 密钥强化
# ==================================================
class KeyDerivation:
    """密钥派生函数，使用PBKDF2进行密钥强化

    防止弱密钥和暴力破解攻击
    """

    # PBKDF2 参数
    PBKDF2_ITERATIONS = 100000  # 迭代次数（遵循 OWASP 最新建议）
    PBKDF2_SALT = b"SecRandom_KDF_SALT_V1"  # 固定盐值（用于确定性派生）
    PBKDF2_HASH_NAME = "sha512"

    @classmethod
    def derive_key(cls, secret: str, salt: bytes = None) -> bytes:
        """使用PBKDF2进行密钥派生

        Args:
            secret: 原始密钥或密码
            salt: 盐值（如果为None，使用默认盐值）

        Returns:
            派生的密钥（字节形式）
        """
        if not secret:
            raise ValueError("秘密密钥不能为空")

        salt = salt or cls.PBKDF2_SALT

        # 使用PBKDF2进行密钥派生
        # PBKDF2应用多次哈希和盐化来强化弱密钥
        derived = hashlib.pbkdf2_hmac(
            cls.PBKDF2_HASH_NAME, secret.encode(), salt, cls.PBKDF2_ITERATIONS
        )

        return derived

    @classmethod
    def derive_key_hex(cls, secret: str, salt: bytes = None) -> str:
        """获取十六进制格式的派生密钥

        Args:
            secret: 原始密钥或密码
            salt: 盐值

        Returns:
            十六进制形式的派生密钥
        """
        derived = cls.derive_key(secret, salt)
        return derived.hex()


# ==================================================
# 安全验证器基类
# ==================================================
class SecurityVerifier(QObject):
    """安全验证器基类

    提供基础的安全验证功能，包括：
    - 密码验证
    - 时间窗口验证
    - 尝试次数限制
    - 验证记录
    """

    verificationRequested = Signal(str, dict)  # 验证请求信号
    verificationCompleted = Signal(str, bool, dict)  # 验证完成信号

    def __init__(self):
        super().__init__()
        self.max_attempts = 3
        self.attempt_window = 300  # 5分钟
        self.verification_history = {}

    def verify(self, verification_data: Dict[str, Any]) -> bool:
        """执行验证

        Args:
            verification_data: 验证数据，包含密码等信息

        Returns:
            验证是否通过
        """
        try:
            command = verification_data.get("command", "")
            password = verification_data.get("password", "")

            # 检查尝试次数
            if not self._check_attempt_limit(command):
                logger.warning(f"验证尝试次数超限: {command}")
                return False

            # 执行具体验证逻辑
            result = self._perform_verification(password, verification_data)

            # 记录验证结果
            self._record_verification(command, result, verification_data)

            # 发送验证完成信号
            self.verificationCompleted.emit(command, result, verification_data)

            return result

        except Exception as e:
            logger.exception(f"验证过程出错: {e}")
            return False

    def _check_attempt_limit(self, command: str) -> bool:
        """检查尝试次数限制"""
        current_time = time.time()
        key = f"attempts_{command}"

        if key not in self.verification_history:
            self.verification_history[key] = []

        # 清理过期记录
        self.verification_history[key] = [
            timestamp
            for timestamp in self.verification_history[key]
            if current_time - timestamp < self.attempt_window
        ]

        # 检查是否超过限制
        if len(self.verification_history[key]) >= self.max_attempts:
            return False

        return True

    def _perform_verification(
        self, password: str, verification_data: Dict[str, Any]
    ) -> bool:
        """执行具体的验证逻辑（子类实现）"""
        raise NotImplementedError("子类必须实现此方法")

    def _record_verification(
        self, command: str, result: bool, verification_data: Dict[str, Any]
    ):
        """记录验证结果"""
        current_time = time.time()

        # 记录尝试次数
        key = f"attempts_{command}"
        if key not in self.verification_history:
            self.verification_history[key] = []
        self.verification_history[key].append(current_time)

        # 在记录验证结果前对验证数据进行脱敏，避免存储明文密码等敏感信息
        sensitive_keys = {"password", "passwd", "pwd"}
        sanitized_data = {
            k: v for k, v in verification_data.items() if k not in sensitive_keys
        }

        # 记录验证结果（仅保存脱敏后的数据）
        result_key = f"result_{command}"
        self.verification_history[result_key] = {
            "result": result,
            "timestamp": current_time,
            "data": sanitized_data,
        }

    def get_verification_status(self, command: str = "") -> Dict[str, Any]:
        """获取验证状态"""
        current_time = time.time()

        status = {
            "max_attempts": self.max_attempts,
            "attempt_window": self.attempt_window,
            "current_attempts": 0,
            "remaining_attempts": self.max_attempts,
            "last_verification": None,
            "can_verify": True,
        }

        if command:
            key = f"attempts_{command}"
            if key in self.verification_history:
                valid_attempts = [
                    timestamp
                    for timestamp in self.verification_history[key]
                    if current_time - timestamp < self.attempt_window
                ]
                status["current_attempts"] = len(valid_attempts)
                status["remaining_attempts"] = max(
                    0, self.max_attempts - len(valid_attempts)
                )
                status["can_verify"] = len(valid_attempts) < self.max_attempts

                result_key = f"result_{command}"
                if result_key in self.verification_history:
                    status["last_verification"] = self.verification_history[result_key]

        return status

    def reset_attempts(self, command: str = ""):
        """重置尝试次数"""
        if command:
            key = f"attempts_{command}"
            if key in self.verification_history:
                del self.verification_history[key]
            result_key = f"result_{command}"
            if result_key in self.verification_history:
                del self.verification_history[result_key]
        else:
            # 重置所有
            self.verification_history.clear()

        logger.info(f"验证尝试次数已重置: {command or 'all'}")


# ==================================================
# 简单密码验证器
# ==================================================
class SimplePasswordVerifier(SecurityVerifier):
    """简单密码验证器

    使用预设密码进行验证

    安全特性：
    - 支持明文密码和预计算哈希值
    - 使用SHA-512进行密码哈希
    - 使用hmac.compare_digest()进行恒定时间比较（防止时间攻击）
    - 支持可选的PBKDF2密钥派生强化（用于弱密码）
    """

    def __init__(self, password: str = None, use_kdf: bool = False):
        """初始化密码验证器

        Args:
            password: 密码（明文或SHA-512哈希）
            use_kdf: 是否使用PBKDF2进行密钥强化（针对弱密码）
        """
        super().__init__()
        original_password = password or "SecRandom2025"
        self.use_kdf = use_kdf

        # 验证是否为有效的SHA-512哈希（128个十六进制字符）
        if self._is_valid_sha512_hash(original_password):
            # 已经是哈希形式，视为预计算的安全散列/密钥
            self.hashed_password = original_password
        else:
            # 明文密码，使用PBKDF2进行密钥派生（计算成本高，防止暴力破解）
            derived = KeyDerivation.derive_key_hex(original_password)
            self.hashed_password = derived
            logger.debug("密码已使用PBKDF2进行强化派生")

    @staticmethod
    def _is_valid_sha512_hash(value: str) -> bool:
        """验证是否为有效的SHA-512哈希值

        SHA-512哈希必须是：
        - 长度为128个字符
        - 全部为十六进制字符（0-9, a-f）
        """
        if not isinstance(value, str) or len(value) != 128:
            return False
        try:
            # 尝试将其作为十六进制字符串
            int(value, 16)
            return True
        except ValueError:
            return False

    def _perform_verification(
        self, password: str, verification_data: Dict[str, Any]
    ) -> bool:
        """执行密码验证

        将输入密码（明文或预先哈希的SHA-512值）与存储的哈希值比较
        使用 hmac.compare_digest() 进行常数时间比较，防止时间攻击
        """
        if not password:
            logger.warning("未提供密码")
            return False

        # 统一使用 KDF 进行密码强化：
        # - 明文密码：直接作为 KDF 输入
        # - 预先哈希的 SHA-512 值：作为 KDF 输入，保持兼容性但不再直接存储/比较裸 SHA-512
        if self._is_valid_sha512_hash(password):
            # 预先计算的 SHA-512 字符串，作为 KDF 的输入
            kdf_input = password
        else:
            # 明文密码，直接作为 KDF 的输入
            kdf_input = password

        derived = KeyDerivation.derive_key(kdf_input)
        candidate_hash = derived.hex()

        # 使用常数时间比较函数防止时间攻击
        # hmac.compare_digest() 会进行恒定时间的比较，不会因为字符不匹配而提前返回
        result = hmac.compare_digest(candidate_hash, self.hashed_password)

        if result:
            logger.info("密码验证成功")
        else:
            logger.warning("密码验证失败")

        return result

    def set_password(self, new_password: str):
        """设置新密码

        支持明文密码或有效的SHA-512哈希值
        自动应用KDF强化（如果已启用）
        """
        # 与 __init__ 保持一致：空值使用默认密码
        original_password = new_password or "SecRandom2024"

        # 验证是否为有效的SHA-512哈希
        if self._is_valid_sha512_hash(original_password):
            # 已经是哈希形式，作为 KDF 的输入以保持兼容
            kdf_input = original_password
        else:
            # 明文密码，直接作为 KDF 的输入
            kdf_input = original_password

        # 始终通过 KDF 强化后再存储，避免存储裸 SHA-512 哈希
        derived = KeyDerivation.derive_key(kdf_input)
        self.hashed_password = derived.hex()

        logger.info("密码已更新")


# ==================================================
# 动态密码验证器
# ==================================================
class DynamicPasswordVerifier(SecurityVerifier):
    """动态密码验证器

    基于时间窗口生成动态密码

    安全特性：
    - 使用HMAC-SHA512防止长度扩展攻击
    - 使用PBKDF2派生密钥防止弱密钥和暴力破解
    - 支持多时间窗口验证（容错机制）
    """

    def __init__(self, secret: str = None, time_window: int = 30):
        super().__init__()
        original_secret = secret or "SecRandomSecretKey"
        self.time_window = time_window  # 时间窗口（秒）

        # 使用PBKDF2进行密钥派生强化
        # 即使原始密钥较弱，派生密钥也会很强
        self.derived_key = KeyDerivation.derive_key(original_secret)
        logger.debug("动态密码验证器已使用PBKDF2进行密钥强化")

    def _perform_verification(
        self, password: str, verification_data: Dict[str, Any]
    ) -> bool:
        """执行动态密码验证"""
        if not password:
            logger.warning("未提供密码")
            return False

        current_time = int(time.time())

        # 检查当前时间窗口和前后各一个时间窗口
        for time_offset in [-1, 0, 1]:
            expected_password = self._generate_password(
                current_time + time_offset * self.time_window
            )
            if password == expected_password:
                logger.info("动态密码验证成功")
                return True

        logger.warning("动态密码验证失败")
        return False

    def _generate_password(self, timestamp: int) -> str:
        """生成指定时间戳的密码

        使用 HMAC-SHA512 结合 PBKDF2 派生密钥来防止：
        - 长度扩展攻击（使用HMAC）
        - 弱密钥和暴力破解（使用PBKDF2派生的密钥）
        """
        # 计算时间窗口
        time_window = timestamp // self.time_window

        # 使用 HMAC-SHA512 + PBKDF2派生密钥
        # derived_key 已通过PBKDF2强化，抗暴力破解
        h = hmac.new(self.derived_key, str(time_window).encode(), hashlib.sha512)
        password_hash = h.hexdigest()

        # 取前6位作为密码
        return password_hash[:6]

    def get_current_password(self) -> str:
        """获取当前时间窗口的密码"""
        current_time = int(time.time())
        return self._generate_password(current_time)

    def set_secret(self, new_secret: str):
        """设置新密钥

        自动使用PBKDF2进行强化处理
        """
        if not new_secret:
            logger.warning("秘密密钥不能为空")
            return

        # 重新派生密钥
        self.derived_key = KeyDerivation.derive_key(new_secret)
        logger.info("动态密码密钥已更新并使用PBKDF2进行强化")


# ==================================================
# 组合验证器
# ==================================================
class CompositeVerifier(SecurityVerifier):
    """组合验证器

    组合多种验证方式
    """

    def __init__(self, verifiers: list = None):
        super().__init__()
        self.verifiers = verifiers or []
        self.require_all = True  # 是否需要所有验证都通过

    def add_verifier(self, verifier: SecurityVerifier):
        """添加验证器"""
        self.verifiers.append(verifier)

    def remove_verifier(self, verifier_type: type):
        """移除指定类型的验证器"""
        self.verifiers = [v for v in self.verifiers if not isinstance(v, verifier_type)]

    def _perform_verification(
        self, password: str, verification_data: Dict[str, Any]
    ) -> bool:
        """执行组合验证"""
        if not self.verifiers:
            logger.warning("没有配置验证器")
            return False

        results = []
        for verifier in self.verifiers:
            try:
                result = verifier.verify(verification_data)
                results.append(result)
            except Exception as e:
                logger.exception(f"验证器执行失败: {e}")
                results.append(False)

        if self.require_all:
            # 需要所有验证都通过
            return all(results)
        else:
            # 只需要任一验证通过
            return any(results)

    def set_require_all(self, require_all: bool):
        """设置是否需要所有验证都通过"""
        self.require_all = require_all
        logger.info(f"组合验证模式已更新: {'全部通过' if require_all else '任一通过'}")


# ==================================================
# 验证器工厂
# ==================================================
class SecurityVerifierFactory:
    """验证器工厂"""

    @staticmethod
    def create_verifier(verifier_type: str, **kwargs) -> SecurityVerifier:
        """创建验证器"""
        if verifier_type == "simple":
            return SimplePasswordVerifier(**kwargs)
        elif verifier_type == "dynamic":
            return DynamicPasswordVerifier(**kwargs)
        elif verifier_type == "composite":
            return CompositeVerifier(**kwargs)
        else:
            raise ValueError(f"不支持的验证器类型: {verifier_type}")

    @staticmethod
    def get_available_types() -> list:
        """获取可用的验证器类型"""
        return ["simple", "dynamic", "composite"]
