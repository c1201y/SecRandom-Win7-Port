"""
协议管理器 - 跨平台URL协议注册管理
支持Windows和Linux系统的自定义协议注册
"""

from __future__ import annotations
import os
import sys
import subprocess
import plistlib
from pathlib import Path
from loguru import logger


class ProtocolManager:
    """协议管理器 - 处理跨平台的URL协议注册"""

    def __init__(self, app_name: str, protocol_name: str):
        """
        初始化协议管理器

        Args:
            app_name: 应用程序名称
            protocol_name: 自定义协议名称（不含://）
        """
        self.app_name = app_name
        self.protocol_name = protocol_name
        self.is_windows = sys.platform.startswith("win")
        self.is_linux = sys.platform.startswith("linux")
        self.is_macos = sys.platform.startswith("darwin")

    def register_protocol(self) -> bool:
        """
        注册自定义协议

        Returns:
            注册成功返回True，失败返回False
        """
        if self.is_windows:
            return self._register_windows_protocol()
        elif self.is_linux:
            return self._register_linux_protocol()
        elif self.is_macos:
            return self._register_macos_protocol()
        else:
            logger.exception(f"不支持的操作系统: {sys.platform}")
            return False

    def unregister_protocol(self) -> bool:
        """
        注销自定义协议

        Returns:
            注销成功返回True，失败返回False
        """
        if self.is_windows:
            return self._unregister_windows_protocol()
        elif self.is_linux:
            return self._unregister_linux_protocol()
        elif self.is_macos:
            return self._unregister_macos_protocol()
        else:
            logger.exception(f"不支持的操作系统: {sys.platform}")
            return False

    def is_protocol_registered(self) -> bool:
        """
        检查协议是否已注册

        Returns:
            已注册返回True，未注册返回False
        """
        if self.is_windows:
            return self._is_windows_protocol_registered()
        elif self.is_linux:
            return self._is_linux_protocol_registered()
        elif self.is_macos:
            return self._is_macos_protocol_registered()
        else:
            return False

    def _register_windows_protocol(self) -> bool:
        """Windows系统注册协议（单用户模式，无需管理员权限）"""
        try:
            # 获取当前可执行文件路径
            exe_path = self._get_executable_path()

            # 直接注册到HKEY_CURRENT_USER（单用户模式，无需管理员权限）
            return self._register_windows_protocol_current_user(exe_path)

        except Exception as e:
            logger.exception(f"Windows协议注册失败: {e}")
            return False

    def _register_windows_protocol_current_user(self, exe_path: str) -> bool:
        """注册到当前用户的Windows协议（无需管理员权限）"""
        try:
            try:
                import winreg
            except Exception as e:
                logger.warning(f"无法加载 winreg: {e}")
                return False

            # 注册协议到HKEY_CURRENT_USER\Software\Classes
            key_path = f"Software\\Classes\\{self.protocol_name}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(
                    key, "", 0, winreg.REG_SZ, f"URL:{self.app_name} Protocol"
                )
                winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

            # 注册命令
            command_key_path = (
                f"Software\\Classes\\{self.protocol_name}\\shell\\open\\command"
            )
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" --url "%1"')

            return True

        except Exception as e:
            logger.exception(f"Windows当前用户协议注册失败: {e}")
            return False

    def _unregister_windows_protocol(self) -> bool:
        """Windows系统注销协议（单用户模式，无需管理员权限）"""
        try:
            # 直接删除当前用户注册表项（单用户模式，无需管理员权限）
            return self._unregister_windows_protocol_current_user()

        except Exception as e:
            logger.exception(f"Windows协议注销失败: {e}")
            return False

    def _unregister_windows_protocol_current_user(self) -> bool:
        """注销当前用户的Windows协议"""
        try:
            try:
                import winreg
            except Exception as e:
                logger.warning(f"无法加载 winreg: {e}")
                return False

            # 删除当前用户注册表项
            key_path = f"Software\\Classes\\{self.protocol_name}\\shell\\open\\command"
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{self.protocol_name}\\shell\\open",
            )
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{self.protocol_name}\\shell",
            )
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{self.protocol_name}"
            )
            return True

        except Exception as e:
            logger.exception(f"Windows当前用户协议注销失败: {e}")
            return False

    def _is_windows_protocol_registered(self) -> bool:
        """检查Windows协议是否已注册（单用户模式）"""
        try:
            try:
                import winreg
            except Exception as e:
                logger.warning(f"无法加载 winreg: {e}")
                return False

            # 检查HKEY_CURRENT_USER（用户级）
            key_path = f"Software\\Classes\\{self.protocol_name}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                return True
        except (OSError, FileNotFoundError):
            return False

    def _register_linux_protocol(self) -> bool:
        """Linux系统注册协议"""
        try:
            # 获取当前可执行文件路径
            exe_path = self._get_executable_path()

            # 创建.desktop文件
            desktop_file_path = self._get_linux_desktop_file_path()
            desktop_content = self._generate_linux_desktop_file(exe_path)

            # 写入.desktop文件
            with open(desktop_file_path, "w", encoding="utf-8") as f:
                f.write(desktop_content)

            # 设置可执行权限
            os.chmod(desktop_file_path, 0o755)

            # 注册协议处理程序
            self._register_linux_mime_handler()

            # 更新桌面数据库
            self._update_linux_desktop_database()

            return True

        except Exception as e:
            logger.exception(f"Linux协议注册失败: {e}")
            return False

    def _unregister_linux_protocol(self) -> bool:
        """Linux系统注销协议"""
        try:
            desktop_file_path = self._get_linux_desktop_file_path()

            if os.path.exists(desktop_file_path):
                os.remove(desktop_file_path)

            # 更新桌面数据库
            self._update_linux_desktop_database()

            return True

        except Exception as e:
            logger.exception(f"Linux协议注销失败: {e}")
            return False

    def _is_linux_protocol_registered(self) -> bool:
        """检查Linux协议是否已注册"""
        desktop_file_path = self._get_linux_desktop_file_path()
        return os.path.exists(desktop_file_path)

    def _register_macos_protocol(self) -> bool:
        try:
            bundle_path = self._get_macos_bundle_path()
            if bundle_path is None:
                logger.warning("未检测到 macOS 应用包，无法注册协议")
                return False
            return self._run_macos_lsregister(bundle_path, register=True)
        except Exception as e:
            logger.exception(f"macOS 协议注册失败: {e}")
            return False

    def _unregister_macos_protocol(self) -> bool:
        try:
            bundle_path = self._get_macos_bundle_path()
            if bundle_path is None:
                logger.warning("未检测到 macOS 应用包，无法注销协议")
                return False
            return self._run_macos_lsregister(bundle_path, register=False)
        except Exception as e:
            logger.exception(f"macOS 协议注销失败: {e}")
            return False

    def _is_macos_protocol_registered(self) -> bool:
        bundle_path = self._get_macos_bundle_path()
        if bundle_path is None:
            return False
        return self._app_supports_macos_protocol(bundle_path)

    def _get_macos_bundle_path(self) -> Path | None:
        exe_path = Path(self._get_executable_path())
        for parent in exe_path.parents:
            if parent.suffix == ".app":
                return parent
        return None

    def _read_macos_info_plist(self, bundle_path: Path) -> dict | None:
        plist_path = bundle_path / "Contents" / "Info.plist"
        if not plist_path.exists():
            return None
        with open(plist_path, "rb") as f:
            return plistlib.load(f)

    def _app_supports_macos_protocol(self, bundle_path: Path) -> bool:
        plist_data = self._read_macos_info_plist(bundle_path)
        if not plist_data:
            return False
        url_types = plist_data.get("CFBundleURLTypes", [])
        for item in url_types:
            schemes = item.get("CFBundleURLSchemes", [])
            if self.protocol_name in schemes:
                return True
        return False

    def _get_macos_lsregister_path(self) -> str:
        return "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"

    def _run_macos_lsregister(self, bundle_path: Path, register: bool) -> bool:
        lsregister_path = self._get_macos_lsregister_path()
        if not os.path.exists(lsregister_path):
            logger.warning("lsregister 不存在，无法更新 macOS 协议注册")
            return False
        args = [lsregister_path, "-f" if register else "-u", str(bundle_path)]
        subprocess.run(args, check=False, capture_output=True)
        return True

    def _get_linux_desktop_file_path(self) -> str:
        """获取Linux桌面文件路径"""
        applications_dir = Path.home() / ".local" / "share" / "applications"
        applications_dir.mkdir(parents=True, exist_ok=True)
        return str(applications_dir / f"{self.app_name.lower()}-url-handler.desktop")

    def _generate_linux_desktop_file(self, exe_path: str) -> str:
        """生成Linux桌面文件内容"""
        return f"""[Desktop Entry]
Name={self.app_name} URL Handler
Comment=Handle {self.protocol_name}:// URLs for {self.app_name}
Exec={exe_path} --url %u
Icon={self.app_name.lower()}
Terminal=false
Type=Application
Categories=Utility;
MimeType=x-scheme-handler/{self.protocol_name};
"""

    def _register_linux_mime_handler(self):
        """注册Linux MIME处理程序"""
        try:
            # 使用xdg-mime注册协议处理程序
            subprocess.run(
                [
                    "xdg-mime",
                    "default",
                    f"{self.app_name.lower()}-url-handler.desktop",
                    f"x-scheme-handler/{self.protocol_name}",
                ],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果xdg-mime不可用，尝试直接创建mimeapps.list
            self._create_linux_mimeapps_list()

    def _create_linux_mimeapps_list(self):
        """创建Linux mimeapps.list文件"""
        config_dir = Path.home() / ".config"
        config_dir.mkdir(parents=True, exist_ok=True)

        mimeapps_file = config_dir / "mimeapps.list"
        content = f"""[Default Applications]
x-scheme-handler/{self.protocol_name}={self.app_name.lower()}-url-handler.desktop

[Added Associations]
x-scheme-handler/{self.protocol_name}={self.app_name.lower()}-url-handler.desktop
"""

        with open(mimeapps_file, "a", encoding="utf-8") as f:
            f.write(content)

    def _update_linux_desktop_database(self):
        """更新Linux桌面数据库"""
        try:
            applications_dir = Path.home() / ".local" / "share" / "applications"
            subprocess.run(
                ["update-desktop-database", str(applications_dir)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果update-desktop-database不可用，忽略错误
            pass

    def _get_executable_path(self) -> str:
        """获取当前可执行文件路径"""
        if getattr(sys, "frozen", False):
            # PyInstaller打包后的可执行文件
            exe_path = sys.executable
        else:
            # 普通Python脚本
            exe_path = sys.argv[0]

        return os.path.abspath(exe_path)
