from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QPixmap
from qfluentwidgets import (
    PrimaryPushButton,
    PushButton,
    DropDownPushButton,
    BodyLabel,
    CaptionLabel,
    ImageLabel,
    CardWidget,
    RoundMenu,
    Action,
)
from app.tools.personalised import get_theme_icon
from app.Language.obtain_language import get_content_name_async


class ThemeCard(CardWidget):
    installSignal = Signal(str)
    uninstallSignal = Signal(str)
    updateSignal = Signal(str)
    applySignal = Signal(str, str)

    def __init__(self, theme_info: dict, parent=None):
        super().__init__(parent)
        self.theme_info = theme_info
        self.theme_id = theme_info.get("id", "unknown")

        self.setFixedSize(320, 290)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # 预览图
        self.imageLabel = ImageLabel(self)
        self.imageLabel.setBorderRadius(8, 8, 0, 0)
        self.imageLabel.setScaledContents(False)
        preview_path = theme_info.get("preview_path", "")
        if preview_path:
            self.set_preview_image(preview_path)
        self.imageLabel.setFixedSize(320, 180)

        # 信息区域
        self.infoWidget = QWidget(self)
        self.infoLayout = QHBoxLayout(self.infoWidget)
        self.infoLayout.setContentsMargins(12, 12, 12, 12)

        self.textLayout = QVBoxLayout()
        self.textLayout.setSpacing(2)

        self.nameLabel = BodyLabel(theme_info.get("name", "Unknown"), self)
        self.nameLabel.setWordWrap(True)

        self.descLabel = CaptionLabel(theme_info.get("description", ""), self)
        self.descLabel.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
        self.descLabel.setWordWrap(True)

        last_updated = get_content_name_async("theme_management", "last_updated")
        self.updateLabel = CaptionLabel(
            f"{last_updated}:\n{theme_info.get('last_updated', '-')}", self
        )
        self.updateLabel.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
        self.updateLabel.setWordWrap(True)

        latest_ver = get_content_name_async("theme_management", "latest_version")
        self.versionLabel = CaptionLabel(
            f"{latest_ver}: {theme_info.get('latest_version', '-')}", self
        )
        self.versionLabel.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
        self.versionLabel.setWordWrap(True)

        self.textLayout.addWidget(self.nameLabel)
        self.textLayout.addWidget(self.descLabel)
        self.textLayout.addWidget(self.updateLabel)
        self.textLayout.addWidget(self.versionLabel)

        if theme_info.get("is_installed"):
            current_ver = get_content_name_async("theme_management", "current_version")
            self.installedVersionLabel = CaptionLabel(
                f"{current_ver}: {theme_info.get('current_version', '-')}", self
            )
            self.installedVersionLabel.setTextColor(
                Qt.GlobalColor.gray, Qt.GlobalColor.gray
            )
            self.installedVersionLabel.setWordWrap(True)
            self.textLayout.addWidget(self.installedVersionLabel)

        self.textLayout.addStretch(1)

        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setSpacing(6)
        self.buttonLayout.addStretch(1)

        if theme_info.get("is_installed"):
            if theme_info.get("update_available"):
                self.updateButton = PushButton(self)
                self.updateButton.setFixedWidth(120)
                self.updateButton.setIcon(
                    get_theme_icon("ic_fluent_arrow_sync_20_filled")
                )
                self.updateButton.setText(
                    get_content_name_async("theme_management", "update")
                )
                self.updateButton.clicked.connect(self._on_update)
                self.buttonLayout.addWidget(self.updateButton)

            self.uninstallButton = PushButton(self)
            self.uninstallButton.setFixedWidth(120)
            self.uninstallButton.setIcon(get_theme_icon("ic_fluent_delete_20_filled"))
            self.uninstallButton.setText(
                get_content_name_async("theme_management", "uninstall")
            )
            self.uninstallButton.clicked.connect(self._on_uninstall)
            self.buttonLayout.addWidget(self.uninstallButton)

            self.applyButton = DropDownPushButton(self)
            self.applyButton.setFixedWidth(120)
            if theme_info.get("is_any_active"):
                self.applyButton.setText(
                    get_content_name_async("theme_management", "in_use")
                )
            else:
                self.applyButton.setText(
                    get_content_name_async("theme_management", "apply")
                )

            menu = RoundMenu(parent=self.applyButton)
            menu_actions = []

            if theme_info.get("can_apply_roll_call"):
                if theme_info.get("can_apply_roll_call_py"):
                    if theme_info.get("is_active_roll_call_py"):
                        text = get_content_name_async(
                            "theme_management", "cancel_roll_call_py"
                        )
                        action_key = "cancel_roll_call_py"
                    else:
                        text = get_content_name_async(
                            "theme_management", "apply_roll_call_py"
                        )
                        action_key = "apply_roll_call_py"
                    menu_actions.append((text, action_key))

                if theme_info.get("can_apply_roll_call_html"):
                    if theme_info.get("is_active_roll_call_html"):
                        text = get_content_name_async(
                            "theme_management", "cancel_roll_call_html"
                        )
                        action_key = "cancel_roll_call_html"
                    else:
                        text = get_content_name_async(
                            "theme_management", "apply_roll_call_html"
                        )
                        action_key = "apply_roll_call_html"
                    menu_actions.append((text, action_key))

            if theme_info.get("can_apply_lottery"):
                if theme_info.get("can_apply_lottery_py"):
                    if theme_info.get("is_active_lottery_py"):
                        text = get_content_name_async(
                            "theme_management", "cancel_lottery_py"
                        )
                        action_key = "cancel_lottery_py"
                    else:
                        text = get_content_name_async(
                            "theme_management", "apply_lottery_py"
                        )
                        action_key = "apply_lottery_py"
                    menu_actions.append((text, action_key))

                if theme_info.get("can_apply_lottery_html"):
                    if theme_info.get("is_active_lottery_html"):
                        text = get_content_name_async(
                            "theme_management", "cancel_lottery_html"
                        )
                        action_key = "cancel_lottery_html"
                    else:
                        text = get_content_name_async(
                            "theme_management", "apply_lottery_html"
                        )
                        action_key = "apply_lottery_html"
                    menu_actions.append((text, action_key))

            for text, action_key in menu_actions:
                action = Action(
                    get_theme_icon("ic_fluent_checkmark_20_filled"),
                    text,
                    triggered=lambda checked=False, a=action_key: self._on_apply(a),
                )
                menu.addAction(action)

            if menu_actions:
                self.applyButton.setMenu(menu)
            else:
                self.applyButton.setEnabled(False)

            self.buttonLayout.addWidget(self.applyButton)
        else:
            self.installButton = PrimaryPushButton(self)
            self.installButton.setFixedWidth(120)
            self.installButton.setIcon(
                get_theme_icon("ic_fluent_arrow_download_20_filled")
            )
            self.installButton.setText(
                get_content_name_async("theme_management", "install")
            )
            self.installButton.clicked.connect(self._on_install)
            self.buttonLayout.addWidget(self.installButton)

        self.infoLayout.addLayout(self.textLayout)
        self.infoLayout.addStretch(1)
        self.infoLayout.addLayout(self.buttonLayout)

        self.vBoxLayout.addWidget(self.imageLabel)
        self.vBoxLayout.addWidget(self.infoWidget)

    def set_preview_image(self, image_path: str):
        if not image_path:
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
        self.set_preview_pixmap(pixmap)

    def set_preview_pixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            return

        # 目标尺寸
        target_w, target_h = 320, 180

        # 计算缩放比例 (Cover模式)
        if pixmap.width() == 0 or pixmap.height() == 0:
            return

        ratio_w = target_w / pixmap.width()
        ratio_h = target_h / pixmap.height()
        ratio = max(ratio_w, ratio_h)

        # 缩放
        scaled_w = int(pixmap.width() * ratio)
        scaled_h = int(pixmap.height() * ratio)
        scaled_pixmap = pixmap.scaled(
            scaled_w,
            scaled_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # 居中裁切
        x = (scaled_w - target_w) // 2
        y = (scaled_h - target_h) // 2
        cropped_pixmap = scaled_pixmap.copy(x, y, target_w, target_h)

        self.imageLabel.setImage(cropped_pixmap)

    def _on_install(self):
        self.installSignal.emit(self.theme_id)

    def _on_uninstall(self):
        self.uninstallSignal.emit(self.theme_id)

    def _on_apply(self, action_key):
        self.applySignal.emit(self.theme_id, action_key)

    def _on_update(self):
        self.updateSignal.emit(self.theme_id)
