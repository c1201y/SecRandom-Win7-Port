# ==================================================
# 导入库
# ==================================================
from __future__ import annotations

import os
import ctypes
from ctypes import wintypes
from typing import Dict, Optional, Type

from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from qfluentwidgets import *
from qframelesswindow import *

from app.tools.variable import *
from app.tools.settings_access import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.Language.obtain_language import *


class BackgroundLayer(QWidget):
    def __init__(self, parent: QWidget, target: str):
        super().__init__(parent)
        self._target = str(target or "").strip()
        self._mode = 0
        self._color = QColor("#ffffff")
        self._gradient_start = QColor("#66CCFF")
        self._gradient_end = QColor("#ffffff")
        self._gradient_direction = 0
        self._image_path = ""
        self._brightness = 100
        self._opacity = 100
        self._blur_enable = False
        self._blur_radius = 0
        self._image_valid = False
        self._movie: QMovie | None = None
        self._movie_path = ""
        self._pixmap_cache_key = None
        self._pixmap_cache = QPixmap()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setStyleSheet("background: transparent;")

    def updateGeometryToParent(self):
        p = self.parentWidget()
        if p is not None:
            self.setGeometry(p.rect())

    def applyFromSettings(self):
        prefix = f"{self._target}_background_"
        mode = readme_settings_async("background_management", f"{prefix}mode")
        color = readme_settings_async("background_management", f"{prefix}color")
        gradient_start = readme_settings_async(
            "background_management", f"{prefix}gradient_start"
        )
        gradient_end = readme_settings_async(
            "background_management", f"{prefix}gradient_end"
        )
        gradient_direction = readme_settings_async(
            "background_management", f"{prefix}gradient_direction"
        )
        gradient_direction_v2 = readme_settings_async(
            "background_management", f"{prefix}gradient_direction_v2"
        )
        image_path = readme_settings_async("background_management", f"{prefix}image")
        brightness = readme_settings_async(
            "background_management", f"{prefix}brightness"
        )
        opacity = readme_settings_async("background_management", f"{prefix}opacity")
        blur_enable = readme_settings_async(
            "background_management", f"{prefix}blur_enable"
        )
        blur_radius = readme_settings_async(
            "background_management", f"{prefix}blur_radius"
        )

        try:
            self._mode = int(mode) if mode is not None else 0
        except Exception:
            self._mode = 0

        try:
            self._color = QColor(str(color or "#ffffff"))
            if not self._color.isValid():
                self._color = QColor("#ffffff")
        except Exception:
            self._color = QColor("#ffffff")

        try:
            self._gradient_start = QColor(str(gradient_start or color or "#66CCFF"))
            if not self._gradient_start.isValid():
                self._gradient_start = QColor("#66CCFF")
        except Exception:
            self._gradient_start = QColor("#66CCFF")

        try:
            self._gradient_end = QColor(str(gradient_end or "#ffffff"))
            if not self._gradient_end.isValid():
                self._gradient_end = QColor("#ffffff")
        except Exception:
            self._gradient_end = QColor("#ffffff")

        try:
            self._gradient_direction = (
                int(gradient_direction) if gradient_direction is not None else 0
            )
        except Exception:
            self._gradient_direction = 0
        if not bool(gradient_direction_v2):
            old_to_new = {0: 0, 1: 2, 2: 4, 3: 6}
            update_settings(
                "background_management",
                f"{prefix}gradient_direction_v2",
                True,
            )
            mapped = old_to_new.get(self._gradient_direction, self._gradient_direction)
            if mapped != self._gradient_direction:
                self._gradient_direction = mapped
                update_settings(
                    "background_management",
                    f"{prefix}gradient_direction",
                    int(self._gradient_direction),
                )
        self._gradient_direction = max(0, min(7, self._gradient_direction))

        self._image_path = str(image_path or "")

        try:
            self._brightness = int(brightness) if brightness is not None else 100
        except Exception:
            self._brightness = 100

        self._brightness = max(0, min(200, self._brightness))

        try:
            self._opacity = int(opacity) if opacity is not None else 100
        except Exception:
            self._opacity = 100
        self._opacity = max(0, min(100, self._opacity))

        self._blur_enable = bool(blur_enable)
        try:
            self._blur_radius = int(blur_radius) if blur_radius is not None else 0
        except Exception:
            self._blur_radius = 0
        self._blur_radius = max(0, min(40, self._blur_radius))

        if self._blur_enable and self._blur_radius > 0:
            effect = self.graphicsEffect()
            if not isinstance(effect, QGraphicsBlurEffect):
                effect = QGraphicsBlurEffect(self)
                self.setGraphicsEffect(effect)
            try:
                effect.setBlurRadius(self._blur_radius)
            except Exception:
                pass
        else:
            self.setGraphicsEffect(None)

        self._image_valid = False
        if self._mode == 2:
            path = str(self._image_path or "")
            if path and os.path.exists(path) and path.lower().endswith(".gif"):
                self._ensure_movie(path)
                self._image_valid = self._movie is not None
            else:
                self._stop_movie()
                if path and os.path.exists(path):
                    try:
                        self._image_valid = not QPixmap(path).isNull()
                    except Exception:
                        self._image_valid = False
                else:
                    self._image_valid = False
        else:
            self._stop_movie()

        if self._mode == 0 or (self._mode == 2 and not self._image_valid):
            self.hide()
        else:
            self.show()
        self._invalidate_pixmap_cache()
        self.update()

    def handleSettingChanged(self, group: str, key: str):
        if group != "background_management":
            return
        if not str(key or "").startswith(f"{self._target}_background_"):
            return
        self.applyFromSettings()

    def _invalidate_pixmap_cache(self):
        cache_key = (self._image_path, self._brightness)
        if cache_key != self._pixmap_cache_key:
            self._pixmap_cache_key = cache_key
            self._pixmap_cache = QPixmap()

    def _stop_movie(self):
        movie = getattr(self, "_movie", None)
        if movie is None:
            self._movie_path = ""
            return
        try:
            movie.frameChanged.disconnect(self._on_movie_frame_changed)
        except Exception:
            pass
        try:
            movie.stop()
        except Exception:
            pass
        self._movie = None
        self._movie_path = ""

    def _ensure_movie(self, path: str):
        path = str(path or "")
        if not path:
            self._stop_movie()
            return
        if getattr(self, "_movie", None) is not None and self._movie_path == path:
            if (
                self._movie is not None
                and self._movie.state() != QMovie.MovieState.Running
            ):
                try:
                    self._movie.start()
                except Exception:
                    pass
            return

        self._stop_movie()
        movie = QMovie(path)
        movie.setCacheMode(QMovie.CacheMode.CacheNone)
        movie.frameChanged.connect(self._on_movie_frame_changed)
        self._movie = movie
        self._movie_path = path
        try:
            movie.start()
        except Exception:
            self._stop_movie()
            return

        try:
            if not movie.jumpToFrame(0) or movie.currentPixmap().isNull():
                self._stop_movie()
        except Exception:
            self._stop_movie()

    def _on_movie_frame_changed(self, _frame: int):
        self.update()

    def _get_pixmap(self) -> QPixmap:
        if self._pixmap_cache_key != (self._image_path, self._brightness):
            self._invalidate_pixmap_cache()

        if not self._pixmap_cache.isNull():
            return self._pixmap_cache

        if not self._image_path:
            return QPixmap()

        if str(self._image_path or "").lower().endswith(".gif"):
            return QPixmap()

        try:
            pixmap = QPixmap(self._image_path)
        except Exception:
            pixmap = QPixmap()

        if pixmap.isNull():
            return QPixmap()

        self._pixmap_cache = pixmap
        return pixmap

    def _draw_scaled_cover(self, painter: QPainter, pixmap: QPixmap):
        if pixmap.isNull():
            return
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        pw = pixmap.width()
        ph = pixmap.height()
        if pw <= 0 or ph <= 0:
            return

        ratio = max(w / pw, h / ph)
        sw = int(pw * ratio)
        sh = int(ph * ratio)
        scaled = pixmap.scaled(
            sw,
            sh,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (sw - w) // 2
        y = (sh - h) // 2
        cropped = scaled.copy(x, y, w, h)
        painter.drawPixmap(0, 0, cropped)

    def _apply_brightness_overlay(self, painter: QPainter, opacity: float):
        if self._brightness == 100:
            return
        if self._brightness > 100:
            alpha = int((self._brightness - 100) / 100 * 180)
            alpha = max(0, min(180, alpha))
            painter.fillRect(self.rect(), QColor(255, 255, 255, int(alpha * opacity)))
        else:
            alpha = int((100 - self._brightness) / 100 * 180)
            alpha = max(0, min(180, alpha))
            painter.fillRect(self.rect(), QColor(0, 0, 0, int(alpha * opacity)))

    def paintEvent(self, event):
        if self._mode == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        opacity = max(0.0, min(1.0, float(self._opacity) / 100))

        if self._mode == 1:
            c = QColor(self._color)
            c.setAlpha(int(opacity * 255))
            painter.fillRect(self.rect(), c)
            return

        if self._mode == 3:
            sc = QColor(self._gradient_start)
            ec = QColor(self._gradient_end)
            sc.setAlpha(int(opacity * 255))
            ec.setAlpha(int(opacity * 255))

            w = self.width()
            h = self.height()
            if w <= 0 or h <= 0:
                return

            d = int(getattr(self, "_gradient_direction", 0))
            if d == 1:
                gradient = QLinearGradient(0, h, 0, 0)
            elif d == 2:
                gradient = QLinearGradient(0, 0, w, 0)
            elif d == 3:
                gradient = QLinearGradient(w, 0, 0, 0)
            elif d == 4:
                gradient = QLinearGradient(0, 0, w, h)
            elif d == 5:
                gradient = QLinearGradient(w, h, 0, 0)
            elif d == 6:
                gradient = QLinearGradient(w, 0, 0, h)
            elif d == 7:
                gradient = QLinearGradient(0, h, w, 0)
            else:
                gradient = QLinearGradient(0, 0, 0, h)

            gradient.setColorAt(0.0, sc)
            gradient.setColorAt(1.0, ec)
            painter.fillRect(self.rect(), gradient)
            return

        if self._mode == 2:
            if not getattr(self, "_image_valid", False):
                return

            c = QColor(self._color)
            c.setAlpha(int(opacity * 255))
            painter.fillRect(self.rect(), c)
            painter.save()
            painter.setOpacity(opacity)
            pixmap = QPixmap()
            movie = getattr(self, "_movie", None)
            if movie is not None:
                pixmap = movie.currentPixmap()
            else:
                pixmap = self._get_pixmap()
            if not pixmap.isNull():
                self._draw_scaled_cover(painter, pixmap)
            painter.restore()
            if not pixmap.isNull():
                self._apply_brightness_overlay(painter, opacity)
            return


class SimpleWindowTemplate(FramelessWindow):
    """简单窗口模板类

    提供一个更简单的窗口模板，不包含导航栏，适用于简单的对话框或弹出窗口。
    该类继承自FramelessWindow，提供了页面管理功能，可以动态添加、切换和移除页面。

    特性:
    - 无边框窗口设计，带有标准标题栏
    - 支持多页面管理，使用QStackedWidget实现页面切换
    - 提供页面添加、移除和切换的便捷方法
    - 支持从页面模板或已有控件创建页面
    - 窗口关闭时发出windowClosed信号

    使用示例:
        # 创建简单窗口
        window = SimpleWindowTemplate("我的窗口", parent=None)

        # 从页面模板添加页面
        page_instance = window.add_page_from_template("settings", SettingsPage)

        # 从已有控件添加页面
        custom_widget = QWidget()
        window.add_page_from_widget("custom", custom_widget)

        # 切换到指定页面
        window.switch_to_page("settings")

        # 显示窗口
        window.show()

    信号:
        windowClosed: 窗口关闭时发出，无参数

    属性:
        parent_window: 父窗口引用
        pages: 页面类字典 {page_name: page_class}
        page_instances: 页面实例字典 {page_name: page_instance}
        stacked_widget: 页面堆叠窗口控件
        main_layout: 主布局
    """

    # 信号定义
    windowClosed = Signal()
    _DEFAULT_TITLEBAR_HEIGHT = 32
    _TITLEBAR_LEFT_OFFSET_PX = 5

    def __init__(
        self,
        title: str = "窗口",
        width: int = 700,
        height: int = 500,
        parent: Optional[QWidget] = None,
    ):
        """
        初始化简单窗口模板

        Args:
            title: 窗口标题
            width: 窗口宽度
            height: 窗口高度
            parent: 父窗口
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._sr_close_guard_enabled = False
        self._sr_allow_close_once = False
        self._sr_close_guard_last_log_ms = 0
        self._sr_close_buttons = []
        self._sr_close_guard_hooks_installed = False

        # 保存父窗口引用
        self.parent_window = parent

        # 存储页面
        self.pages: Dict[str, Type] = {}
        self.page_instances: Dict[str, QWidget] = {}

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self._sync_layout_margins_with_titlebar()
        self.main_layout.setSpacing(0)

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)

        # 连接信号
        self.__connectSignalToSlot()

        # 直接创建UI组件，不使用延迟初始化
        self.create_ui_components()

        # 初始化窗口
        self.initWindow(title, width, height)

    def _sync_layout_margins_with_titlebar(self) -> None:
        top = 0
        try:
            top = int(self.titleBar.height()) if self.titleBar else 0
        except Exception:
            top = 0

        if top <= 1:
            try:
                top = int(self.titleBar.sizeHint().height()) if self.titleBar else 0
            except Exception:
                top = 0

        if top <= 1:
            top = self._DEFAULT_TITLEBAR_HEIGHT

        self.main_layout.setContentsMargins(0, top, 0, 0)

    def _apply_titlebar_font(self) -> None:
        custom_font = load_custom_font()
        try:
            if getattr(self, "_sr_title_text_label", None) is not None:
                if custom_font:
                    self._sr_title_text_label.setFont(QFont(custom_font, 9))
                else:
                    f = self._sr_title_text_label.font()
                    f.setPointSize(9)
                    self._sr_title_text_label.setFont(f)
        except Exception:
            pass

        for child in self.titleBar.findChildren(QLabel):
            if not isinstance(child, QLabel):
                continue
            label_text = child.text() if hasattr(child, "text") else ""
            if not label_text:
                continue
            if custom_font:
                child.setFont(QFont(custom_font, 9))
            else:
                f = child.font()
                f.setPointSize(9)
                child.setFont(f)
            break

    def _ensure_sr_title_overlay(self) -> None:
        if getattr(self, "_sr_title_overlay", None) is not None:
            return

        self._sr_title_overlay = QWidget(self.titleBar)
        self._sr_title_overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._sr_title_overlay.setObjectName("srTitleOverlay")

        layout = QHBoxLayout(self._sr_title_overlay)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._sr_title_icon_label = QLabel(self._sr_title_overlay)
        self._sr_title_icon_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._sr_title_icon_label.setObjectName("srTitleIcon")
        self._sr_title_icon_label.setFixedSize(16, 16)

        self._sr_title_text_label = QLabel(self._sr_title_overlay)
        self._sr_title_text_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._sr_title_text_label.setObjectName("srTitleLabel")
        self._sr_title_text_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )

        layout.addWidget(self._sr_title_icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._sr_title_text_label, 0, Qt.AlignmentFlag.AlignVCenter)

        try:
            self.windowTitleChanged.connect(self._update_sr_title_overlay)
            self.windowIconChanged.connect(self._update_sr_title_overlay)
        except Exception:
            pass

    def _update_sr_title_overlay(self, *args) -> None:
        try:
            if getattr(self, "_sr_title_text_label", None) is None:
                return

            title = self.windowTitle() or ""
            self._sr_title_text_label.setText(title)

            icon = self.windowIcon()
            pixmap = None
            try:
                if icon and not icon.isNull():
                    pixmap = icon.pixmap(16, 16)
            except Exception:
                pixmap = None

            if pixmap is not None and not pixmap.isNull():
                self._sr_title_icon_label.setPixmap(pixmap)
                self._sr_title_icon_label.show()
            else:
                self._sr_title_icon_label.hide()

            self._sr_title_overlay.adjustSize()
        except Exception as e:
            logger.exception(f"更新自定义标题栏失败: {e}")

    def _position_sr_title_overlay(self) -> None:
        try:
            if getattr(self, "_sr_title_overlay", None) is None:
                return
            self._sr_title_overlay.adjustSize()
            x = int(self._TITLEBAR_LEFT_OFFSET_PX)
            y = max(
                0, int((self.titleBar.height() - self._sr_title_overlay.height()) / 2)
            )
            self._sr_title_overlay.move(x, y)
            self._sr_title_overlay.raise_()
        except Exception as e:
            logger.exception(f"定位自定义标题栏失败: {e}")

    def _rebuild_titlebar_title_and_icon(self) -> None:
        try:
            if not self.titleBar:
                return

            current_title = self.windowTitle() or ""
            for child in self.titleBar.findChildren(QLabel):
                if child.objectName() in {"srTitleIcon", "srTitleLabel"}:
                    continue

                try:
                    pixmap = child.pixmap()
                except Exception:
                    pixmap = None

                label_text = child.text() if hasattr(child, "text") else ""
                is_original_icon = pixmap is not None and not pixmap.isNull()
                is_original_title = bool(current_title) and label_text == current_title

                if is_original_icon or is_original_title:
                    child.hide()

            self._ensure_sr_title_overlay()
            self._update_sr_title_overlay()
            self._apply_titlebar_font()
            self._position_sr_title_overlay()
        except Exception as e:
            logger.exception(f"重建标题栏标题失败: {e}")

    def _apply_titlebar_left_offset(self) -> None:
        try:
            for child in self.titleBar.findChildren(QWidget):
                if (
                    isinstance(child, QWidget)
                    and child.property("srTitleOffset") is not None
                ):
                    child.setProperty("srTitleOffset", None)

            icon_label = None
            title_label = None

            labels = self.titleBar.findChildren(QLabel)
            current_title = self.windowTitle() or ""

            for child in labels:
                try:
                    pixmap = child.pixmap()
                except Exception:
                    pixmap = None

                if pixmap is not None and not pixmap.isNull():
                    icon_label = child

                label_text = child.text() if hasattr(child, "text") else ""
                if current_title and label_text == current_title:
                    title_label = child
                if label_text and title_label is None:
                    title_label = child

            if icon_label is None and title_label is None:
                return

            offset = int(self._TITLEBAR_LEFT_OFFSET_PX)
            if icon_label is not None:
                icon_label.setProperty("srTitleOffset", "true")
                m = icon_label.contentsMargins()
                icon_label.setContentsMargins(offset, m.top(), m.right(), m.bottom())
            if title_label is not None:
                title_label.setProperty("srTitleOffset", "true")
                m = title_label.contentsMargins()
                title_label.setContentsMargins(offset, m.top(), m.right(), m.bottom())
            self.titleBar.style().unpolish(self.titleBar)
            self.titleBar.style().polish(self.titleBar)
        except Exception as e:
            logger.exception(f"设置标题栏偏移失败: {e}")

    def initWindow(self, title: str, width: int = 700, height: int = 500) -> None:
        """初始化窗口"""
        self.setTitleBar(FluentTitleBar(self))
        try:
            fixed_h = max(
                int(self.titleBar.sizeHint().height()), self._DEFAULT_TITLEBAR_HEIGHT
            )
            self.titleBar.setFixedHeight(fixed_h)
        except Exception:
            self.titleBar.setFixedHeight(self._DEFAULT_TITLEBAR_HEIGHT)

        self._install_sr_close_guard_hooks()
        self._sync_layout_margins_with_titlebar()
        self.setMinimumSize(MINIMUM_WINDOW_SIZE[0], MINIMUM_WINDOW_SIZE[1])
        self.resize(width, height)
        window_icon = QIcon(
            str(get_data_path("assets/icon", "secrandom-icon-paper.ico"))
        )
        self.setWindowIcon(window_icon)
        self.setWindowTitle(title)
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.titleBar.raise_()
        self._apply_titlebar_font()
        self._rebuild_titlebar_title_and_icon()

        # 确保在设置标题栏后应用当前主题和自定义字体
        self._apply_current_theme()
        self._setup_background_layer()

        if self.parent_window is None:
            screen = QApplication.primaryScreen().availableGeometry()
            w, h = screen.width(), screen.height()
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def enable_close_guard(self, enabled: bool = True) -> None:
        self._sr_close_guard_enabled = bool(enabled)
        if self._sr_close_guard_enabled:
            self._install_sr_close_guard_hooks()

    def _is_sr_close_button(self, btn: QAbstractButton) -> bool:
        try:
            name = str(btn.objectName() or "")
        except Exception:
            name = ""
        try:
            tooltip = str(btn.toolTip() or "")
        except Exception:
            tooltip = ""

        n = name.lower()
        t = tooltip.lower()

        if n in {"closebutton", "closebtn"}:
            return True
        if "close" in n and "disclose" not in n:
            return True
        if "close" in t or "关闭" in tooltip or "退出" in tooltip:
            return True
        return False

    def _sr_mark_allow_close_once(self) -> None:
        self._sr_allow_close_once = True

    def _find_sr_close_button_by_layout(self) -> QAbstractButton | None:
        if not self.titleBar:
            return None
        try:
            candidates = [
                b
                for b in self.titleBar.findChildren(QAbstractButton)
                if b is not None and b.isVisible() and b.width() > 0 and b.height() > 0
            ]
        except Exception:
            candidates = []
        if not candidates:
            return None
        try:
            candidates.sort(
                key=lambda b: b.mapToGlobal(QPoint(b.width(), int(b.height() / 2))).x()
            )
        except Exception:
            return None
        return candidates[-1] if candidates else None

    def _install_sr_titlebar_press_guard(self) -> None:
        try:
            if not self.titleBar:
                return
            if bool(getattr(self, "_sr_titlebar_press_guard_installed", False)):
                return
            self.titleBar.installEventFilter(self)
            self._sr_titlebar_press_guard_installed = True
        except Exception:
            pass

    def _install_sr_close_guard_hooks(self) -> None:
        try:
            if not self.titleBar:
                return
            existing = set(getattr(self, "_sr_close_buttons", []))
            found = 0
            buttons = list(self.titleBar.findChildren(QAbstractButton))
            layout_close = self._find_sr_close_button_by_layout()
            if layout_close is not None:
                buttons.append(layout_close)
            for btn in buttons:
                if btn is None:
                    continue
                if btn is not layout_close and not self._is_sr_close_button(btn):
                    continue
                if btn in existing:
                    continue
                try:
                    btn.clicked.connect(self._sr_mark_allow_close_once)
                except Exception:
                    pass
                try:
                    btn.installEventFilter(self)
                except Exception:
                    pass
                self._sr_close_buttons.append(btn)
                found += 1
            if found > 0:
                self._sr_close_guard_hooks_installed = True
                self._install_sr_titlebar_press_guard()
        except Exception:
            pass

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        try:
            if (
                self._sr_close_guard_enabled
                and watched is not None
                and self.titleBar is not None
                and watched is self.titleBar
                and event.type() == QEvent.Type.MouseButtonPress
            ):
                try:
                    pos = event.position().toPoint()
                except Exception:
                    pos = None
                if pos is not None:
                    w = int(self.titleBar.width() or 0)
                    h = int(self.titleBar.height() or 0)
                    if w > 0 and h > 0 and pos.x() >= w - 120 and 0 <= pos.y() <= h:
                        self._sr_allow_close_once = True

            if (
                self._sr_close_guard_enabled
                and watched is not None
                and watched in getattr(self, "_sr_close_buttons", [])
            ):
                if event.type() == QEvent.Type.MouseButtonPress:
                    self._sr_allow_close_once = True
        except Exception:
            pass
        return super().eventFilter(watched, event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_layout_margins_with_titlebar)
        QTimer.singleShot(0, self._rebuild_titlebar_title_and_icon)
        if bool(getattr(self, "_sr_close_guard_enabled", False)):
            QTimer.singleShot(0, self._install_sr_close_guard_hooks)
        try:
            if getattr(self, "_background_layer", None) is not None:
                self._background_layer.updateGeometryToParent()
        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_layout_margins_with_titlebar()
        self._position_sr_title_overlay()
        try:
            if getattr(self, "_background_layer", None) is not None:
                self._background_layer.updateGeometryToParent()
        except Exception:
            pass

    def keyPressEvent(self, event) -> None:
        try:
            if self._sr_close_guard_enabled:
                key = event.key()
                modifiers = event.modifiers()
                if key == Qt.Key_F4 and (modifiers & Qt.AltModifier):
                    try:
                        event.accept()
                    except Exception:
                        pass
                    return
        except Exception:
            pass
        return super().keyPressEvent(event)

    def _sr_is_recent_user_input(self, max_age_ms: int) -> bool:
        try:
            if os.name != "nt":
                return True
            max_age_ms = int(max_age_ms or 0)
            if max_age_ms <= 0:
                return False

            class _LASTINPUTINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("dwTime", wintypes.DWORD),
                ]

            lii = _LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
            if not bool(ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))):
                return False
            tick = int(ctypes.windll.kernel32.GetTickCount() or 0)
            last = int(lii.dwTime or 0)
            age = (tick - last) & 0xFFFFFFFF
            return int(age) <= max_age_ms
        except Exception:
            return False

    def _sr_is_foreground_window(self) -> bool:
        try:
            if os.name != "nt":
                return True
            hwnd = int(self.winId() or 0)
            if not hwnd:
                return False
            fg = int(ctypes.windll.user32.GetForegroundWindow() or 0)
            return fg == hwnd
        except Exception:
            return False

    def nativeEvent(self, eventType, message):
        try:
            if os.name == "nt" and bool(
                getattr(self, "_sr_close_guard_enabled", False)
            ):
                msg = ctypes.cast(int(message), ctypes.POINTER(wintypes.MSG)).contents
                if int(msg.message) == 0x0112 and (int(msg.wParam) & 0xFFF0) == 0xF060:
                    lparam = int(msg.lParam) if msg.lParam is not None else 0
                    is_keyboard_close = lparam == 0
                    if (
                        not is_keyboard_close
                        and self._sr_is_foreground_window()
                        and self._sr_is_recent_user_input(1500)
                    ):
                        self._sr_allow_close_once = True
        except Exception:
            pass

        try:
            return super().nativeEvent(eventType, message)
        except Exception:
            return False, 0

    def __connectSignalToSlot(self) -> None:
        """连接信号与槽"""
        try:
            qconfig.themeChanged.connect(self._on_theme_changed)
        except Exception as e:
            logger.exception(f"连接信号时发生未知错误: {e}")

    def _on_theme_changed(self) -> None:
        """主题变化时自动更新窗口背景"""
        try:
            # 强制刷新窗口背景
            self._apply_current_theme()
            pass
        except Exception as e:
            logger.exception(f"主题变化时更新窗口背景失败: {e}")

    def _is_dark_mode_by_settings(self) -> bool:
        try:
            current_theme = readme_settings("basic_settings", "theme")
            if current_theme == "DARK":
                return True
            if current_theme == "AUTO":
                try:
                    from darkdetect import isDark

                    return bool(isDark())
                except Exception as e:
                    logger.exception(
                        "Error detecting dark mode with darkdetect (fallback to light): {}",
                        e,
                    )
                    return False
            return False
        except Exception:
            return False

    def _apply_current_theme(self) -> None:
        """应用当前主题设置到窗口"""
        try:
            current_theme = readme_settings("basic_settings", "theme")
            is_dark = self._is_dark_mode_by_settings()
            background_color = "#202020" if is_dark else "#ffffff"

            self.setStyleSheet(f"background-color: {background_color};")
            self.default_page.setStyleSheet("background-color: transparent;")

            self._set_titlebar_colors(is_dark)

            logger.debug(f"窗口主题已更新为: {current_theme}")
        except Exception as e:
            logger.exception(f"应用主题时出错: {e}")
            # 设置默认的浅色背景作为备选
            self.setStyleSheet("background-color: #ffffff;")
            self.default_page.setStyleSheet("background-color: transparent;")

    def _setup_background_layer(self):
        if getattr(self, "_background_layer", None) is None:
            self._background_layer = BackgroundLayer(
                self, "notification_floating_window"
            )
            self._background_layer.updateGeometryToParent()
            self._background_layer.lower()

            try:
                get_settings_signals().settingChanged.connect(
                    lambda first,
                    second,
                    value: self._background_layer.handleSettingChanged(first, second)
                )
            except Exception:
                pass

        try:
            self._background_layer.applyFromSettings()
        except Exception:
            pass

    def _set_titlebar_colors(self, is_dark: bool) -> None:
        """设置标题栏颜色"""
        try:
            if is_dark:
                title_color = "#ffffff"  # 白色文字
                background_color = "#202020"
            else:
                title_color = "#000000"  # 黑色文字
                background_color = "#ffffff"

            if hasattr(self.titleBar, "setTitle") and hasattr(self.titleBar, "setIcon"):
                titlebar_style = f"""
                    QWidget {{
                        background-color: {background_color};
                    }}
                    QLabel {{
                        background-color: transparent;
                    }}
                    QLabel#srTitleLabel {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    *[srTitleOffset="true"] {{
                        margin-left: {self._TITLEBAR_LEFT_OFFSET_PX}px;
                    }}
                """
            else:
                titlebar_style = f"""
                    QWidget {{
                        color: {title_color};
                        background-color: {background_color};
                    }}
                    QLabel {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    QLabel#srTitleLabel {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    *[srTitleOffset="true"] {{
                        margin-left: {self._TITLEBAR_LEFT_OFFSET_PX}px;
                    }}
                    QPushButton {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    QToolButton {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    QAbstractButton {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    #minimizeButton, #maximizeButton, #closeButton,
                    #minBtn, #maxBtn, #closeBtn,
                    #minimizeBtn, #maximizeBtn, #closeBtn {{
                        color: {title_color};
                        background-color: transparent;
                    }}
                    #minimizeButton:hover, #maximizeButton:hover, #closeButton:hover,
                    #minBtn:hover, #maxBtn:hover, #closeBtn:hover,
                    #minimizeBtn:hover, #maximizeBtn:hover, #closeBtn:hover {{
                        background-color: rgba(255, 255, 255, 0.1);
                    }}
                    #closeButton:hover, #closeBtn:hover {{
                        background-color: rgba(232, 17, 35, 0.8);
                    }}
                """

            self.titleBar.setStyleSheet(titlebar_style)

            logger.debug(
                f"标题栏颜色已设置: 文字色={title_color}, 背景色={background_color}"
            )
        except Exception as e:
            logger.exception(f"设置标题栏颜色失败: {e}")

    def create_ui_components(self) -> None:
        """创建UI组件"""
        try:
            # 创建默认页面
            self.default_page = QWidget()
            default_layout = QVBoxLayout(self.default_page)
            default_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 添加默认页面到堆叠窗口
            self.stacked_widget.addWidget(self.default_page)
        except Exception as e:
            logger.exception(f"创建UI组件时出错: {e}")
            raise

    def add_page_from_template(
        self, page_name: str, page_class: Type, **kwargs
    ) -> Optional[QWidget]:
        """
        从页面模板添加页面

        Args:
            page_name: 页面名称（唯一标识）
            page_class: 页面类
            **kwargs: 传递给页面类构造函数的额外参数

        Returns:
            页面实例，如果创建失败则返回None
        """
        # 输入验证
        if not page_name or not isinstance(page_name, str):
            logger.exception("页面名称必须是非空字符串")
            return None

        if page_name in self.page_instances:
            logger.warning(f"页面 {page_name} 已存在，将返回现有实例")
            return self.page_instances[page_name]

        try:
            # 创建页面实例，传递额外参数
            page_instance = page_class(self, **kwargs)

            # 设置对象名称
            page_instance.setObjectName(page_name)

            # 添加到堆叠窗口
            self.stacked_widget.addWidget(page_instance)

            # 存储页面
            self.page_instances[page_name] = page_instance
            self.pages[page_name] = page_class
            return page_instance
        except Exception as e:
            logger.exception(f"创建页面 {page_name} 时出错: {e}")
            return None

    def add_page_from_widget(self, page_name: str, widget: QWidget) -> QWidget:
        """
        从控件添加页面

        Args:
            page_name: 页面名称（唯一标识）
            widget: 页面控件

        Returns:
            页面控件

        Raises:
            ValueError: 如果输入参数无效
        """
        # 输入验证
        if not page_name or not isinstance(page_name, str):
            raise ValueError("页面名称必须是非空字符串")

        if page_name in self.page_instances:
            logger.warning(f"页面 {page_name} 已存在，将返回现有实例")
            return self.page_instances[page_name]

        # 设置对象名称
        widget.setObjectName(page_name)

        try:
            # 添加到堆叠窗口
            self.stacked_widget.addWidget(widget)

            # 存储页面
            self.page_instances[page_name] = widget
            return widget
        except Exception as e:
            logger.exception(f"添加页面 {page_name} 到堆叠窗口时出错: {e}")
            raise

    def get_page(self, page_name: str) -> Optional[QWidget]:
        """
        获取页面实例

        Args:
            page_name: 页面名称

        Returns:
            页面实例，如果不存在则返回None
        """
        # 输入验证
        if not page_name or not isinstance(page_name, str):
            logger.warning("页面名称必须是非空字符串")
            return None

        page = self.page_instances.get(page_name, None)
        if page is None:
            logger.debug(f"请求的页面 {page_name} 不存在")

        return page

    def remove_page(self, page_name: str) -> bool:
        """
        移除页面

        Args:
            page_name: 页面名称

        Returns:
            是否成功移除页面
        """
        # 输入验证
        if not page_name or not isinstance(page_name, str):
            logger.exception("页面名称必须是非空字符串")
            return False

        if page_name not in self.page_instances:
            logger.warning(f"尝试移除不存在的页面: {page_name}")
            return False

        try:
            page = self.page_instances[page_name]

            # 如果当前显示的是要删除的页面，先切换到默认页面
            if self.stacked_widget.currentWidget() == page:
                if self.default_page:
                    self.stacked_widget.setCurrentWidget(self.default_page)
                else:
                    logger.warning(
                        f"删除当前显示的页面 {page_name} 但没有默认页面可切换"
                    )

            # 从堆叠窗口中移除
            self.stacked_widget.removeWidget(page)

            # 从存储中移除
            del self.page_instances[page_name]
            if page_name in self.pages:
                del self.pages[page_name]
            return True
        except Exception as e:
            logger.exception(f"移除页面 {page_name} 时出错: {e}")
            return False

    def switch_to_page(self, page_name: str) -> bool:
        """
        切换到指定页面

        Args:
            page_name: 页面名称

        Returns:
            是否成功切换到页面
        """
        # 输入验证
        if not page_name or not isinstance(page_name, str):
            logger.exception("页面名称必须是非空字符串")
            return False

        if page_name not in self.page_instances:
            logger.warning(f"尝试切换到不存在的页面: {page_name}")
            return False

        try:
            target_page = self.page_instances[page_name]
            current_page = self.stacked_widget.currentWidget()

            # 检查是否已经在目标页面
            if current_page == target_page:
                return True

            # 切换页面
            self.stacked_widget.setCurrentWidget(target_page)
            return True
        except Exception as e:
            logger.exception(f"切换到页面 {page_name} 时出错: {e}")
            return False

    def closeEvent(self, event) -> None:
        """窗口关闭事件处理"""
        try:
            if (
                self._sr_close_guard_enabled
                and not getattr(self, "_sr_allow_close_once", False)
                and not QApplication.instance().closingDown()
            ):
                try:
                    event.ignore()
                except Exception:
                    pass
                now_ms = int(QDateTime.currentMSecsSinceEpoch() or 0)
                if now_ms - int(self._sr_close_guard_last_log_ms or 0) >= 5000:
                    self._sr_close_guard_last_log_ms = now_ms
                    logger.warning("检测到外部关闭请求，已阻止关闭窗口")
                try:
                    if self.isMinimized():
                        self.showNormal()
                    self.show()
                    self.raise_()
                    self.activateWindow()
                except Exception:
                    pass
                return
        finally:
            self._sr_allow_close_once = False
        try:
            qconfig.themeChanged.disconnect(self._on_theme_changed)
        except Exception:
            pass
        self.windowClosed.emit()
        super().closeEvent(event)
