from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QScrollArea,
    QFrame,
)
from PySide2.QtCore import Qt, QUrl, QTimer, QFileSystemWatcher
from PySide2.QtGui import QDesktopServices, QPixmap
from qfluentwidgets import (
    SegmentedWidget,
    TitleLabel,
    PushButton,
)
from app.view.components.center_flow_layout import CenterFlowLayout
from app.view.settings.theme_management.theme_card import ThemeCard
from app.view.settings.theme_management.background_page import BackgroundManagementPage
from app.tools.personalised import get_theme_icon
from app.Language.obtain_language import get_content_name_async
from app.tools.path_utils import get_data_path
from app.tools.settings_access import readme_settings_async, update_settings
import os
import requests
import yaml
import json
import shutil
import urllib3
import zipfile
import io
import concurrent.futures
from PySide2.QtCore import QThread, Signal
from loguru import logger
from app.tools.update_utils import compare_versions
from pathlib import Path
from datetime import datetime


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import weakref


class MarketLoader(QThread):
    loaded = Signal(list)
    error = Signal(str)

    def _format_github_datetime(self, value: str) -> str:
        value = str(value or "").strip()
        if not value:
            return "-"
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return value

    def fetch_latest_tag(self, item_data):
        try:
            owner = item_data.get("repoOwner")
            repo = item_data.get("repoName")

            # 补全 owner/repo
            if not owner or not repo:
                if "url" in item_data:
                    parts = item_data["url"].rstrip("/").split("/")
                    if len(parts) >= 2:
                        repo = parts[-1]
                        owner = parts[-2]

            if owner and repo:
                item_data["repoOwner"] = owner
                item_data["repoName"] = repo

                api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
                r = requests.get(api_url, timeout=10, verify=False)
                if r.status_code == 200:
                    tags = r.json()
                    if tags and isinstance(tags, list) and len(tags) > 0:
                        latest_tag = tags[0]["name"]
                        item_data["version"] = latest_tag
                        item_data["tag_name"] = latest_tag

                        published_time = ""
                        try:
                            release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{latest_tag}"
                            rr = requests.get(release_url, timeout=10, verify=False)
                            if rr.status_code == 200:
                                release_data = rr.json() or {}
                                published_time = (
                                    release_data.get("published_at")
                                    or release_data.get("created_at")
                                    or ""
                                )
                            else:
                                sha = ((tags[0] or {}).get("commit", {}) or {}).get(
                                    "sha", ""
                                )
                                if sha:
                                    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                                    cr = requests.get(
                                        commit_url, timeout=10, verify=False
                                    )
                                    if cr.status_code == 200:
                                        commit_data = cr.json() or {}
                                        commit_info = (
                                            commit_data.get("commit", {}) or {}
                                        )
                                        committer = (
                                            commit_info.get("committer", {}) or {}
                                        )
                                        author = commit_info.get("author", {}) or {}
                                        published_time = (
                                            committer.get("date")
                                            or author.get("date")
                                            or ""
                                        )
                        except Exception:
                            published_time = ""
                        item_data["last_updated"] = self._format_github_datetime(
                            published_time
                        )
        except Exception:
            pass
        return item_data

    def run(self):
        try:
            raw_themes = []

            # 从 GitHub 获取
            url = "https://api.github.com/repos/SECTL/SecRandnom-themes/contents/index/themes"
            resp = requests.get(url, timeout=10, verify=False)
            resp.raise_for_status()
            files = resp.json()

            for item in files:
                if item["name"].endswith(".yml") or item["name"].endswith(".yaml"):
                    try:
                        r = requests.get(item["download_url"], timeout=10, verify=False)
                        r.raise_for_status()
                        data = yaml.safe_load(r.text)

                        # 解析 repoOwner 和 repoName，如果缺失
                        if "url" in data and (
                            not data.get("repoOwner") or not data.get("repoName")
                        ):
                            # 假设 url 是 https://github.com/owner/repo
                            parts = data["url"].rstrip("/").split("/")
                            if len(parts) >= 2:
                                data["repoName"] = parts[-1]
                                data["repoOwner"] = parts[-2]

                        raw_themes.append(data)
                    except Exception as e:
                        logger.error(f"加载主题文件失败 {item['name']}: {e}")

            # 并发获取 tags
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                themes = list(executor.map(self.fetch_latest_tag, raw_themes))

            self.loaded.emit(themes)
        except Exception as e:
            self.error.emit(str(e))


class ImageLoader(QThread):
    loaded = Signal(str, QPixmap)  # url, pixmap

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            if self.isInterruptionRequested():
                return
            resp = requests.get(self.url, timeout=15, verify=False)
            resp.raise_for_status()
            if self.isInterruptionRequested():
                return
            pixmap = QPixmap()
            pixmap.loadFromData(resp.content)
            if self.isInterruptionRequested():
                return
            self.loaded.emit(self.url, pixmap)
        except Exception as e:
            logger.error(f"下载图片失败 {self.url}: {e}")


class InstallThread(QThread):
    finished_signal = Signal(bool, str)  # success, message

    def __init__(self, theme_info):
        super().__init__()
        self.theme_info = theme_info

    def _find_artifact_prefix(self, z: zipfile.ZipFile, artifact_name: str) -> str:
        artifact_name = str(artifact_name or "").strip()
        if not artifact_name:
            return ""
        candidates = []
        for name in z.namelist():
            normalized = (name or "").replace("\\", "/")
            if not normalized or normalized.endswith("/"):
                continue
            parts = [p for p in normalized.split("/") if p]
            if artifact_name not in parts:
                continue
            idx = parts.index(artifact_name)
            candidates.append("/".join(parts[: idx + 1]))
        if not candidates:
            return ""
        candidates.sort(key=lambda p: (len(p.split("/")), len(p)))
        return candidates[0]

    def _read_manifest_from_zip(self, z: zipfile.ZipFile, theme_id: str):
        candidates = []
        for name in z.namelist():
            if not name.lower().endswith("manifest.json"):
                continue
            try:
                data = json.loads(z.read(name).decode("utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            artifact_name = str(data.get("artifactName", "")).strip()
            if not artifact_name:
                continue
            manifest_id = str(data.get("id", "")).strip()
            score = 0
            if manifest_id and str(manifest_id) == str(theme_id):
                score += 10
            if f"/{artifact_name}/" in name.replace("\\", "/"):
                score += 3
            candidates.append((score, name, data))
        if not candidates:
            return None, None
        candidates.sort(key=lambda x: (-x[0], len(x[1])))
        _, manifest_path, manifest_data = candidates[0]
        return manifest_path, manifest_data

    def _safe_extract_theme_folder(
        self,
        z: zipfile.ZipFile,
        theme_dir: Path,
        folder_prefix: str,
    ):
        folder_prefix = (folder_prefix or "").replace("\\", "/")
        if folder_prefix and not folder_prefix.endswith("/"):
            folder_prefix += "/"

        base = theme_dir.resolve()
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            if not name or info.is_dir():
                continue
            if folder_prefix and not name.startswith(folder_prefix):
                continue
            rel = name[len(folder_prefix) :] if folder_prefix else name
            rel = rel.lstrip("/").strip()
            if not rel:
                continue
            out_path = (theme_dir / rel).resolve()
            if not str(out_path).startswith(str(base)):
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(out_path, "wb") as dst:
                shutil.copyfileobj(src, dst)

    def _flatten_extracted_theme_dir(self, theme_dir: Path):
        try:
            theme_dir.mkdir(parents=True, exist_ok=True)
            if (theme_dir / "manifest.json").exists():
                return

            child_dirs = [p for p in theme_dir.iterdir() if p.is_dir()]
            manifest_dirs = [d for d in child_dirs if (d / "manifest.json").exists()]

            if len(manifest_dirs) == 1:
                src_root = manifest_dirs[0]
            elif len(child_dirs) == 1 and manifest_dirs:
                src_root = child_dirs[0]
            else:
                return

            for item in list(src_root.iterdir()):
                dest = theme_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))

            try:
                shutil.rmtree(src_root)
            except Exception:
                pass
        except Exception:
            return

    def run(self):
        try:
            theme_id = self.theme_info.get("id")
            if not theme_id:
                raise ValueError("Theme ID is missing")

            repo_owner = self.theme_info.get("repoOwner")
            repo_name = self.theme_info.get("repoName")

            if not repo_owner or not repo_name:
                url = self.theme_info.get("url", "")
                parts = url.rstrip("/").split("/")
                if len(parts) >= 2:
                    repo_name = parts[-1]
                    repo_owner = parts[-2]

            if not repo_owner or not repo_name:
                raise ValueError("Cannot determine repository owner and name")

            # 1. 获取下载链接 (优先使用 tag)
            tag_name = self.theme_info.get("tag_name")
            if tag_name:
                zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/tags/{tag_name}.zip"
            else:
                # 获取默认分支
                api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
                resp = requests.get(api_url, timeout=10, verify=False)
                resp.raise_for_status()
                default_branch = resp.json().get("default_branch", "main")
                zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{default_branch}.zip"

            logger.info(f"正在下载主题: {zip_url}")

            r = requests.get(zip_url, stream=True, timeout=60, verify=False)
            r.raise_for_status()

            # 3. 解压
            theme_root = get_data_path("themes")
            theme_dir = theme_root / theme_id
            if theme_dir.exists():
                shutil.rmtree(theme_dir)

            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                manifest_path, manifest_data = self._read_manifest_from_zip(z, theme_id)
                if manifest_path and manifest_data:
                    artifact_name = str(manifest_data.get("artifactName", "")).strip()
                    prefix = self._find_artifact_prefix(z, artifact_name)
                    if not prefix:
                        parts = [
                            p for p in manifest_path.replace("\\", "/").split("/") if p
                        ]
                        if artifact_name and artifact_name in parts:
                            idx = len(parts) - 1 - parts[::-1].index(artifact_name)
                            prefix = "/".join(parts[: idx + 1])
                        else:
                            prefix = "/".join(parts[:-1])
                    self._safe_extract_theme_folder(z, theme_dir, prefix)
                else:
                    names = [n.replace("\\", "/") for n in z.namelist() if n]
                    top_levels = {n.split("/", 1)[0] for n in names if "/" in n}
                    if len(top_levels) == 1:
                        self._safe_extract_theme_folder(
                            z, theme_dir, next(iter(top_levels))
                        )
                    else:
                        z.extractall(theme_dir)

            self._flatten_extracted_theme_dir(theme_dir)
            self.finished_signal.emit(True, theme_id)

        except Exception as e:
            logger.error(f"安装主题失败: {e}")
            self.finished_signal.emit(False, str(e))


class UninstallThread(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, theme_id):
        super().__init__()
        self.theme_id = theme_id

    def run(self):
        try:
            theme_root = get_data_path("themes")
            theme_dir = theme_root / self.theme_id
            if theme_dir.exists():
                shutil.rmtree(theme_dir)
            self.finished_signal.emit(True, self.theme_id)
        except Exception as e:
            logger.error(f"卸载主题失败: {e}")
            self.finished_signal.emit(False, str(e))


class ThemeManagement(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ThemeManagement")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)

        # 标题栏
        self.headerLayout = QHBoxLayout()
        self.titleLabel = TitleLabel(
            get_content_name_async("theme_management", "title"), self
        )
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.vBoxLayout.addLayout(self.headerLayout)

        self.vBoxLayout.addSpacing(10)

        # 工具栏
        self.toolbarLayout = QHBoxLayout()

        self.pivot = SegmentedWidget(self)
        self.pivot.addItem(
            "market", get_content_name_async("theme_management", "market")
        )
        self.pivot.addItem(
            "installed", get_content_name_async("theme_management", "installed")
        )
        self.pivot.addItem(
            "background", get_content_name_async("theme_management", "background")
        )
        self.pivot.setCurrentItem("market")
        self.pivot.currentItemChanged.connect(self._on_pivot_changed)

        self.toolbarLayout.addWidget(self.pivot)
        self.toolbarLayout.addStretch(1)

        # 按钮
        self.refreshBtn = PushButton(
            get_theme_icon("ic_fluent_arrow_sync_20_filled"),
            get_content_name_async("theme_management", "refresh_market"),
            self,
        )
        self.refreshBtn.clicked.connect(self._refresh_market)

        self.folderBtn = PushButton(
            get_theme_icon("ic_fluent_folder_open_20_filled"),
            get_content_name_async("theme_management", "open_folder"),
            self,
        )
        self.folderBtn.clicked.connect(self._open_theme_folder)

        self.toolbarLayout.addWidget(self.refreshBtn)
        self.toolbarLayout.addWidget(self.folderBtn)

        self.vBoxLayout.addLayout(self.toolbarLayout)

        self.vBoxLayout.addSpacing(10)

        # 堆叠窗口
        self.stackedWidget = QStackedWidget(self)

        # 市场页面
        self.marketPage = QWidget()
        self.marketLayout = QVBoxLayout(self.marketPage)
        self.marketLayout.setContentsMargins(0, 0, 0, 0)

        self.marketScroll = QScrollArea(self.marketPage)
        self.marketScroll.setWidgetResizable(True)
        self.marketScroll.setFrameShape(QFrame.NoFrame)
        self.marketScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.marketScroll.setStyleSheet("background: transparent;")  # 确保透明背景

        self.marketContent = QWidget()
        self.marketContent.setStyleSheet("background: transparent;")
        self.marketFlowLayout = CenterFlowLayout(self.marketContent, needAni=True)
        self.marketFlowLayout.setContentsMargins(10, 10, 10, 10)
        self.marketFlowLayout.setVerticalSpacing(20)
        self.marketFlowLayout.setHorizontalSpacing(20)
        self.marketScroll.setWidget(self.marketContent)
        self.marketLayout.addWidget(self.marketScroll)

        # 已安装页面
        self.installedPage = QWidget()
        self.installedLayout = QVBoxLayout(self.installedPage)
        self.installedLayout.setContentsMargins(0, 0, 0, 0)

        self.installedScroll = QScrollArea(self.installedPage)
        self.installedScroll.setWidgetResizable(True)
        self.installedScroll.setFrameShape(QFrame.NoFrame)
        self.installedScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.installedScroll.setStyleSheet("background: transparent;")

        self.installedContent = QWidget()
        self.installedContent.setStyleSheet("background: transparent;")
        self.installedFlowLayout = CenterFlowLayout(self.installedContent, needAni=True)
        self.installedFlowLayout.setContentsMargins(10, 10, 10, 10)
        self.installedFlowLayout.setVerticalSpacing(20)
        self.installedFlowLayout.setHorizontalSpacing(20)

        self.installedScroll.setWidget(self.installedContent)
        self.installedLayout.addWidget(self.installedScroll)

        self.backgroundPage = BackgroundManagementPage(self)

        self.stackedWidget.addWidget(self.marketPage)
        self.stackedWidget.addWidget(self.installedPage)
        self.stackedWidget.addWidget(self.backgroundPage)

        self.vBoxLayout.addWidget(self.stackedWidget)

        self.image_loaders = []
        self.active_threads = []
        self.market_loader = None
        self.market_themes = {}
        self.theme_watcher = QFileSystemWatcher(self)
        self.theme_watcher.directoryChanged.connect(self._schedule_installed_reload)
        self.theme_watcher.fileChanged.connect(self._schedule_installed_reload)
        self.installed_reload_timer = QTimer(self)
        self.installed_reload_timer.setSingleShot(True)
        self.installed_reload_timer.timeout.connect(self._load_installed_data)

        # 初始加载
        self._load_market_data()
        self._load_installed_data()

    def _on_pivot_changed(self, k):
        if k == "market":
            self.stackedWidget.setCurrentWidget(self.marketPage)
            self.refreshBtn.setVisible(True)
            self.folderBtn.setVisible(True)
        elif k == "installed":
            self.stackedWidget.setCurrentWidget(self.installedPage)
            self._load_installed_data()
            self.refreshBtn.setVisible(True)
            self.folderBtn.setVisible(True)
        else:
            self.stackedWidget.setCurrentWidget(self.backgroundPage)
            self.refreshBtn.setVisible(False)
            self.folderBtn.setVisible(False)

    def _refresh_market(self):
        self._load_market_data()

    def _reload_themes(self):
        self._load_installed_data()

    def _open_theme_folder(self):
        # 主题文件夹路径
        path = self._get_theme_primary_root()
        if not os.path.exists(path):
            os.makedirs(path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _load_market_data(self):
        # 如果正在加载，则不重复加载
        if self.market_loader and self.market_loader.isRunning():
            return

        self._stop_image_loaders()
        self._clear_layout(self.marketFlowLayout)

        # 显示加载中提示
        self.market_loader = MarketLoader()
        self.market_loader.loaded.connect(self._on_market_data_loaded)
        self.market_loader.error.connect(
            lambda e: logger.error(f"市场数据加载错误: {e}")
        )
        self.market_loader.start()

    def _on_market_data_loaded(self, themes):
        self._stop_image_loaders()
        self._clear_layout(self.marketFlowLayout)
        self.market_themes = {t["id"]: t for t in themes}

        roll_call_theme_id = readme_settings_async(
            "theme_management", "roll_call_theme_id"
        )
        lottery_theme_id = readme_settings_async("theme_management", "lottery_theme_id")
        roll_call_theme_type = readme_settings_async(
            "theme_management", "roll_call_theme_type"
        )
        lottery_theme_type = readme_settings_async(
            "theme_management", "lottery_theme_type"
        )

        for info in themes:
            # 检查安装状态
            installed_ver = self._get_installed_version(info["id"])
            if installed_ver:
                info["is_installed"] = True
                info["current_version"] = installed_ver
                info["update_available"] = self._is_update_available(
                    installed_ver, str(info.get("version", ""))
                )
                theme_dir = next(self._iter_theme_dirs(info["id"]), None)
                info.update(
                    self._build_apply_state(
                        info["id"],
                        theme_dir,
                        roll_call_theme_id,
                        lottery_theme_id,
                        roll_call_theme_type,
                        lottery_theme_type,
                    )
                )
            else:
                info["is_installed"] = False

            info["latest_version"] = str(info.get("version", "0.0.0"))
            info["last_updated"] = str(info.get("last_updated", "-"))

            # 构建预览图 URL
            repo_owner = info.get("repoOwner")
            repo_name = info.get("repoName")
            assets_root = info.get("assetsRoot")
            banner = info.get("banner")

            card = None
            if repo_owner and repo_name and assets_root and banner:
                banner_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{assets_root}/{banner}"

                card = ThemeCard(info)
                card.installSignal.connect(self._install_theme)
                card.uninstallSignal.connect(self._uninstall_theme)
                card.updateSignal.connect(self._update_theme)
                card.applySignal.connect(self._apply_theme)
                self.marketFlowLayout.addWidget(card)

                loader = ImageLoader(banner_url)
                card_ref = weakref.ref(card)

                def _apply_preview(_u, _pm, _ref=card_ref):
                    c = _ref()
                    if not c:
                        return
                    try:
                        c.set_preview_pixmap(_pm)
                    except RuntimeError:
                        return

                loader.loaded.connect(_apply_preview)
                loader.finished.connect(
                    lambda loader=loader: self._remove_image_loader(loader)
                )
                loader.start()
                self.image_loaders.append(loader)
            else:
                card = ThemeCard(info)
                card.installSignal.connect(self._install_theme)
                card.uninstallSignal.connect(self._uninstall_theme)
                card.updateSignal.connect(self._update_theme)
                card.applySignal.connect(self._apply_theme)
                self.marketFlowLayout.addWidget(card)

    def _remove_image_loader(self, loader):
        if loader in self.image_loaders:
            self.image_loaders.remove(loader)

    def _stop_image_loaders(self):
        for loader in list(self.image_loaders):
            try:
                loader.loaded.disconnect()
            except Exception:
                pass
            try:
                loader.requestInterruption()
            except Exception:
                pass
        self.image_loaders = []

    def _get_installed_version(self, theme_id):
        for theme_dir in self._iter_theme_dirs(theme_id):
            manifest_path = theme_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return str(data.get("version", ""))
                except Exception:
                    return None
        return None

    def _read_manifest(self, theme_dir):
        manifest_path = theme_dir / "manifest.json"
        if not manifest_path.exists():
            return None
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取主题清单失败 {manifest_path}: {e}")
            return None

    def _flatten_theme_dir_if_needed(self, theme_dir: Path):
        try:
            if (theme_dir / "manifest.json").exists():
                return
            child_dirs = [p for p in theme_dir.iterdir() if p.is_dir()]
            manifest_dirs = [d for d in child_dirs if (d / "manifest.json").exists()]
            if len(manifest_dirs) != 1:
                return
            src_root = manifest_dirs[0]
            for item in list(src_root.iterdir()):
                dest = theme_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            try:
                shutil.rmtree(src_root)
            except Exception:
                pass
        except Exception:
            return

    def _is_update_available(self, current_version, latest_version):
        if not current_version or not latest_version:
            return False
        result = compare_versions(str(current_version), str(latest_version))
        return result == 1

    def _load_installed_data(self):
        self._clear_layout(self.installedFlowLayout)
        theme_roots = self._get_theme_roots()
        if not theme_roots:
            return

        roll_call_theme_id = readme_settings_async(
            "theme_management", "roll_call_theme_id"
        )
        lottery_theme_id = readme_settings_async("theme_management", "lottery_theme_id")
        roll_call_theme_type = readme_settings_async(
            "theme_management", "roll_call_theme_type"
        )
        lottery_theme_type = readme_settings_async(
            "theme_management", "lottery_theme_type"
        )
        seen_ids = set()

        for theme_root in theme_roots:
            for theme_dir in theme_root.iterdir():
                if not theme_dir.is_dir():
                    continue

                self._flatten_theme_dir_if_needed(theme_dir)
                manifest_data = self._read_manifest(theme_dir)
                if not manifest_data:
                    continue

                theme_id = str(manifest_data.get("id", theme_dir.name))
                if theme_id in seen_ids:
                    continue
                seen_ids.add(theme_id)

                market_info = self.market_themes.get(theme_id, {})
                info = dict(market_info)
                info["id"] = theme_id
                current_version = str(manifest_data.get("version", ""))
                info["current_version"] = current_version
                info["is_installed"] = True
                info["url"] = manifest_data.get("url", info.get("url", ""))

                info.update(
                    self._build_apply_state(
                        theme_id,
                        theme_dir,
                        roll_call_theme_id,
                        lottery_theme_id,
                        roll_call_theme_type,
                        lottery_theme_type,
                    )
                )

                if "banner" in info:
                    local_banner = theme_dir / info["banner"]
                    if local_banner.exists():
                        info["preview_path"] = str(local_banner)

                market_latest = str(market_info.get("version", ""))
                latest_version = market_latest or current_version
                info["version"] = latest_version
                info["latest_version"] = latest_version

                if market_latest and info.get("current_version"):
                    info["update_available"] = self._is_update_available(
                        info["current_version"], info["version"]
                    )
                else:
                    info["update_available"] = False

                card = ThemeCard(info)
                card.uninstallSignal.connect(self._uninstall_theme)
                card.updateSignal.connect(self._update_theme)
                card.applySignal.connect(self._apply_theme)
                self.installedFlowLayout.addWidget(card)

        self._reset_theme_watcher()

    def _get_theme_roots(self):
        theme_root = get_data_path("themes")
        return [theme_root] if theme_root.exists() else []

    def _get_theme_primary_root(self):
        return get_data_path("themes")

    def _iter_theme_dirs(self, theme_id):
        for root in self._get_theme_roots():
            theme_dir = root / theme_id
            if theme_dir.exists():
                yield theme_dir
        for root in self._get_theme_roots():
            try:
                for theme_dir in root.iterdir():
                    if not theme_dir.is_dir():
                        continue
                    manifest_path = theme_dir / "manifest.json"
                    if not manifest_path.exists():
                        continue
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if str(data.get("id", "")) == str(theme_id):
                            yield theme_dir
                    except Exception:
                        continue
            except Exception:
                continue

    def _has_theme_page(self, theme_dir, folder_name):
        target_dir = theme_dir / folder_name
        if not target_dir.exists():
            return False
        has_py, has_html = self._get_theme_page_impls(theme_dir, folder_name)
        return has_py or has_html

    def _get_theme_page_impls(self, theme_dir, folder_name):
        target_dir = theme_dir / folder_name
        if not target_dir.exists():
            return False, False
        py_file = target_dir / "main.py"
        html_file = target_dir / "main.html"
        index_file = target_dir / "index.html"
        has_py = py_file.exists()
        has_html = html_file.exists() or index_file.exists()
        return has_py, has_html

    def _normalize_theme_type(self, stored_type, has_py, has_html):
        stored_type = str(stored_type or "").lower().strip()
        if stored_type == "py" and has_py:
            return "py"
        if stored_type == "html" and has_html:
            return "html"
        if has_py:
            return "py"
        if has_html:
            return "html"
        return ""

    def _is_scope_active(self, theme_id, scope_value):
        scope_value = str(scope_value or "")
        if scope_value == "__none__":
            return False
        return scope_value == theme_id

    def _build_apply_state(
        self,
        theme_id,
        theme_dir,
        roll_call_theme_id,
        lottery_theme_id,
        roll_call_theme_type,
        lottery_theme_type,
    ):
        has_roll_call_py = False
        has_roll_call_html = False
        has_lottery_py = False
        has_lottery_html = False
        if theme_dir:
            has_roll_call_py, has_roll_call_html = self._get_theme_page_impls(
                theme_dir, "Roll_call_page"
            )
            has_lottery_py, has_lottery_html = self._get_theme_page_impls(
                theme_dir, "Lottery_page"
            )
        can_roll_call = has_roll_call_py or has_roll_call_html
        can_lottery = has_lottery_py or has_lottery_html

        normalized_roll_call_type = self._normalize_theme_type(
            roll_call_theme_type, has_roll_call_py, has_roll_call_html
        )
        normalized_lottery_type = self._normalize_theme_type(
            lottery_theme_type, has_lottery_py, has_lottery_html
        )

        active_roll_call = can_roll_call and self._is_scope_active(
            str(theme_id), roll_call_theme_id
        )
        active_lottery = can_lottery and self._is_scope_active(
            str(theme_id), lottery_theme_id
        )
        active_roll_call_py = active_roll_call and normalized_roll_call_type == "py"
        active_roll_call_html = active_roll_call and normalized_roll_call_type == "html"
        active_lottery_py = active_lottery and normalized_lottery_type == "py"
        active_lottery_html = active_lottery and normalized_lottery_type == "html"
        return {
            "can_apply_roll_call": can_roll_call,
            "can_apply_lottery": can_lottery,
            "can_apply_roll_call_py": has_roll_call_py,
            "can_apply_roll_call_html": has_roll_call_html,
            "can_apply_lottery_py": has_lottery_py,
            "can_apply_lottery_html": has_lottery_html,
            "is_active_roll_call": active_roll_call,
            "is_active_lottery": active_lottery,
            "is_active_roll_call_py": active_roll_call_py,
            "is_active_roll_call_html": active_roll_call_html,
            "is_active_lottery_py": active_lottery_py,
            "is_active_lottery_html": active_lottery_html,
            "is_any_active": active_roll_call or active_lottery,
        }

    def add_market_card(self, info):
        card = ThemeCard(info)
        card.installSignal.connect(self._install_theme)
        self.marketFlowLayout.addWidget(card)

    def add_installed_card(self, info):
        card = ThemeCard(info)
        card.uninstallSignal.connect(self._uninstall_theme)
        self.installedFlowLayout.addWidget(card)

    def _install_theme(self, theme_id):
        logger.info(f"正在安装主题 {theme_id}")
        info = self.market_themes.get(theme_id)
        if not info:
            logger.error(f"无法找到主题信息: {theme_id}")
            return

        thread = InstallThread(info)
        thread.finished_signal.connect(self._on_install_finished)
        thread.finished.connect(lambda: self._remove_thread(thread))
        thread.start()
        self.active_threads.append(thread)

    def _on_install_finished(self, success, msg):
        if success:
            logger.info(f"主题安装成功: {msg}")
            self._reload_ui()
        else:
            logger.error(f"主题安装失败: {msg}")

    def _uninstall_theme(self, theme_id):
        logger.info(f"正在卸载主题 {theme_id}")
        roll_call_theme_id = readme_settings_async(
            "theme_management", "roll_call_theme_id"
        )
        lottery_theme_id = readme_settings_async("theme_management", "lottery_theme_id")
        if str(roll_call_theme_id) == str(theme_id):
            update_settings("theme_management", "roll_call_theme_id", "__none__")
            update_settings("theme_management", "roll_call_theme_type", "")
        if str(lottery_theme_id) == str(theme_id):
            update_settings("theme_management", "lottery_theme_id", "__none__")
            update_settings("theme_management", "lottery_theme_type", "")
        thread = UninstallThread(theme_id)
        thread.finished_signal.connect(self._on_uninstall_finished)
        thread.finished.connect(lambda: self._remove_thread(thread))
        thread.start()
        self.active_threads.append(thread)

    def _apply_theme(self, theme_id, action_key):
        logger.info(f"主题应用操作 {theme_id}: {action_key}")
        roll_call_theme_id = readme_settings_async(
            "theme_management", "roll_call_theme_id"
        )
        lottery_theme_id = readme_settings_async("theme_management", "lottery_theme_id")
        roll_call_theme_type = readme_settings_async(
            "theme_management", "roll_call_theme_type"
        )
        lottery_theme_type = readme_settings_async(
            "theme_management", "lottery_theme_type"
        )
        if action_key == "apply_roll_call":
            update_settings("theme_management", "roll_call_theme_id", theme_id)
        elif action_key == "cancel_roll_call":
            update_settings("theme_management", "roll_call_theme_id", "__none__")
            update_settings("theme_management", "roll_call_theme_type", "")
        elif action_key == "apply_roll_call_py":
            update_settings("theme_management", "roll_call_theme_id", theme_id)
            update_settings("theme_management", "roll_call_theme_type", "py")
        elif action_key == "apply_roll_call_html":
            update_settings("theme_management", "roll_call_theme_id", theme_id)
            update_settings("theme_management", "roll_call_theme_type", "html")
        elif action_key == "cancel_roll_call_py":
            if (
                str(roll_call_theme_id) == str(theme_id)
                and str(roll_call_theme_type) == "py"
            ):
                update_settings("theme_management", "roll_call_theme_id", "__none__")
                update_settings("theme_management", "roll_call_theme_type", "")
        elif action_key == "cancel_roll_call_html":
            if (
                str(roll_call_theme_id) == str(theme_id)
                and str(roll_call_theme_type) == "html"
            ):
                update_settings("theme_management", "roll_call_theme_id", "__none__")
                update_settings("theme_management", "roll_call_theme_type", "")
        elif action_key == "apply_lottery":
            update_settings("theme_management", "lottery_theme_id", theme_id)
        elif action_key == "cancel_lottery":
            update_settings("theme_management", "lottery_theme_id", "__none__")
            update_settings("theme_management", "lottery_theme_type", "")
        elif action_key == "apply_lottery_py":
            update_settings("theme_management", "lottery_theme_id", theme_id)
            update_settings("theme_management", "lottery_theme_type", "py")
        elif action_key == "apply_lottery_html":
            update_settings("theme_management", "lottery_theme_id", theme_id)
            update_settings("theme_management", "lottery_theme_type", "html")
        elif action_key == "cancel_lottery_py":
            if (
                str(lottery_theme_id) == str(theme_id)
                and str(lottery_theme_type) == "py"
            ):
                update_settings("theme_management", "lottery_theme_id", "__none__")
                update_settings("theme_management", "lottery_theme_type", "")
        elif action_key == "cancel_lottery_html":
            if (
                str(lottery_theme_id) == str(theme_id)
                and str(lottery_theme_type) == "html"
            ):
                update_settings("theme_management", "lottery_theme_id", "__none__")
                update_settings("theme_management", "lottery_theme_type", "")
        self._reload_ui()

    def _on_uninstall_finished(self, success, msg):
        if success:
            logger.info(f"主题卸载成功: {msg}")
            self._reload_ui()
        else:
            logger.error(f"主题卸载失败: {msg}")

    def _update_theme(self, theme_id):
        logger.info(f"正在更新主题 {theme_id}")
        self._install_theme(theme_id)

    def _remove_thread(self, thread):
        if thread in self.active_threads:
            self.active_threads.remove(thread)

    def _reload_ui(self):
        self._load_installed_data()
        # 刷新市场列表以更新按钮状态
        if self.market_themes:
            self._on_market_data_loaded(list(self.market_themes.values()))

    def _schedule_installed_reload(self, *_):
        if self.installed_reload_timer.isActive():
            return
        self.installed_reload_timer.start(300)

    def _reset_theme_watcher(self):
        paths = []
        for theme_root in self._get_theme_roots():
            paths.append(str(theme_root))
            for theme_dir in theme_root.iterdir():
                if theme_dir.is_dir():
                    paths.append(str(theme_dir))
                    manifest_path = theme_dir / "manifest.json"
                    if manifest_path.exists():
                        paths.append(str(manifest_path))
        existing = self.theme_watcher.directories() + self.theme_watcher.files()
        if existing:
            self.theme_watcher.removePaths(existing)
        if paths:
            self.theme_watcher.addPaths(paths)
