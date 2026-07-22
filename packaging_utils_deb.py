"""
Debian 包构建工具，用于简化 PyInstaller 和 Nuitka 构建的 deb 包生成
"""

from __future__ import annotations
import os
import shutil
import subprocess
import platform
from pathlib import Path


class DebBuilder:
    """Debian 包构建器类"""

    @staticmethod
    def _normalize_arch(machine: str) -> str:
        m = (machine or "").lower()
        if m in ("x86_64", "amd64"):
            return "amd64"
        if m in ("aarch64", "arm64"):
            return "arm64"
        return "amd64"

    @staticmethod
    def _normalize_arch_for_control(value: str | None, fallback: str) -> str:
        v = (value or "").strip().lower()
        if v in ("amd64", "arm64"):
            return v
        return fallback

    @staticmethod
    def _normalize_arch_for_filename(value: str | None, fallback: str) -> str:
        v = (value or "").strip().lower()
        if v == "arch64":
            return "arm64"
        if v in ("amd64", "arm64"):
            return v
        return fallback

    def __init__(
        self,
        project_root: Path,
        app_name: str,
        version: str,
        description: str,
        author: str,
        website: str,
    ):
        """初始化 DebBuilder

        Args:
            project_root: 项目根目录
            app_name: 应用名称
            version: 应用版本
            description: 应用描述
            author: 作者信息
            website: 网站地址
        """
        self.project_root = project_root
        self.app_name = app_name
        self.version = version
        self.description = description
        self.author = author
        self.website = website

        # 处理版本号，移除开头的v并转换预发布版本格式
        self.deb_version = self._normalize_version(version)

        # 输出目录
        self.output_dir = project_root / "zip"
        self.output_dir.mkdir(exist_ok=True)

        # 临时构建目录
        self.deb_root = project_root / "deb_build"

        machine = platform.machine()
        default_arch = self._normalize_arch(machine)
        self.deb_arch = self._normalize_arch_for_control(
            os.environ.get("SECRANDOM_DEB_CONTROL_ARCH"), default_arch
        )
        self.deb_filename_arch = self._normalize_arch_for_filename(
            os.environ.get("SECRANDOM_DEB_FILENAME_ARCH"), self.deb_arch
        )

        # deb包文件名
        self.deb_filename = f"{self.app_name}-linux-Setup-{self.deb_version}-{self.deb_filename_arch}.deb"
        self.deb_path = self.output_dir / self.deb_filename

    def _normalize_version(self, version: str) -> str:
        """将版本号转换为deb包兼容格式"""
        version = version.lstrip("v")
        version = version.replace("-alpha", "~alpha").replace("-beta", "~beta")
        return version

    def _create_deb_structure(
        self, executable_path: Path, is_single_file: bool = False
    ) -> None:
        """创建deb包的基本结构"""
        # 清理并创建临时目录
        if self.deb_root.exists():
            shutil.rmtree(self.deb_root)
        self.deb_root.mkdir()

        # 创建必要的目录结构
        (self.deb_root / "DEBIAN").mkdir(parents=True, exist_ok=True)
        (self.deb_root / "usr" / "bin").mkdir(parents=True, exist_ok=True)
        (self.deb_root / "usr" / "share" / "applications").mkdir(
            parents=True, exist_ok=True
        )
        (
            self.deb_root / "usr" / "share" / "icons" / "hicolor" / "128x128" / "apps"
        ).mkdir(parents=True, exist_ok=True)

        if is_single_file:
            # 单文件模式：直接复制可执行文件到/usr/bin
            bin_path = self.deb_root / "usr" / "bin" / self.app_name
            shutil.copy2(executable_path, bin_path)
            os.chmod(bin_path, 0o755)
        else:
            # 目录模式：复制整个目录到/usr/share并创建符号链接
            app_dir = self.deb_root / "usr" / "share" / self.app_name
            shutil.copytree(executable_path, app_dir, dirs_exist_ok=True)

            # 创建可执行文件的符号链接
            bin_path = self.deb_root / "usr" / "bin" / self.app_name
            with open(bin_path, "w") as f:
                f.write(f"#!/bin/sh\n/usr/share/{self.app_name}/SecRandom.bin\n")
            os.chmod(bin_path, 0o755)

        # 复制图标文件
        icon_src = (
            self.project_root / "data" / "assets" / "icon" / "secrandom-icon-paper.png"
        )
        icon_dst = (
            self.deb_root
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "128x128"
            / "apps"
            / f"{self.app_name}.png"
        )
        shutil.copy2(icon_src, icon_dst)

        # 创建桌面快捷方式
        desktop_file = (
            self.deb_root
            / "usr"
            / "share"
            / "applications"
            / f"{self.app_name}.desktop"
        )
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Name={self.app_name.capitalize()}
Comment={self.description}
Exec={self.app_name}
Icon={self.app_name}
Terminal=false
Type=Application
Categories=Education;Utility;
""")
        os.chmod(desktop_file, 0o644)

    def _create_control_file(self) -> None:
        """创建deb包的控制文件"""
        control_file = self.deb_root / "DEBIAN" / "control"
        with open(control_file, "w") as f:
            f.write(f"""Package: {self.app_name}
Version: {self.deb_version}
Architecture: {self.deb_arch}
Maintainer: {self.author}
Installed-Size: {self._get_installed_size()}
Depends: libc6, libgcc-s1, libgl1, libglib2.0-0, libgstreamer-plugins-base1.0-0, libgstreamer1.0-0, libpulse0, libqt5core5a, libqt5dbus5, libqt5gui5, libqt5network5, libqt5widgets5, libstdc++6, libxcb1
Section: education
Priority: optional
Homepage: {self.website}
Description: {self.description}
""")
        os.chmod(control_file, 0o644)

    def _get_installed_size(self) -> int:
        """计算deb包的安装大小（KB）"""
        total_size = 0
        for root, dirs, files in os.walk(self.deb_root):
            # 跳过DEBIAN目录，因为它不包含在安装大小中
            if "DEBIAN" in root.split(os.sep):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        # 转换为KB并四舍五入
        return int(total_size / 1024)

    def _create_postinst_script(self) -> None:
        """创建安装后执行的脚本"""
        postinst_file = self.deb_root / "DEBIAN" / "postinst"
        with open(postinst_file, "w") as f:
            f.write(f"""#!/bin/sh
set -e

# 更新图标缓存
if command -v update-icon-caches > /dev/null; then
    update-icon-caches /usr/share/icons/hicolor
fi

# 更新桌面数据库
if command -v update-desktop-database > /dev/null; then
    update-desktop-database -q /usr/share/applications
fi

echo "{self.app_name} 安装完成！"
""")
        os.chmod(postinst_file, 0o755)

    def _create_prerm_script(self) -> None:
        """创建卸载前执行的脚本"""
        prerm_file = self.deb_root / "DEBIAN" / "prerm"
        with open(prerm_file, "w") as f:
            f.write(f"""#!/bin/sh
set -e

# 停止正在运行的应用程序（如果有）
pkill -f "{self.app_name}" || true

echo "正在卸载 {self.app_name}..."
""")
        os.chmod(prerm_file, 0o755)

    def build(self, executable_path: Path, is_single_file: bool = False) -> Path:
        """构建deb包

        Args:
            executable_path: 可执行文件或目录路径
            is_single_file: 是否为单文件模式

        Returns:
            deb包路径
        """
        print(f"\n开始构建deb包: {self.deb_path}")

        try:
            # 创建deb包结构
            self._create_deb_structure(executable_path, is_single_file)

            # 创建控制文件
            self._create_control_file()

            # 创建安装后脚本
            self._create_postinst_script()

            # 创建卸载前脚本
            self._create_prerm_script()

            # 构建deb包
            subprocess.run(
                ["dpkg-deb", "--build", str(self.deb_root), str(self.deb_path)],
                check=True,
                cwd=str(self.project_root),
            )

            print("\ndeb包构建成功！")
            print(f"deb包路径: {self.deb_path}")

            return self.deb_path

        except Exception as e:
            print(f"构建deb包失败: {e}")
            raise
        finally:
            # 清理临时目录
            if self.deb_root.exists():
                shutil.rmtree(self.deb_root)

    @staticmethod
    def build_from_pyinstaller(
        project_root: Path,
        app_name: str,
        version: str,
        description: str,
        author: str,
        website: str,
    ) -> Path:
        """从PyInstaller输出构建deb包

        Args:
            project_root: 项目根目录
            app_name: 应用名称
            version: 应用版本
            description: 应用描述
            author: 作者信息
            website: 网站地址

        Returns:
            deb包路径
        """
        builder = DebBuilder(
            project_root, app_name, version, description, author, website
        )
        pyinstaller_dist = project_root / "dist" / "SecRandom"
        return builder.build(pyinstaller_dist, is_single_file=False)

    @staticmethod
    def build_from_nuitka(
        project_root: Path,
        app_name: str,
        version: str,
        description: str,
        author: str,
        website: str,
    ) -> Path:
        """从Nuitka输出构建deb包

        Args:
            project_root: 项目根目录
            app_name: 应用名称
            version: 应用版本
            description: 应用描述
            author: 作者信息
            website: 网站地址

        Returns:
            deb包路径
        """
        builder = DebBuilder(
            project_root, app_name, version, description, author, website
        )

        # 检查Nuitka输出文件
        nuitka_exe = project_root / "dist" / "main.bin"
        if not nuitka_exe.exists():
            nuitka_exe = project_root / "dist" / "main"
            if not nuitka_exe.exists():
                raise FileNotFoundError(f"Nuitka输出文件不存在: {nuitka_exe}")

        return builder.build(nuitka_exe, is_single_file=True)
