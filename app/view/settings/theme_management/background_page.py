from __future__ import annotations

import os

from PySide2.QtCore import Qt, QEvent, QTimer
from PySide2.QtGui import QColor, QImage, QLinearGradient, QMovie, QPainter, QPixmap
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QFileDialog,
    QLabel,
    QLineEdit,
    QSlider,
    QSizePolicy,
    QScroller,
    QGraphicsBlurEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
)
from qfluentwidgets import (
    GroupHeaderCardWidget,
    ComboBox,
    SingleDirectionScrollArea,
    SettingCard,
    ColorConfigItem,
    ColorSettingCard,
    PushButton,
    SwitchButton,
)

from app.Language.obtain_language import (
    get_content_combo_name_async,
    get_content_description_async,
    get_content_name_async,
    get_content_pushbutton_name_async,
    get_content_switchbutton_name_async,
)
from app.tools.personalised import get_theme_icon
from app.tools.settings_access import readme_settings_async, update_settings
from app.tools.variable import SUPPORTED_IMAGE_EXTENSIONS


class BackgroundManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        self.scrollArea = SingleDirectionScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
            """
        )
        QScroller.grabGesture(
            self.scrollArea.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture,
        )

        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("backgroundScrollWidget")
        self.scrollWidget.setStyleSheet("background: transparent;")

        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(10)

        self.mainWindowGroup = _BackgroundGroup(
            "main_window",
            get_content_name_async("theme_management", "main_window_background"),
            parent=self.scrollWidget,
        )
        self.settingsWindowGroup = _BackgroundGroup(
            "settings_window",
            get_content_name_async("theme_management", "settings_window_background"),
            parent=self.scrollWidget,
        )
        self.secRandomWindowGroup = _BackgroundGroup(
            "notification_floating_window",
            get_content_name_async(
                "theme_management", "notification_floating_window_background"
            ),
            parent=self.scrollWidget,
        )

        self.scrollLayout.addWidget(self.mainWindowGroup)
        self.scrollLayout.addWidget(self.settingsWindowGroup)
        self.scrollLayout.addWidget(self.secRandomWindowGroup)
        self.scrollLayout.addStretch(1)

        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)


class _BackgroundGroup(GroupHeaderCardWidget):
    def __init__(self, target: str, title: str, parent=None):
        super().__init__(parent=parent)
        self._target = str(target or "").strip()
        self.setTitle(title)
        self.setBorderRadius(8)
        self._preview_movie: QMovie | None = None

        self.modeCombo = ComboBox()
        self.modeCombo.addItems(
            get_content_combo_name_async("theme_management", "background_mode")
        )

        mode = readme_settings_async(
            "background_management", f"{self._target}_background_mode"
        )
        try:
            self.modeCombo.setCurrentIndex(int(mode) if mode is not None else 0)
        except Exception:
            self.modeCombo.setCurrentIndex(0)

        self.modeCombo.currentIndexChanged.connect(self._on_mode_changed)

        self.colorItem = ColorConfigItem(
            "background_management",
            f"{self._target}_background_color",
            readme_settings_async(
                "background_management", f"{self._target}_background_color"
            ),
        )
        self.colorItem.valueChanged.connect(
            lambda color: update_settings(
                "background_management",
                f"{self._target}_background_color",
                color.name(),
            )
        )
        self.colorItem.valueChanged.connect(lambda _color: self._refresh_preview())

        self.colorCard = ColorSettingCard(
            self.colorItem,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr(get_content_name_async("theme_management", "background_color")),
            self.tr(
                get_content_description_async("theme_management", "background_color")
            ),
            parent=self,
        )

        gradient_start = readme_settings_async(
            "background_management", f"{self._target}_background_gradient_start"
        )
        if not gradient_start:
            gradient_start = readme_settings_async(
                "background_management", f"{self._target}_background_color"
            )
        gradient_end = readme_settings_async(
            "background_management", f"{self._target}_background_gradient_end"
        )

        self.gradientStartItem = ColorConfigItem(
            "background_management",
            f"{self._target}_background_gradient_start",
            gradient_start or "#66CCFF",
        )
        self.gradientStartItem.valueChanged.connect(
            lambda color: update_settings(
                "background_management",
                f"{self._target}_background_gradient_start",
                color.name(),
            )
        )
        self.gradientStartItem.valueChanged.connect(
            lambda _color: self._refresh_preview()
        )
        self.gradientStartCard = ColorSettingCard(
            self.gradientStartItem,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr(
                get_content_name_async("theme_management", "background_gradient_start")
            ),
            self.tr(
                get_content_description_async(
                    "theme_management", "background_gradient_start"
                )
            ),
            parent=self,
        )

        self.gradientEndItem = ColorConfigItem(
            "background_management",
            f"{self._target}_background_gradient_end",
            gradient_end or "#ffffff",
        )
        self.gradientEndItem.valueChanged.connect(
            lambda color: update_settings(
                "background_management",
                f"{self._target}_background_gradient_end",
                color.name(),
            )
        )
        self.gradientEndItem.valueChanged.connect(
            lambda _color: self._refresh_preview()
        )
        self.gradientEndCard = ColorSettingCard(
            self.gradientEndItem,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr(
                get_content_name_async("theme_management", "background_gradient_end")
            ),
            self.tr(
                get_content_description_async(
                    "theme_management", "background_gradient_end"
                )
            ),
            parent=self,
        )

        self.gradientDirectionCard = SettingCard(
            get_theme_icon("ic_fluent_arrow_right_20_filled"),
            get_content_name_async("theme_management", "background_gradient_direction"),
            get_content_description_async(
                "theme_management", "background_gradient_direction"
            ),
            parent=self,
        )
        self.gradientDirectionCombo = ComboBox(self.gradientDirectionCard)
        self.gradientDirectionCombo.addItems(
            get_content_combo_name_async(
                "theme_management", "background_gradient_direction"
            )
        )
        gradient_direction = readme_settings_async(
            "background_management", f"{self._target}_background_gradient_direction"
        )
        gradient_direction_v2 = readme_settings_async(
            "background_management",
            f"{self._target}_background_gradient_direction_v2",
        )
        try:
            gradient_direction = (
                int(gradient_direction) if gradient_direction is not None else 0
            )
        except Exception:
            gradient_direction = 0
        if not bool(gradient_direction_v2):
            old_to_new = {0: 0, 1: 2, 2: 4, 3: 6}
            update_settings(
                "background_management",
                f"{self._target}_background_gradient_direction_v2",
                True,
            )
            mapped = old_to_new.get(gradient_direction, gradient_direction)
            if mapped != gradient_direction:
                gradient_direction = mapped
                update_settings(
                    "background_management",
                    f"{self._target}_background_gradient_direction",
                    int(gradient_direction),
                )
        self.gradientDirectionCombo.setCurrentIndex(max(0, min(7, gradient_direction)))
        self.gradientDirectionCombo.currentIndexChanged.connect(
            self._on_gradient_direction_changed
        )
        self.gradientDirectionCard.hBoxLayout.addWidget(
            self.gradientDirectionCombo, 0, Qt.AlignmentFlag.AlignRight
        )
        self.gradientDirectionCard.hBoxLayout.addSpacing(16)

        self.imageCard = SettingCard(
            get_theme_icon("ic_fluent_image_20_filled"),
            get_content_name_async("theme_management", "background_image"),
            get_content_description_async("theme_management", "background_image"),
            parent=self,
        )
        self.imageLineEdit = QLineEdit(self.imageCard)
        self.imageLineEdit.setReadOnly(True)
        self.imageLineEdit.setFixedWidth(260)
        self.imageSelectBtn = PushButton(
            get_content_pushbutton_name_async(
                "theme_management", "select_background_image"
            )
        )
        self.imageClearBtn = PushButton(
            get_content_pushbutton_name_async(
                "theme_management", "clear_background_image"
            )
        )
        self.imageCard.hBoxLayout.addWidget(
            self.imageLineEdit, 0, Qt.AlignmentFlag.AlignRight
        )
        self.imageCard.hBoxLayout.addSpacing(8)
        self.imageCard.hBoxLayout.addWidget(
            self.imageSelectBtn, 0, Qt.AlignmentFlag.AlignRight
        )
        self.imageCard.hBoxLayout.addSpacing(8)
        self.imageCard.hBoxLayout.addWidget(
            self.imageClearBtn, 0, Qt.AlignmentFlag.AlignRight
        )
        self.imageCard.hBoxLayout.addSpacing(16)

        self.imageSelectBtn.clicked.connect(self._select_image)
        self.imageClearBtn.clicked.connect(self._clear_image)

        self.brightnessCard = SettingCard(
            get_theme_icon("ic_fluent_brightness_high_20_filled"),
            get_content_name_async("theme_management", "background_brightness"),
            get_content_description_async("theme_management", "background_brightness"),
            parent=self,
        )
        self.brightnessValueLabel = QLabel(self.brightnessCard)
        self.brightnessSlider = QSlider(Qt.Orientation.Horizontal, self.brightnessCard)
        self.brightnessSlider.setRange(0, 200)
        self.brightnessSlider.setFixedWidth(200)

        brightness = readme_settings_async(
            "background_management", f"{self._target}_background_brightness"
        )
        try:
            brightness = int(brightness) if brightness is not None else 100
        except Exception:
            brightness = 100
        brightness = max(0, min(200, brightness))
        self.brightnessSlider.setValue(brightness)
        self.brightnessValueLabel.setText(f"{brightness}%")

        self.brightnessSlider.valueChanged.connect(self._on_brightness_changed)

        self.blurCard = SettingCard(
            get_theme_icon("ic_fluent_blur_20_filled"),
            get_content_name_async("theme_management", "background_blur"),
            get_content_description_async("theme_management", "background_blur"),
            parent=self,
        )
        self.blurSwitch = SwitchButton(self.blurCard)
        self.blurSwitch.setOffText(
            get_content_switchbutton_name_async(
                "theme_management", "background_blur", "disable"
            )
        )
        self.blurSwitch.setOnText(
            get_content_switchbutton_name_async(
                "theme_management", "background_blur", "enable"
            )
        )

        blur_enable = readme_settings_async(
            "background_management", f"{self._target}_background_blur_enable"
        )
        self.blurSwitch.setChecked(bool(blur_enable))
        self.blurSwitch.checkedChanged.connect(self._on_blur_enable_changed)

        self.blurCard.hBoxLayout.addWidget(
            self.blurSwitch, 0, Qt.AlignmentFlag.AlignRight
        )
        self.blurCard.hBoxLayout.addSpacing(16)

        self.blurRadiusCard = SettingCard(
            get_theme_icon("ic_fluent_blur_20_filled"),
            get_content_name_async("theme_management", "background_blur_radius"),
            get_content_description_async("theme_management", "background_blur_radius"),
            parent=self,
        )
        self.blurRadiusValueLabel = QLabel(self.blurRadiusCard)
        self.blurRadiusSlider = QSlider(Qt.Orientation.Horizontal, self.blurRadiusCard)
        self.blurRadiusSlider.setRange(0, 40)
        self.blurRadiusSlider.setFixedWidth(200)

        blur_radius = readme_settings_async(
            "background_management", f"{self._target}_background_blur_radius"
        )
        try:
            blur_radius = int(blur_radius) if blur_radius is not None else 12
        except Exception:
            blur_radius = 15
        blur_radius = max(0, min(40, blur_radius))
        self.blurRadiusSlider.setValue(blur_radius)
        self.blurRadiusValueLabel.setText(str(blur_radius))

        self.blurRadiusSlider.valueChanged.connect(self._on_blur_radius_changed)

        self.blurRadiusCard.hBoxLayout.addWidget(
            self.blurRadiusValueLabel, 0, Qt.AlignmentFlag.AlignRight
        )
        self.blurRadiusCard.hBoxLayout.addSpacing(10)
        self.blurRadiusCard.hBoxLayout.addWidget(
            self.blurRadiusSlider, 0, Qt.AlignmentFlag.AlignRight
        )
        self.blurRadiusCard.hBoxLayout.addSpacing(16)

        self.brightnessCard.hBoxLayout.addWidget(
            self.brightnessValueLabel, 0, Qt.AlignmentFlag.AlignRight
        )
        self.brightnessCard.hBoxLayout.addSpacing(10)
        self.brightnessCard.hBoxLayout.addWidget(
            self.brightnessSlider, 0, Qt.AlignmentFlag.AlignRight
        )
        self.brightnessCard.hBoxLayout.addSpacing(16)

        self.previewLabel = QLabel()
        self.previewLabel.setMinimumSize(260, 80)
        self.previewLabel.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.previewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previewLabel.setStyleSheet("background: transparent;")

        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self.previewLabel)
        self.addGroup(
            get_theme_icon("ic_fluent_window_20_filled"),
            get_content_name_async("theme_management", "background_preview"),
            get_content_description_async("theme_management", "background_preview"),
            preview_widget,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_paint_brush_20_filled"),
            get_content_name_async("theme_management", "background_mode"),
            get_content_description_async("theme_management", "background_mode"),
            self.modeCombo,
        )
        self.vBoxLayout.addWidget(self.colorCard)
        self.vBoxLayout.addWidget(self.gradientStartCard)
        self.vBoxLayout.addWidget(self.gradientEndCard)
        self.vBoxLayout.addWidget(self.gradientDirectionCard)
        self.vBoxLayout.addWidget(self.imageCard)
        self.vBoxLayout.addWidget(self.blurCard)
        self.vBoxLayout.addWidget(self.blurRadiusCard)
        self.vBoxLayout.addWidget(self.brightnessCard)
        self.previewLabel.installEventFilter(self)

        self._load_image_line_edit()
        self._refresh_enabled_state()
        self._refresh_preview()

    def eventFilter(self, obj, event):
        if (
            obj == getattr(self, "previewLabel", None)
            and event.type() == QEvent.Type.Resize
        ):
            QTimer.singleShot(0, self._refresh_preview)
        return super().eventFilter(obj, event)

    def _on_mode_changed(self, index: int):
        update_settings(
            "background_management", f"{self._target}_background_mode", int(index)
        )
        self._refresh_enabled_state()
        self._refresh_preview()

    def _load_image_line_edit(self):
        path = readme_settings_async(
            "background_management", f"{self._target}_background_image"
        )
        self.imageLineEdit.setText(str(path or ""))

    def _select_image(self):
        exts = " ".join(f"*{e}" for e in SUPPORTED_IMAGE_EXTENSIONS)
        file_filter = f"{get_content_name_async('theme_management', 'image_files')} ({exts});;{get_content_name_async('theme_management', 'all_files')}"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_content_name_async(
                "theme_management", "select_background_image_dialog"
            ),
            "",
            file_filter,
        )
        if not file_path:
            return
        update_settings(
            "background_management", f"{self._target}_background_image", file_path
        )
        self.imageLineEdit.setText(file_path)
        self._refresh_preview()

    def _clear_image(self):
        update_settings("background_management", f"{self._target}_background_image", "")
        self.imageLineEdit.setText("")
        self._refresh_preview()

    def _on_brightness_changed(self, value: int):
        value = int(value)
        self.brightnessValueLabel.setText(f"{value}%")
        update_settings(
            "background_management", f"{self._target}_background_brightness", value
        )
        self._refresh_preview()

    def _on_blur_enable_changed(self, is_checked: bool):
        update_settings(
            "background_management",
            f"{self._target}_background_blur_enable",
            bool(is_checked),
        )
        self._refresh_enabled_state()
        self._refresh_preview()

    def _on_blur_radius_changed(self, value: int):
        value = int(value)
        self.blurRadiusValueLabel.setText(str(value))
        update_settings(
            "background_management",
            f"{self._target}_background_blur_radius",
            value,
        )
        self._refresh_preview()

    def _on_gradient_direction_changed(self, index: int):
        update_settings(
            "background_management",
            f"{self._target}_background_gradient_direction",
            int(index),
        )
        update_settings(
            "background_management",
            f"{self._target}_background_gradient_direction_v2",
            True,
        )
        self._refresh_preview()

    def _refresh_enabled_state(self):
        mode = self.modeCombo.currentIndex()
        self.colorCard.setEnabled(mode == 1 or mode == 2)
        self.gradientStartCard.setEnabled(mode == 3)
        self.gradientEndCard.setEnabled(mode == 3)
        self.gradientDirectionCard.setEnabled(mode == 3)
        self.imageCard.setEnabled(mode == 2)
        self.blurCard.setEnabled(mode == 1 or mode == 2 or mode == 3)
        self.blurRadiusCard.setEnabled(
            (mode == 1 or mode == 2 or mode == 3) and self.blurSwitch.isChecked()
        )
        self.brightnessCard.setEnabled(mode == 2)

    def _render_gradient_preview_pixmap(self) -> QPixmap:
        size = self.previewLabel.size()
        pix = QPixmap(size)
        pix.fill(Qt.GlobalColor.transparent)

        w = size.width()
        h = size.height()
        if w <= 0 or h <= 0:
            return pix

        direction = self.gradientDirectionCombo.currentIndex()
        if direction == 1:
            gradient = QLinearGradient(0, h, 0, 0)
        elif direction == 2:
            gradient = QLinearGradient(0, 0, w, 0)
        elif direction == 3:
            gradient = QLinearGradient(w, 0, 0, 0)
        elif direction == 4:
            gradient = QLinearGradient(0, 0, w, h)
        elif direction == 5:
            gradient = QLinearGradient(w, h, 0, 0)
        elif direction == 6:
            gradient = QLinearGradient(w, 0, 0, h)
        elif direction == 7:
            gradient = QLinearGradient(0, h, w, 0)
        else:
            gradient = QLinearGradient(0, 0, 0, h)

        gradient.setColorAt(0.0, self.gradientStartItem.value)
        gradient.setColorAt(1.0, self.gradientEndItem.value)

        p = QPainter(pix)
        p.fillRect(pix.rect(), gradient)
        p.end()
        return pix

    def _blur_pixmap(self, pix: QPixmap, radius: int) -> QPixmap:
        if pix.isNull():
            return pix
        radius = int(radius)
        if radius <= 0:
            return pix

        src = pix
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(src)
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(radius)
        item.setGraphicsEffect(effect)
        scene.addItem(item)

        img = QImage(src.size(), QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        scene.render(p)
        p.end()
        return QPixmap.fromImage(img)

    def _stop_preview_movie(self):
        movie = getattr(self, "_preview_movie", None)
        if movie is None:
            return
        try:
            movie.frameChanged.disconnect(self._on_preview_movie_frame_changed)
        except Exception:
            pass
        try:
            movie.stop()
        except Exception:
            pass
        self._preview_movie = None

    def _start_preview_movie(self, path: str):
        path = str(path or "")
        if not path:
            self._stop_preview_movie()
            return

        movie = getattr(self, "_preview_movie", None)
        if movie is not None and str(movie.fileName() or "") == path:
            if movie.state() != QMovie.MovieState.Running:
                try:
                    movie.start()
                except Exception:
                    pass
            return

        self._stop_preview_movie()
        movie = QMovie(path)
        movie.setCacheMode(QMovie.CacheMode.CacheNone)
        movie.frameChanged.connect(self._on_preview_movie_frame_changed)
        self._preview_movie = movie
        try:
            movie.start()
        except Exception:
            self._stop_preview_movie()

    def _on_preview_movie_frame_changed(self, _frame: int):
        movie = getattr(self, "_preview_movie", None)
        if movie is None:
            return
        frame = movie.currentPixmap()
        if frame.isNull():
            return
        canvas = self._render_image_preview_canvas(frame)
        self.previewLabel.setPixmap(canvas)
        self.previewLabel.setText("")

    def _render_image_preview_canvas(self, src: QPixmap) -> QPixmap:
        target_size = self.previewLabel.size()
        canvas = QPixmap(target_size)
        canvas.fill(Qt.GlobalColor.transparent)
        p = QPainter(canvas)
        p.fillRect(canvas.rect(), self.colorItem.value)

        tw = target_size.width()
        th = target_size.height()
        pw = src.width()
        ph = src.height()
        if tw > 0 and th > 0 and pw > 0 and ph > 0:
            ratio = max(tw / pw, th / ph)
            sw = int(pw * ratio)
            sh = int(ph * ratio)
            scaled = src.scaled(
                sw,
                sh,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (sw - tw) // 2
            y = (sh - th) // 2
            cropped = scaled.copy(x, y, tw, th)
            p.drawPixmap(0, 0, cropped)
        p.end()

        value = self.brightnessSlider.value()
        if value != 100:
            overlay = QPixmap(canvas.size())
            overlay.fill(Qt.GlobalColor.transparent)
            p = QPainter(overlay)
            p.drawPixmap(0, 0, canvas)
            if value > 100:
                alpha = int((value - 100) / 100 * 180)
                alpha = max(0, min(180, alpha))
                p.fillRect(overlay.rect(), QColor(255, 255, 255, alpha))
            else:
                alpha = int((100 - value) / 100 * 180)
                alpha = max(0, min(180, alpha))
                p.fillRect(overlay.rect(), QColor(0, 0, 0, alpha))
            p.end()
            canvas = overlay

        if self.blurSwitch.isChecked() and self.blurRadiusSlider.value() > 0:
            canvas = self._blur_pixmap(canvas, self.blurRadiusSlider.value())

        return canvas

    def _refresh_preview(self):
        mode = self.modeCombo.currentIndex()
        if mode == 0:
            self._stop_preview_movie()
            self.previewLabel.setPixmap(QPixmap())
            self.previewLabel.setText(
                get_content_name_async("theme_management", "preview_default")
            )
            return

        if mode == 1:
            self._stop_preview_movie()
            pix = QPixmap(self.previewLabel.size())
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.fillRect(pix.rect(), self.colorItem.value)
            p.end()
            if self.blurSwitch.isChecked() and self.blurRadiusSlider.value() > 0:
                pix = self._blur_pixmap(pix, self.blurRadiusSlider.value())
            self.previewLabel.setPixmap(pix)
            self.previewLabel.setText("")
            return

        if mode == 3:
            self._stop_preview_movie()
            pix = self._render_gradient_preview_pixmap()
            if self.blurSwitch.isChecked() and self.blurRadiusSlider.value() > 0:
                pix = self._blur_pixmap(pix, self.blurRadiusSlider.value())
            self.previewLabel.setPixmap(pix)
            self.previewLabel.setText("")
            return

        path = readme_settings_async(
            "background_management", f"{self._target}_background_image"
        )
        path = str(path or "")
        if not path or not os.path.exists(path):
            self._stop_preview_movie()
            self.previewLabel.setPixmap(QPixmap())
            self.previewLabel.setText(
                get_content_name_async("theme_management", "preview_no_image")
            )
            return

        if path.lower().endswith(".gif"):
            self._start_preview_movie(path)
            movie = getattr(self, "_preview_movie", None)
            if movie is not None:
                try:
                    if movie.jumpToFrame(0):
                        self._on_preview_movie_frame_changed(0)
                        return
                except Exception:
                    pass
            self._stop_preview_movie()

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._stop_preview_movie()
            self.previewLabel.setPixmap(QPixmap())
            self.previewLabel.setText(
                get_content_name_async("theme_management", "preview_load_failed")
            )
            return

        self._stop_preview_movie()
        canvas = self._render_image_preview_canvas(pixmap)
        self.previewLabel.setPixmap(canvas)
        self.previewLabel.setText("")
