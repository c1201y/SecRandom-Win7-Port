from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.personalised import get_theme_icon
from app.tools.language_manager import get_all_languages_name
from app.tools.path_utils import get_data_path
from app.view.settings.list_management.list_management import roll_call_list
from app.view.settings.basic_settings import basic_settings_function
from app.view.settings.voice_settings.basic_voice_settings import (
    basic_settings_voice_engine,
    basic_settings_volume,
)
from app.view.settings.more_settings.music_settings import (
    music_management,
    music_settings_table,
)
from app.view.settings.linkage_settings import (
    class_break_settings,
    cses_import_settings,
    data_source_settings,
)
from app.common.voice.voice import TTSHandler
from app.common.IPC_URL.csharp_ipc_handler import CSharpIPCHandler
from app.common.music.music_player import get_music_files, music_player
from app.common.notification.notification_service import FloatingNotificationManager
from app.tools.variable import GITHUB_WEB, BILIBILI_WEB, WEBSITE


from app.tools.config import import_all_data


class roll_call_classisland_notification_service_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "roll_call_notification_settings",
                "classisland_notification_service_settings",
            )
        )
        self.setBorderRadius(8)

        self.notification_service_type_combo_box = ComboBox()
        self.notification_service_type_combo_box.addItems(
            get_content_combo_name_async(
                "roll_call_notification_settings", "notification_service_type"
            )
        )
        self.notification_service_type_combo_box.setCurrentIndex(
            readme_settings_async(
                "roll_call_notification_settings", "notification_service_type"
            )
        )
        self.notification_service_type_combo_box.currentIndexChanged.connect(
            self._on_notification_service_type_changed
        )

        self.notification_display_duration_spinbox = SpinBox()
        self.notification_display_duration_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.notification_display_duration_spinbox.setRange(1, 60)
        self.notification_display_duration_spinbox.setSuffix("s")
        self.notification_display_duration_spinbox.setValue(
            readme_settings_async(
                "roll_call_notification_settings", "notification_display_duration"
            )
        )
        self.notification_display_duration_spinbox.valueChanged.connect(
            lambda: update_settings(
                "roll_call_notification_settings",
                "notification_display_duration",
                self.notification_display_duration_spinbox.value(),
            )
        )

        self.addGroup(
            get_theme_icon("ic_fluent_cloud_20_filled"),
            get_content_name_async(
                "roll_call_notification_settings", "notification_service_type"
            ),
            get_content_description_async(
                "roll_call_notification_settings", "notification_service_type"
            ),
            self.notification_service_type_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async(
                "roll_call_notification_settings", "notification_display_duration"
            ),
            get_content_description_async(
                "roll_call_notification_settings", "notification_display_duration"
            ),
            self.notification_display_duration_spinbox,
        )

    def _on_notification_service_type_changed(self, index):
        update_settings(
            "roll_call_notification_settings",
            "notification_service_type",
            index,
        )
        if index == 1 or index == 2:
            hint_title = get_any_position_value_async(
                "roll_call_notification_settings",
                "classisland_notification_hint",
                "title",
            )
            hint_content = get_any_position_value_async(
                "roll_call_notification_settings",
                "classisland_notification_hint",
                "content",
            )
            InfoBar.success(
                title=hint_title,
                content=hint_content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )


class quick_draw_classisland_notification_service_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "quick_draw_notification_settings",
                "classisland_notification_service_settings",
            )
        )
        self.setBorderRadius(8)

        self.notification_service_type_combo_box = ComboBox()
        self.notification_service_type_combo_box.addItems(
            get_content_combo_name_async(
                "quick_draw_notification_settings", "notification_service_type"
            )
        )
        self.notification_service_type_combo_box.setCurrentIndex(
            readme_settings_async(
                "quick_draw_notification_settings", "notification_service_type"
            )
        )
        self.notification_service_type_combo_box.currentIndexChanged.connect(
            self._on_notification_service_type_changed
        )

        self.notification_display_duration_spinbox = SpinBox()
        self.notification_display_duration_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.notification_display_duration_spinbox.setRange(1, 60)
        self.notification_display_duration_spinbox.setSuffix("s")
        self.notification_display_duration_spinbox.setValue(
            readme_settings_async(
                "quick_draw_notification_settings", "notification_display_duration"
            )
        )
        self.notification_display_duration_spinbox.valueChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "notification_display_duration",
                self.notification_display_duration_spinbox.value(),
            )
        )

        self.addGroup(
            get_theme_icon("ic_fluent_cloud_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "notification_service_type"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "notification_service_type"
            ),
            self.notification_service_type_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "notification_display_duration"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "notification_display_duration"
            ),
            self.notification_display_duration_spinbox,
        )

    def _on_notification_service_type_changed(self, index):
        update_settings(
            "quick_draw_notification_settings",
            "notification_service_type",
            index,
        )
        if index == 1 or index == 2:
            hint_title = get_any_position_value_async(
                "quick_draw_notification_settings",
                "classisland_notification_hint",
                "title",
            )
            hint_content = get_any_position_value_async(
                "quick_draw_notification_settings",
                "classisland_notification_hint",
                "content",
            )
            InfoBar.success(
                title=hint_title,
                content=hint_content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )


class WelcomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(16)

        self.logoLabel = QLabel(self)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(str(get_data_path("assets/icon", "secrandom-icon-paper.png")))
        if not pixmap.isNull():
            self.logoLabel.setPixmap(
                pixmap.scaled(
                    108,
                    108,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "welcome_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "welcome_page", "subtitle")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.startBtn = PrimaryPushButton(
            get_any_position_value_async("guide", "welcome_page", "start_btn"),
            self,
        )
        self.startBtn.setFixedWidth(160)
        self.startBtn.clicked.connect(self._on_start)

        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.logoLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addSpacing(6)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addSpacing(18)
        self.vBoxLayout.addWidget(self.startBtn, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)

    def _on_start(self):
        try:
            self.window().next_page()
        except Exception:
            pass


class LanguagePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(30)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "language_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "language_page", "subtitle")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 语言选择
        self.langCard = SettingCard(
            get_theme_icon("ic_fluent_local_language_20_filled"),
            get_any_position_value_async("guide", "language_page", "language"),
            get_any_position_value_async("guide", "language_page", "restart_hint"),
            parent=self,
        )

        self.langCombo = ComboBox(self.langCard)
        self.langCard.hBoxLayout.addWidget(
            self.langCombo, 0, Qt.AlignmentFlag.AlignRight
        )
        self.langCard.hBoxLayout.addSpacing(16)

        # 获取可用语言
        self.available_langs = get_all_languages_name()
        self.langCombo.addItems(self.available_langs)

        # 设置当前语言
        current_lang = readme_settings_async("basic_settings", "language")
        self.initial_lang = current_lang if current_lang in self.available_langs else ""
        if current_lang in self.available_langs:
            self.langCombo.setCurrentText(current_lang)
        elif self.available_langs:
            self.langCombo.setCurrentIndex(0)
            self.initial_lang = self.langCombo.currentText()

        self.langCombo.currentIndexChanged.connect(self._on_lang_changed)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.langCard)
        self.vBoxLayout.addStretch(1)

    def _on_lang_changed(self, index):
        new_lang = self.langCombo.currentText()
        if new_lang != self.initial_lang:
            w = MessageBox(
                get_any_position_value_async(
                    "guide", "language_page", "restart_dialog_title"
                ),
                get_any_position_value_async(
                    "guide", "language_page", "restart_dialog_content"
                ),
                self.window(),
            )
            w.yesButton.setText(
                get_any_position_value_async("guide", "language_page", "restart_btn")
            )
            w.cancelButton.setText(
                get_any_position_value_async("guide", "language_page", "cancel_btn")
            )
            if w.exec():
                update_settings("basic_settings", "language", new_lang)
                QApplication.exit(EXIT_CODE_RESTART)
            else:
                # 恢复原来的选择
                self.langCombo.setCurrentText(self.initial_lang)


class LicensePage(QWidget):
    licenseAccepted = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "license_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "license_page", "subtitle")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 切换许可/免责
        self.segmentWidget = SegmentedWidget(self)
        self.segmentWidget.addItem(
            "license",
            get_any_position_value_async("guide", "license_page", "tab_license"),
        )
        self.segmentWidget.addItem(
            "disclaimer",
            get_any_position_value_async("guide", "license_page", "tab_disclaimer"),
        )
        self.segmentWidget.setCurrentItem("license")
        self.segmentWidget.currentItemChanged.connect(self._on_tab_changed)

        self.stackedWidget = QStackedWidget(self)

        # GPL License Text
        self.licenseText = TextEdit()
        self.licenseText.setMarkdown(
            get_any_position_value_async("guide", "license_page", "license_content")
        )
        self.licenseText.setReadOnly(True)

        # Disclaimer Text
        self.disclaimerText = TextEdit()
        self.disclaimerText.setMarkdown(
            get_any_position_value_async("guide", "license_page", "disclaimer_content")
        )
        self.disclaimerText.setReadOnly(True)

        self.stackedWidget.addWidget(self.licenseText)
        self.stackedWidget.addWidget(self.disclaimerText)

        self._license_scrolled_to_bottom = False
        self._disclaimer_scrolled_to_bottom = False
        self._license_scroll_range_initialized = False
        self._disclaimer_scroll_range_initialized = False

        self.agreeLicenseCheckBox = CheckBox(
            get_any_position_value_async(
                "guide", "license_page", "agree_license_checkbox"
            )
        )
        self.agreeDisclaimerCheckBox = CheckBox(
            get_any_position_value_async(
                "guide", "license_page", "agree_disclaimer_checkbox"
            )
        )
        self.agreeLicenseCheckBox.setEnabled(False)
        self.agreeDisclaimerCheckBox.setEnabled(False)
        self.agreeLicenseCheckBox.stateChanged.connect(self._on_agree_changed)
        self.agreeDisclaimerCheckBox.stateChanged.connect(self._on_agree_changed)

        self.licenseText.verticalScrollBar().valueChanged.connect(
            self._on_license_scroll_changed
        )
        self.disclaimerText.verticalScrollBar().valueChanged.connect(
            self._on_disclaimer_scroll_changed
        )
        self.licenseText.verticalScrollBar().rangeChanged.connect(
            self._on_license_scroll_range_changed
        )
        self.disclaimerText.verticalScrollBar().rangeChanged.connect(
            self._on_disclaimer_scroll_range_changed
        )

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.segmentWidget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.agreeRow = QWidget(self)
        self.agreeRowLayout = QHBoxLayout(self.agreeRow)
        self.agreeRowLayout.setContentsMargins(0, 0, 0, 0)
        self.agreeRowLayout.setSpacing(16)
        self.agreeRowLayout.addStretch(1)
        self.agreeRowLayout.addWidget(self.agreeLicenseCheckBox)
        self.agreeRowLayout.addWidget(self.agreeDisclaimerCheckBox)
        self.agreeRowLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.agreeRow)

    def _on_tab_changed(self, key):
        if key == "license":
            self.stackedWidget.setCurrentWidget(self.licenseText)
        else:
            self.stackedWidget.setCurrentWidget(self.disclaimerText)

    def _scrollbar_at_bottom(self, scroll_bar: QScrollBar) -> bool:
        maximum = scroll_bar.maximum()
        return scroll_bar.value() >= max(0, maximum - 1)

    def _on_license_scroll_range_changed(self, _min: int, _max: int):
        self._license_scroll_range_initialized = True
        if self._license_scrolled_to_bottom:
            return
        if _max <= 0:
            QTimer.singleShot(0, self._check_license_no_scroll_unlock)

    def _on_disclaimer_scroll_range_changed(self, _min: int, _max: int):
        self._disclaimer_scroll_range_initialized = True
        if self._disclaimer_scrolled_to_bottom:
            return
        if _max <= 0:
            QTimer.singleShot(0, self._check_disclaimer_no_scroll_unlock)

    def _check_license_no_scroll_unlock(self):
        if self._license_scrolled_to_bottom:
            return
        if self.licenseText.verticalScrollBar().maximum() <= 0:
            self._license_scrolled_to_bottom = True
            self.agreeLicenseCheckBox.setEnabled(True)
            self._emit_accept_state()

    def _check_disclaimer_no_scroll_unlock(self):
        if self._disclaimer_scrolled_to_bottom:
            return
        if self.disclaimerText.verticalScrollBar().maximum() <= 0:
            self._disclaimer_scrolled_to_bottom = True
            self.agreeDisclaimerCheckBox.setEnabled(True)
            self._emit_accept_state()

    def _on_license_scroll_changed(self, _value: int):
        if not self._license_scroll_range_initialized:
            return
        if self._license_scrolled_to_bottom:
            return
        if self._scrollbar_at_bottom(self.licenseText.verticalScrollBar()):
            self._license_scrolled_to_bottom = True
            self.agreeLicenseCheckBox.setEnabled(True)
            self._emit_accept_state()

    def _on_disclaimer_scroll_changed(self, _value: int):
        if not self._disclaimer_scroll_range_initialized:
            return
        if self._disclaimer_scrolled_to_bottom:
            return
        if self._scrollbar_at_bottom(self.disclaimerText.verticalScrollBar()):
            self._disclaimer_scrolled_to_bottom = True
            self.agreeDisclaimerCheckBox.setEnabled(True)
            self._emit_accept_state()

    def _on_agree_changed(self, _state):
        self._emit_accept_state()

    def is_accepted(self) -> bool:
        return (
            self.agreeLicenseCheckBox.isChecked()
            and self.agreeDisclaimerCheckBox.isChecked()
        )

    def _emit_accept_state(self):
        self.licenseAccepted.emit(self.is_accepted())


class MigrationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "license_page", "migration_title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "license_page", "migration_desc")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitleLabel.setFixedWidth(620)

        self.importBtn = PrimaryPushButton(
            get_any_position_value_async("guide", "license_page", "manual_import")
        )
        self.importBtn.setFixedWidth(200)
        self.importBtn.clicked.connect(self._manual_import)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.importBtn, 0, Qt.AlignmentFlag.AlignCenter)

    def _manual_import(self):
        def _on_import_success():
            try:
                w = self.window()
                try:
                    w._prev_override_index = w.pages.index(w.migrationPage)
                except Exception:
                    pass
                last_index = len(w.pages) - 1
                w._start_page_transition(last_index)
            except Exception:
                return

        ok = import_all_data(self, on_success=_on_import_success)
        if not ok:
            return


class BasicSettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "basic_settings_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "basic_settings_page", "subtitle")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scrollArea = SingleDirectionScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.scrollWidget.setStyleSheet(
            "QWidget#scrollWidget { background: transparent; }"
        )

        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(20, 0, 20, 20)
        self.scrollLayout.setSpacing(12)

        self.basicFunctionSettings = basic_settings_function(self.scrollWidget)
        self.themeSettings = GuideThemeSettings(self.scrollWidget)

        self.scrollLayout.addWidget(self.basicFunctionSettings)
        self.scrollLayout.addWidget(self.themeSettings)
        self.scrollLayout.addStretch(1)

        self.scrollArea.setWidget(self.scrollWidget)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.scrollArea)


class GuideThemeSettings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("basic_settings", "personalised"))
        self.setBorderRadius(8)

        current_theme = readme_settings_async("basic_settings", "theme")
        if not current_theme:
            legacy_theme = readme_settings_async("basic_settings", "theme_mode")
            legacy_map = {"Light": "LIGHT", "Dark": "DARK", "Auto": "AUTO"}
            if legacy_theme in legacy_map:
                current_theme = legacy_map[legacy_theme]
                update_settings("basic_settings", "theme", current_theme)

        self.theme = ComboBox()
        self.theme.addItems(get_content_combo_name_async("basic_settings", "theme"))
        theme_to_index = {"LIGHT": 0, "DARK": 1, "AUTO": 2}
        index_to_theme = {0: Theme.LIGHT, 1: Theme.DARK, 2: Theme.AUTO}

        current_index = theme_to_index.get(current_theme, 2)
        self.theme.setCurrentIndex(current_index)
        try:
            setTheme(index_to_theme.get(current_index))
        except Exception:
            pass

        def on_theme_changed(index: int):
            update_settings("basic_settings", "theme", ["LIGHT", "DARK", "AUTO"][index])
            setTheme(index_to_theme.get(index))

        self.theme.currentIndexChanged.connect(on_theme_changed)

        self.themeColor = ColorConfigItem(
            "basic_settings",
            "theme_color",
            readme_settings_async("basic_settings", "theme_color"),
        )
        self.themeColor.valueChanged.connect(
            lambda color: update_settings("basic_settings", "theme_color", color.name())
        )
        self.themeColor.valueChanged.connect(lambda color: setThemeColor(color))

        try:
            theme_color_value = readme_settings_async("basic_settings", "theme_color")
            if isinstance(theme_color_value, QColor):
                if theme_color_value.isValid():
                    setThemeColor(theme_color_value)
            elif isinstance(theme_color_value, str):
                qc = QColor(theme_color_value)
                if qc.isValid():
                    setThemeColor(qc)
        except Exception:
            pass

        self.themeColorCard = ColorSettingCard(
            self.themeColor,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr(get_content_name_async("basic_settings", "theme_color")),
            self.tr(get_content_description_async("basic_settings", "theme_color")),
        )

        self.addGroup(
            get_theme_icon("ic_fluent_dark_theme_20_filled"),
            get_content_name_async("basic_settings", "theme"),
            get_content_description_async("basic_settings", "theme"),
            self.theme,
        )

        self.vBoxLayout.addWidget(self.themeColorCard)


class ThemePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "theme_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "theme_page", "subtitle")
        )

        # Theme selection
        self.themeGroup = QButtonGroup(self)
        self.lightBtn = RadioButton(
            get_any_position_value_async("guide", "theme_page", "light_mode")
        )
        self.darkBtn = RadioButton(
            get_any_position_value_async("guide", "theme_page", "dark_mode")
        )
        self.autoBtn = RadioButton(
            get_any_position_value_async("guide", "theme_page", "follow_system")
        )

        self.themeGroup.addButton(self.lightBtn, 0)
        self.themeGroup.addButton(self.darkBtn, 1)
        self.themeGroup.addButton(self.autoBtn, 2)

        # Set current theme
        current_theme = readme_settings_async("basic_settings", "theme_mode")
        if current_theme == "Light":
            self.lightBtn.setChecked(True)
        elif current_theme == "Dark":
            self.darkBtn.setChecked(True)
        else:
            self.autoBtn.setChecked(True)

        self.themeGroup.idToggled.connect(self._on_theme_changed)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.lightBtn, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.darkBtn, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.autoBtn, 0, Qt.AlignmentFlag.AlignCenter)

    def _on_theme_changed(self, id, checked):
        if not checked:
            return
        theme_map = {0: "Light", 1: "Dark", 2: "Auto"}
        update_settings("basic_settings", "theme_mode", theme_map[id])
        # Apply theme immediately (simplified)
        from qfluentwidgets import setTheme, Theme

        if id == 0:
            setTheme(Theme.LIGHT)
        elif id == 1:
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.AUTO)


class ListPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "list_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "list_page", "subtitle")
        )

        # Use the reusable roll_call_list widget
        self.rollCallList = roll_call_list(self)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.rollCallList)


class EnhancedPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.headerLayout = QVBoxLayout()
        self.headerLayout.setContentsMargins(20, 20, 20, 10)
        self.headerLayout.setSpacing(10)
        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "enhanced_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "enhanced_page", "subtitle")
        )
        self.headerLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.headerLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addLayout(self.headerLayout)

        # Scroll Area for settings
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(20, 0, 20, 20)
        self.scrollLayout.setSpacing(12)

        self.segmentWidget = SegmentedWidget(self)
        self.segmentWidget.addItem(
            "tts",
            get_any_position_value_async("guide", "enhanced_page", "tts_settings"),
        )
        self.segmentWidget.addItem(
            "music",
            get_any_position_value_async("guide", "enhanced_page", "music_settings"),
        )
        self.segmentWidget.addItem(
            "linkage",
            get_any_position_value_async("guide", "enhanced_page", "classisland"),
        )
        self.scrollLayout.addWidget(self.segmentWidget)

        self.stackedWidget = QStackedWidget(self)
        self.scrollLayout.addWidget(self.stackedWidget)

        self.ttsPage = QWidget()
        self.ttsLayout = QVBoxLayout(self.ttsPage)
        self.ttsLayout.setContentsMargins(0, 0, 0, 0)
        self.ttsLayout.setSpacing(12)
        self.voiceEngine = basic_settings_voice_engine(self.ttsPage)
        self.voiceVolume = basic_settings_volume(self.ttsPage)
        self.ttsLayout.addWidget(self.voiceEngine)
        self.ttsLayout.addWidget(self.voiceVolume)
        self.ttsLayout.addStretch(1)

        self.musicPage = QWidget()
        self.musicLayout = QVBoxLayout(self.musicPage)
        self.musicLayout.setContentsMargins(0, 0, 0, 0)
        self.musicLayout.setSpacing(12)
        self.musicManagement = music_management(self.musicPage)
        self.musicTable = music_settings_table(self.musicPage)
        self.musicPage.music_settings_table_widget = self.musicTable
        self.musicLayout.addWidget(self.musicManagement)
        self.musicLayout.addWidget(self.musicTable)
        self.musicLayout.addStretch(1)

        self.linkagePage = QWidget()
        self.linkageLayout = QVBoxLayout(self.linkagePage)
        self.linkageLayout.setContentsMargins(0, 0, 0, 0)
        self.linkageLayout.setSpacing(12)

        self.ciSettingsContainer = QWidget()
        self.ciLayout = QVBoxLayout(self.ciSettingsContainer)
        self.ciLayout.setContentsMargins(0, 0, 0, 0)
        self.ciLayout.setSpacing(12)

        self.ciDataSource = data_source_settings(self.ciSettingsContainer)
        self.ciCsesImport = cses_import_settings(self.ciSettingsContainer)
        self.ciRollCallNotification = (
            roll_call_classisland_notification_service_settings(
                self.ciSettingsContainer
            )
        )
        self.ciQuickDrawNotification = (
            quick_draw_classisland_notification_service_settings(
                self.ciSettingsContainer
            )
        )
        self.ciBreak = class_break_settings(self.ciSettingsContainer)

        self.ciLayout.addWidget(self.ciDataSource)
        self.ciLayout.addWidget(self.ciCsesImport)
        self.ciLayout.addWidget(self.ciRollCallNotification)
        self.ciLayout.addWidget(self.ciQuickDrawNotification)
        self.ciLayout.addWidget(self.ciBreak)

        self.linkageLayout.addWidget(self.ciSettingsContainer)
        self.linkageLayout.addStretch(1)

        self.stackedWidget.addWidget(self.ttsPage)
        self.stackedWidget.addWidget(self.musicPage)
        self.stackedWidget.addWidget(self.linkagePage)
        self.segmentWidget.currentItemChanged.connect(self._on_segment_changed)
        self.segmentWidget.setCurrentItem("tts")

        self.scrollArea.setWidget(self.scrollContent)
        self.vBoxLayout.addWidget(self.scrollArea)

    def _on_segment_changed(self, key):
        if key == "tts":
            self.stackedWidget.setCurrentWidget(self.ttsPage)
        elif key == "music":
            self.stackedWidget.setCurrentWidget(self.musicPage)
        else:
            self.stackedWidget.setCurrentWidget(self.linkagePage)


class TestPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "test_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "test_page", "subtitle")
        )

        self.statusLabel = BodyLabel("")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.startBtn = PrimaryPushButton(
            get_any_position_value_async("guide", "test_page", "start_test")
        )
        self.startBtn.setFixedWidth(200)
        self.startBtn.clicked.connect(self.run_test)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.startBtn, 0, Qt.AlignmentFlag.AlignCenter)

        self.tts_handler = TTSHandler()
        self._notification_manager = FloatingNotificationManager()
        self._tests = []
        self._current_test_key = None
        self._has_failure = False
        self._failure_message = ""

    def _get_float_notification_settings(self) -> dict:
        return {
            "font_size": 50,
            "animation_color_theme": 0,
            "display_format": 0,
            "student_image": False,
            "show_random": 0,
            "animation": True,
            "transparency": 0.8,
            "auto_close_time": 5,
            "enabled_monitor": "OFF",
            "window_position": 0,
            "horizontal_offset": 0,
            "vertical_offset": 0,
            "notification_display_duration": 5,
        }

    def _push_float_notification(self, text: str) -> None:
        try:
            title = get_any_position_value_async("guide", "test_page", "title")
            selected_students = [(0, str(text), True)]
            settings = self._get_float_notification_settings()
            self._notification_manager._show_secrandom_notification(
                title,
                selected_students,
                draw_count=1,
                settings=settings,
                settings_group="roll_call_notification_settings",
                is_animating=False,
            )
        except Exception:
            pass

    def run_test(self):
        self.startBtn.setEnabled(False)
        self._has_failure = False
        self._tests = self._build_tests()
        if not self._tests:
            self.statusLabel.setText(
                get_any_position_value_async("guide", "test_page", "success")
            )
            self.startBtn.setEnabled(True)
            return

        self._run_next_test()

    def _test_tts(self):
        self._set_testing_status("test_tts")
        try:
            voice_settings = {
                "voice_volume": readme_settings_async(
                    "basic_voice_settings", "volume_size"
                ),
                "voice_speed": readme_settings_async(
                    "basic_voice_settings", "speech_rate"
                ),
                "system_voice_name": readme_settings_async(
                    "basic_voice_settings", "system_voice_name"
                ),
            }
            voice_engine = readme_settings_async("basic_voice_settings", "voice_engine")
            engine_type = 1 if voice_engine == "Edge TTS" else 0
            edge_tts_voice_name = readme_settings_async(
                "basic_voice_settings", "edge_tts_voice_name"
            )
            self.tts_handler.voice_play(
                config=voice_settings,
                student_names=[APPLY_NAME],
                engine_type=engine_type,
                voice_name=edge_tts_voice_name,
                class_name="",
            )
        except Exception as e:
            self._has_failure = True
            self._failure_message = (
                f"{get_any_position_value_async('guide', 'test_page', 'failure')} {e}"
            )
            self.statusLabel.setText(self._failure_message)
            self.startBtn.setEnabled(True)
            return

        QTimer.singleShot(1200, self._run_next_test)

    def _test_music(self):
        self._set_testing_status("test_music")
        failure_text = get_any_position_value_async("guide", "test_page", "failure")
        feature_text = get_any_position_value_async("guide", "test_page", "test_music")

        files = get_music_files()
        real_files = [
            f
            for f in files
            if f
            not in [
                get_content_name_async("music_settings", "no_music"),
                get_content_name_async("music_settings", "random_play"),
            ]
        ]

        if not real_files:
            QTimer.singleShot(200, self._run_next_test)
            return

        selected_music = readme_settings_async("roll_call_settings", "animation_music")
        if selected_music in (
            "",
            None,
            get_content_name_async("music_settings", "no_music"),
            get_content_name_async("music_settings", "random_play"),
        ):
            selected_music = real_files[0]

        try:
            started = music_player.play_music(
                selected_music,
                settings_group="roll_call_settings",
                loop=False,
                fade_in=False,
            )
        except Exception as e:
            self._has_failure = True
            self._failure_message = f"{failure_text} {e}"
            self.statusLabel.setText(self._failure_message)
            QTimer.singleShot(300, self._run_next_test)
            return

        def check_and_finish():
            if started and music_player.is_playing():
                music_player.stop_music(fade_out=False)
                QTimer.singleShot(200, self._run_next_test)
                return

            self._has_failure = True
            self._failure_message = f"{failure_text} {feature_text}"
            self.statusLabel.setText(self._failure_message)
            QTimer.singleShot(200, self._run_next_test)

        if music_player.wait_play_started(timeout=0.8):
            QTimer.singleShot(5000, check_and_finish)
        else:
            last_error = music_player.get_last_error()
            self._has_failure = True
            self._failure_message = f"{failure_text} {feature_text}"
            if last_error:
                self._failure_message = f"{self._failure_message} {last_error}"
            self.statusLabel.setText(self._failure_message)
            QTimer.singleShot(200, self._run_next_test)

    def _test_classisland(self):
        self._set_testing_status("test_classisland")
        try:
            handler = CSharpIPCHandler.instance()
            if handler.is_connected:
                handler.send_notification(
                    "SecRandom Test",
                    [
                        {
                            "student_id": 0,
                            "student_name": "Test Student",
                            "display_text": "Test Student",
                            "exists": True,
                            "group_name": "",
                            "lottery_name": "",
                        }
                    ],
                )
                self.statusLabel.setText(
                    get_any_position_value_async("guide", "test_page", "success")
                )
                self._push_float_notification("Test Student")
            else:
                self._has_failure = True
                self._failure_message = get_any_position_value_async(
                    "guide", "test_page", "failure"
                )
                self.statusLabel.setText(self._failure_message)
        except Exception as e:
            self._has_failure = True
            self._failure_message = (
                f"{get_any_position_value_async('guide', 'test_page', 'failure')} {e}"
            )
            self.statusLabel.setText(self._failure_message)

        QTimer.singleShot(800, self._run_next_test)

    def finish_test(self):
        self.startBtn.setEnabled(True)
        if self._has_failure and self._failure_message:
            self.statusLabel.setText(self._failure_message)
            return
        result_text = get_any_position_value_async(
            "guide", "test_page", "failure" if self._has_failure else "success"
        )
        self.statusLabel.setText(result_text)

    def _set_testing_status(self, feature_key: str):
        self._current_test_key = feature_key
        testing = get_any_position_value_async("guide", "test_page", "testing")
        feature = get_any_position_value_async("guide", "test_page", feature_key)
        status_text = f"{testing} {feature}"
        self.statusLabel.setText(status_text)

    def _run_next_test(self):
        if not self._tests:
            self.finish_test()
            return

        fn, feature_key = self._tests.pop(0)
        self._current_test_key = feature_key
        fn()

    def _build_tests(self):
        tests = []
        if readme_settings_async("basic_voice_settings", "voice_enable"):
            tests.append((self._test_tts, "test_tts"))

        files = get_music_files()
        real_files = [
            f
            for f in files
            if f
            not in [
                get_content_name_async("music_settings", "no_music"),
                get_content_name_async("music_settings", "random_play"),
            ]
        ]
        if real_files:
            tests.append((self._test_music, "test_music"))

        service_types = [
            readme_settings_async(
                "roll_call_notification_settings", "notification_service_type"
            ),
            readme_settings_async(
                "quick_draw_notification_settings", "notification_service_type"
            ),
            readme_settings_async(
                "lottery_notification_settings", "notification_service_type"
            ),
        ]
        guide_enabled = False
        try:
            guide_enabled = bool(self.window().enhancedPage.linkageSwitch.isChecked())
        except Exception:
            guide_enabled = False

        if guide_enabled or any(t in (1, 2) for t in service_types):
            tests.append((self._test_classisland, "test_classisland"))

        return tests


class LinksPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(16)

        self.logoLabel = QLabel(self)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(str(get_data_path("assets/icon", "secrandom-icon-paper.png")))
        if not pixmap.isNull():
            self.logoLabel.setPixmap(
                pixmap.scaled(
                    96,
                    96,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self.titleLabel = TitleLabel(
            get_any_position_value_async("guide", "links_page", "title")
        )
        self.subtitleLabel = BodyLabel(
            get_any_position_value_async("guide", "links_page", "subtitle")
        )
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitleLabel.setFixedWidth(640)

        self.githubLink = HyperlinkButton(
            GITHUB_WEB,
            get_any_position_value_async("guide", "links_page", "github"),
        )

        self.bilibiliLink = HyperlinkButton(
            BILIBILI_WEB,
            get_any_position_value_async("guide", "links_page", "bilibili"),
        )

        self.docsLink = HyperlinkButton(
            WEBSITE,
            get_any_position_value_async("guide", "links_page", "docs"),
        )

        self.organizationLink = HyperlinkButton(
            SECTL_WEBDITE,
            get_any_position_value_async("guide", "links_page", "organization_website"),
        )

        self.issuesLink = HyperlinkButton(
            f"{GITHUB_WEB}/issues",
            get_any_position_value_async("guide", "links_page", "issues"),
        )

        self.finishBtn = PrimaryPushButton(
            get_any_position_value_async("guide", "links_page", "finish_btn")
        )
        self.finishBtn.setFixedWidth(200)
        self.finishBtn.clicked.connect(self._on_finish)

        self.linksRow = QWidget(self)
        self.linksRowLayout = QHBoxLayout(self.linksRow)
        self.linksRowLayout.setContentsMargins(0, 0, 0, 0)
        self.linksRowLayout.setSpacing(16)
        self.linksRowLayout.addWidget(self.githubLink)
        self.linksRowLayout.addWidget(self.bilibiliLink)
        self.linksRowLayout.addWidget(self.organizationLink)
        self.linksRowLayout.addWidget(self.docsLink)
        self.linksRowLayout.addWidget(self.issuesLink)

        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.logoLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.linksRow, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.finishBtn, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)

    def _on_finish(self):
        try:
            self.window().next_page()
            return
        except Exception:
            pass

        try:
            self.window().close()
        except Exception:
            self.close()
