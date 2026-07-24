# ==================================================
# 导入库
# ==================================================
from __future__ import annotations
import os

from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.tools.settings_access import get_safe_font_size
from app.tools.list_specific_settings_access import (
    read_quick_draw_setting,
    set_quick_draw_setting_override,
    get_safe_font_size_list_specific,
    clear_list_specific_overrides,
)
from app.Language.obtain_language import *
from app.common.data.list import *


# ==================================================
# 闪抽设置
# ==================================================
class quick_draw_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        self.list_specific_entry_widget = quick_draw_list_specific_entry(self)
        self.vBoxLayout.addWidget(self.list_specific_entry_widget)

        # 添加抽取功能设置组件
        self.extraction_function_widget = quick_draw_extraction_function(self)
        self.vBoxLayout.addWidget(self.extraction_function_widget)

        # 添加显示设置组件
        self.display_settings_widget = quick_draw_display_settings(self)
        self.vBoxLayout.addWidget(self.display_settings_widget)

        # 添加动画设置组件
        self.animation_settings_widget = quick_draw_animation_settings(self)
        self.vBoxLayout.addWidget(self.animation_settings_widget)


class quick_draw_list_specific_entry(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "quick_draw_settings", "list_specific_settings_entry"
            )
        )
        self.setBorderRadius(8)

        self.open_button = PushButton(
            get_content_pushbutton_name_async(
                "quick_draw_settings", "list_specific_settings_entry"
            )
        )
        self.open_button.clicked.connect(self._open_window)

        self.addGroup(
            get_theme_icon("ic_fluent_settings_20_filled"),
            get_content_name_async(
                "quick_draw_settings", "list_specific_settings_entry"
            ),
            get_content_description_async(
                "quick_draw_settings", "list_specific_settings_entry"
            ),
            self.open_button,
        )

    def _open_window(self):
        try:
            from app.page_building.another_window import (
                create_quick_draw_list_specific_settings_window,
            )

            create_quick_draw_list_specific_settings_window()
        except Exception as e:
            logger.exception(f"打开独立名单配置窗口失败: {e}")


class quick_draw_extraction_function(GroupHeaderCardWidget):
    def __init__(
        self,
        parent=None,
        list_name: str | None = None,
        *,
        show_default_class: bool = True,
        enable_file_watcher: bool = True,
    ):
        super().__init__(parent)
        self._list_name = list_name
        self._show_default_class = show_default_class
        self._enable_file_watcher = enable_file_watcher
        self.setTitle(
            get_content_name_async("quick_draw_settings", "extraction_function")
        )
        self.setBorderRadius(8)

        # 抽取模式下拉框（延迟填充）
        self.draw_mode_combo = ComboBox()
        self.draw_mode_combo.currentIndexChanged.connect(self.on_draw_mode_changed)

        # 半重复抽取次数输入框
        self.half_repeat_spin = SpinBox()
        self.half_repeat_spin.setFixedWidth(WIDTH_SPINBOX)
        self.half_repeat_spin.setRange(0, 100)
        self.half_repeat_spin.setValue(self._read_setting("half_repeat"))
        self.half_repeat_spin.valueChanged.connect(
            lambda: self._write_setting("half_repeat", self.half_repeat_spin.value())
        )

        # 抽取方式下拉框（延迟填充）
        self.draw_type_combo = ComboBox()
        self.draw_type_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "draw_type", self.draw_type_combo.currentIndex()
            )
        )

        self.default_class_combo = None
        if self._show_default_class:
            self.default_class_combo = ComboBox()
            self.default_class_combo.currentIndexChanged.connect(
                lambda: update_settings(
                    "quick_draw_settings",
                    "default_class",
                    self.default_class_combo.currentText(),
                )
            )

        # 抽取人数输入框
        self.draw_count_spin = SpinBox()
        self.draw_count_spin.setFixedWidth(WIDTH_SPINBOX)
        self.draw_count_spin.setRange(1, 100)
        self.draw_count_spin.setValue(self._read_setting("draw_count"))
        self.draw_count_spin.valueChanged.connect(
            lambda: self._write_setting("draw_count", self.draw_count_spin.value())
        )

        # 点击后禁用时间输入框
        self.disable_after_click_spin = SpinBox()
        self.disable_after_click_spin.setFixedWidth(WIDTH_SPINBOX)
        self.disable_after_click_spin.setRange(0, 60)
        self.disable_after_click_spin.setSuffix("s")
        self.disable_after_click_spin.setValue(
            self._read_setting("disable_after_click")
        )
        self.disable_after_click_spin.valueChanged.connect(
            lambda: self._write_setting(
                "disable_after_click", self.disable_after_click_spin.value()
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_document_bullet_list_cube_20_filled"),
            get_content_name_async("quick_draw_settings", "draw_mode"),
            get_content_description_async("quick_draw_settings", "draw_mode"),
            self.draw_mode_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_clipboard_bullet_list_20_filled"),
            get_content_name_async("quick_draw_settings", "half_repeat"),
            get_content_description_async("quick_draw_settings", "half_repeat"),
            self.half_repeat_spin,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_drawer_add_20_filled"),
            get_content_name_async("quick_draw_settings", "draw_type"),
            get_content_description_async("quick_draw_settings", "draw_type"),
            self.draw_type_combo,
        )
        if self._show_default_class and self.default_class_combo is not None:
            self.addGroup(
                get_theme_icon("ic_fluent_class_20_filled"),
                get_content_name_async("quick_draw_settings", "default_class"),
                get_content_description_async("quick_draw_settings", "default_class"),
                self.default_class_combo,
            )
        self.addGroup(
            get_theme_icon("ic_fluent_people_20_filled"),
            get_content_name_async("quick_draw_settings", "draw_count"),
            get_content_description_async("quick_draw_settings", "draw_count"),
            self.draw_count_spin,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async("quick_draw_settings", "disable_after_click"),
            get_content_description_async("quick_draw_settings", "disable_after_click"),
            self.disable_after_click_spin,
        )

        # 初始化时先在后台加载所有需要的选项并回填
        QTimer.singleShot(0, self._start_background_load)

    def _start_background_load(self):
        class _Signals(QObject):
            loaded = Signal(dict)

        class _Loader(QRunnable):
            def __init__(self, fn, signals):
                super().__init__()
                self.fn = fn
                self.signals = signals

            def run(self):
                try:
                    data = self.fn()
                    self.signals.loaded.emit(data)
                except Exception as e:
                    logger.exception(f"后台加载 quick_draw_settings 数据失败: {e}")

        def _collect():
            data = {}
            try:
                data["draw_mode_items"] = get_content_combo_name_async(
                    "quick_draw_settings", "draw_mode"
                )
                data["draw_mode_index"] = self._read_setting("draw_mode")
                data["half_repeat_value"] = self._read_setting("half_repeat")
                data["draw_type_items"] = get_content_combo_name_async(
                    "quick_draw_settings", "draw_type"
                )
                data["draw_type_index"] = self._read_setting("draw_type")
                if self._show_default_class:
                    data["class_list"] = get_class_name_list()
                    data["default_class"] = readme_settings_async(
                        "quick_draw_settings", "default_class"
                    )
            except Exception as e:
                logger.exception(f"收集 quick_draw_settings 初始数据失败: {e}")
            return data

        signals = _Signals()
        signals.loaded.connect(self._on_background_loaded)
        runnable = _Loader(_collect, signals)
        QThreadPool.globalInstance().start(runnable)

    def _on_background_loaded(self, data: dict):
        try:
            if "draw_mode_items" in data:
                self.draw_mode_combo.addItems(data.get("draw_mode_items", []))
                self.draw_mode_combo.setCurrentIndex(data.get("draw_mode_index", 0))
            if "half_repeat_value" in data:
                self.half_repeat_spin.setValue(data.get("half_repeat_value", 0))
            if "draw_type_items" in data:
                self.draw_type_combo.addItems(data.get("draw_type_items", []))
                self.draw_type_combo.setCurrentIndex(data.get("draw_type_index", 0))
            if (
                self._show_default_class
                and "class_list" in data
                and self.default_class_combo is not None
            ):
                class_list = data.get("class_list", [])
                self.default_class_combo.clear()
                self.default_class_combo.addItems(class_list)
                default_class = data.get("default_class", "")
                if default_class:
                    self.default_class_combo.setCurrentText(default_class)
                elif not class_list:
                    self.default_class_combo.setCurrentIndex(-1)
                    self.default_class_combo.setPlaceholderText(
                        get_content_name_async("quick_draw_settings", "default_class")
                    )

            self.on_draw_mode_changed()
        except Exception as e:
            logger.exception(f"回填 quick_draw_settings 数据失败: {e}")

    def on_draw_mode_changed(self):
        """当抽取模式改变时的处理逻辑"""
        # 更新设置值
        self._write_setting("draw_mode", self.draw_mode_combo.currentIndex())

        # 获取当前抽取模式索引
        draw_mode_index = self.draw_mode_combo.currentIndex()

        # 根据抽取模式设置不同的控制逻辑
        if draw_mode_index == 0:  # 重复抽取模式
            # 设置half_repeat_spin为0并禁用
            self.half_repeat_spin.setEnabled(False)
            self.half_repeat_spin.setRange(0, 0)
            self.half_repeat_spin.setValue(0)
            # 更新设置
            self._write_setting("half_repeat", 0)

        else:  # 不重复抽取模式或半重复抽取模式
            # 根据具体模式设置half_repeat_spin
            if draw_mode_index == 1:  # 不重复抽取模式
                # 设置half_repeat_spin为1并禁用
                self.half_repeat_spin.setEnabled(False)
                self.half_repeat_spin.setRange(1, 1)
                self.half_repeat_spin.setValue(1)
                # 更新设置
                self._write_setting("half_repeat", 1)
            else:  # 半重复抽取模式（索引2）
                # 设置half_repeat_spin为2-100范围并启用
                self.half_repeat_spin.setEnabled(True)
                self.half_repeat_spin.setRange(2, 100)
                # 如果当前值小于2，则设置为2
                if self.half_repeat_spin.value() < 2:
                    self.half_repeat_spin.setValue(2)
                    # 更新设置
                    self._write_setting("half_repeat", 2)

    def _read_setting(self, key: str, default=None):
        if self._list_name:
            return read_quick_draw_setting(self._list_name, key, default)
        return readme_settings_async("quick_draw_settings", key, default)

    def _write_setting(self, key: str, value):
        if self._list_name:
            set_quick_draw_setting_override(self._list_name, key, value)
            return
        update_settings("quick_draw_settings", key, value)


class quick_draw_display_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self._list_name = list_name
        self.setTitle(get_content_name_async("quick_draw_settings", "display_settings"))
        self.setBorderRadius(8)

        # 字体大小输入框
        self.font_size_spin = SpinBox()
        self.font_size_spin.setFixedWidth(WIDTH_SPINBOX)
        self.font_size_spin.setRange(10, 1000)
        self.font_size_spin.setSuffix("px")
        if self._list_name:
            self.font_size_spin.setValue(
                get_safe_font_size_list_specific(
                    "quick_draw_settings",
                    "quick_draw_list_specific_settings",
                    self._list_name,
                    "font_size",
                )
            )
        else:
            self.font_size_spin.setValue(
                get_safe_font_size("quick_draw_settings", "font_size")
            )
        self.font_size_spin.valueChanged.connect(
            lambda: self._write_setting("font_size", self.font_size_spin.value())
        )

        # 是否使用全局字体下拉框
        self.use_global_font_combo = ComboBox()
        self.use_global_font_combo.addItems(
            get_content_combo_name_async("quick_draw_settings", "use_global_font")
        )
        self.use_global_font_combo.setCurrentIndex(
            self._read_setting("use_global_font")
        )
        self.use_global_font_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "use_global_font", self.use_global_font_combo.currentIndex()
            )
        )

        # 自定义字体下拉框
        self.custom_font_combo = ComboBox()
        self.custom_font_combo.addItems(QFontDatabase().families())
        current_custom_font = self._read_setting("custom_font")
        try:
            index = self.custom_font_combo.findText(current_custom_font)
            if index >= 0:
                self.custom_font_combo.setCurrentIndex(index)
            else:
                self.custom_font_combo.setCurrentIndex(0)
        except:
            self.custom_font_combo.setCurrentIndex(0)
        self.custom_font_combo.currentTextChanged.connect(
            lambda: self._write_setting(
                "custom_font", self.custom_font_combo.currentText()
            )
        )

        # 结果显示格式下拉框
        self.display_format_combo = ComboBox()
        self.display_format_combo.addItems(
            get_content_combo_name_async("quick_draw_settings", "display_format")
        )
        self.display_format_combo.setCurrentIndex(self._read_setting("display_format"))
        self.display_format_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "display_format", self.display_format_combo.currentIndex()
            )
        )

        # 显示随机组员格式下拉框
        self.show_random_format_combo = ComboBox()
        self.show_random_format_combo.addItems(
            get_content_combo_name_async("quick_draw_settings", "show_random")
        )
        self.show_random_format_combo.setCurrentIndex(self._read_setting("show_random"))
        self.show_random_format_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "show_random", self.show_random_format_combo.currentIndex()
            )
        )

        self.show_tags_switch = SwitchButton()
        self.show_tags_switch.setOffText(
            get_content_switchbutton_name_async(
                "quick_draw_settings", "show_tags", "disable"
            )
        )
        self.show_tags_switch.setOnText(
            get_content_switchbutton_name_async(
                "quick_draw_settings", "show_tags", "enable"
            )
        )
        self.show_tags_switch.setChecked(bool(self._read_setting("show_tags")))
        self.show_tags_switch.checkedChanged.connect(
            lambda: self._write_setting("show_tags", self.show_tags_switch.isChecked())
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_text_font_size_20_filled"),
            get_content_name_async("quick_draw_settings", "use_global_font"),
            get_content_description_async("quick_draw_settings", "use_global_font"),
            self.use_global_font_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_text_font_20_filled"),
            get_content_name_async("quick_draw_settings", "custom_font"),
            get_content_description_async("quick_draw_settings", "custom_font"),
            self.custom_font_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_text_font_20_filled"),
            get_content_name_async("quick_draw_settings", "font_size"),
            get_content_description_async("quick_draw_settings", "font_size"),
            self.font_size_spin,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_text_sparkle_20_filled"),
            get_content_name_async("quick_draw_settings", "display_format"),
            get_content_description_async("quick_draw_settings", "display_format"),
            self.display_format_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_group_list_20_filled"),
            get_content_name_async("quick_draw_settings", "show_random"),
            get_content_description_async("quick_draw_settings", "show_random"),
            self.show_random_format_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_tag_20_filled"),
            get_content_name_async("quick_draw_settings", "show_tags"),
            get_content_description_async("quick_draw_settings", "show_tags"),
            self.show_tags_switch,
        )

    def _read_setting(self, key: str, default=None):
        if self._list_name:
            return read_quick_draw_setting(self._list_name, key, default)
        return readme_settings_async("quick_draw_settings", key, default)

    def _write_setting(self, key: str, value):
        if self._list_name:
            set_quick_draw_setting_override(self._list_name, key, value)
            return
        update_settings("quick_draw_settings", key, value)


class quick_draw_animation_settings(QWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self._list_name = list_name
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加基础动画设置组件
        self.basic_animation_widget = quick_draw_basic_animation_settings(
            self, list_name=self._list_name
        )
        self.vBoxLayout.addWidget(self.basic_animation_widget)

        # 添加颜色主题设置组件
        self.color_theme_widget = quick_draw_color_theme_settings(
            self, list_name=self._list_name
        )
        self.vBoxLayout.addWidget(self.color_theme_widget)

        # 添加学生图片设置组件
        self.student_image_widget = quick_draw_student_image_settings(
            self, list_name=self._list_name
        )
        self.vBoxLayout.addWidget(self.student_image_widget)


class quick_draw_basic_animation_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self._list_name = list_name
        self.setTitle(
            get_content_name_async("quick_draw_settings", "basic_animation_settings")
        )
        self.setBorderRadius(8)

        # 动画模式下拉框
        self.animation_combo = ComboBox()
        self.animation_combo.addItems(
            get_content_combo_name_async("quick_draw_settings", "animation")
        )
        self.animation_combo.setCurrentIndex(
            int(self._read_setting("animation") or 1) - 1
        )
        self.animation_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "animation", self.animation_combo.currentIndex() + 1
            )
        )

        # 动画间隔输入框
        self.animation_interval_spin = SpinBox()
        self.animation_interval_spin.setFixedWidth(WIDTH_SPINBOX)
        self.animation_interval_spin.setRange(1, 1000)
        self.animation_interval_spin.setSuffix("ms")
        self.animation_interval_spin.setValue(self._read_setting("animation_interval"))
        self.animation_interval_spin.valueChanged.connect(
            lambda: self._write_setting(
                "animation_interval", self.animation_interval_spin.value()
            )
        )

        # 自动播放次数输入框
        self.autoplay_count_spin = SpinBox()
        self.autoplay_count_spin.setFixedWidth(WIDTH_SPINBOX)
        self.autoplay_count_spin.setRange(1, 1000)
        self.autoplay_count_spin.setValue(self._read_setting("autoplay_count"))
        self.autoplay_count_spin.valueChanged.connect(
            lambda: self._write_setting(
                "autoplay_count", self.autoplay_count_spin.value()
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_sanitize_20_filled"),
            get_content_name_async("quick_draw_settings", "animation"),
            get_content_description_async("quick_draw_settings", "animation"),
            self.animation_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timeline_20_filled"),
            get_content_name_async("quick_draw_settings", "animation_interval"),
            get_content_description_async("quick_draw_settings", "animation_interval"),
            self.animation_interval_spin,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_play_20_filled"),
            get_content_name_async("quick_draw_settings", "autoplay_count"),
            get_content_description_async("quick_draw_settings", "autoplay_count"),
            self.autoplay_count_spin,
        )

    def _read_setting(self, key: str, default=None):
        if self._list_name:
            return read_quick_draw_setting(self._list_name, key, default)
        return readme_settings_async("quick_draw_settings", key, default)

    def _write_setting(self, key: str, value):
        if self._list_name:
            set_quick_draw_setting_override(self._list_name, key, value)
            return
        update_settings("quick_draw_settings", key, value)


class quick_draw_color_theme_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self._list_name = list_name
        self.setTitle(
            get_content_name_async("quick_draw_settings", "color_theme_settings")
        )
        self.setBorderRadius(8)

        # 合并动画/结果颜色主题下拉框
        self.animation_color_theme_combo = ComboBox()
        self.animation_color_theme_combo.addItems(
            get_content_combo_name_async("quick_draw_settings", "animation_color_theme")
        )
        self.animation_color_theme_combo.setCurrentIndex(
            self._read_setting("animation_color_theme")
        )
        self.animation_color_theme_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "animation_color_theme", self.animation_color_theme_combo.currentIndex()
            )
        )

        # 合并动画/结果固定颜色
        self.animation_fixed_color_button = ColorConfigItem(
            "Theme",
            "Color",
            self._read_setting("animation_fixed_color"),
        )
        self.animation_fixed_color_button.valueChanged.connect(
            lambda color: self._write_setting("animation_fixed_color", color.name())
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_color_20_filled"),
            get_content_name_async("quick_draw_settings", "animation_color_theme"),
            get_content_description_async(
                "quick_draw_settings", "animation_color_theme"
            ),
            self.animation_color_theme_combo,
        )

        self.animationColorCard = ColorSettingCard(
            self.animation_fixed_color_button,
            get_theme_icon("ic_fluent_text_color_20_filled"),
            self.tr(
                get_content_name_async("quick_draw_settings", "animation_fixed_color")
            ),
            self.tr(
                get_content_description_async(
                    "quick_draw_settings", "animation_fixed_color"
                )
            ),
            self,
        )

        self.vBoxLayout.addWidget(self.animationColorCard)

    def _read_setting(self, key: str, default=None):
        if self._list_name:
            return read_quick_draw_setting(self._list_name, key, default)
        return readme_settings_async("quick_draw_settings", key, default)

    def _write_setting(self, key: str, value):
        if self._list_name:
            set_quick_draw_setting_override(self._list_name, key, value)
            return
        update_settings("quick_draw_settings", key, value)


class quick_draw_student_image_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self._list_name = list_name
        self.setTitle(
            get_content_name_async("quick_draw_settings", "student_image_settings")
        )
        self.setBorderRadius(8)

        # 学生图片开关
        self.student_image_switch = SwitchButton()
        self.student_image_switch.setOffText(
            get_content_switchbutton_name_async(
                "quick_draw_settings", "student_image", "disable"
            )
        )
        self.student_image_switch.setOnText(
            get_content_switchbutton_name_async(
                "quick_draw_settings", "student_image", "enable"
            )
        )
        self.student_image_switch.setChecked(self._read_setting("student_image"))
        self.student_image_switch.checkedChanged.connect(
            lambda: self._write_setting(
                "student_image", self.student_image_switch.isChecked()
            )
        )

        self.student_image_position_combo = ComboBox()
        self.student_image_position_combo.addItems(
            get_content_combo_name_async(
                "quick_draw_settings", "student_image_position"
            )
        )
        self.student_image_position_combo.setCurrentIndex(
            self._read_setting("student_image_position")
        )
        self.student_image_position_combo.currentIndexChanged.connect(
            lambda: self._write_setting(
                "student_image_position",
                self.student_image_position_combo.currentIndex(),
            )
        )

        # 打开学生图片文件夹按钮
        self.open_student_image_folder_button = PushButton(
            get_content_name_async("quick_draw_settings", "open_student_image_folder")
        )
        self.open_student_image_folder_button.clicked.connect(
            lambda: self.open_student_image_folder()
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_image_circle_20_filled"),
            get_content_name_async("quick_draw_settings", "student_image"),
            get_content_description_async("quick_draw_settings", "student_image"),
            self.student_image_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_image_circle_20_filled"),
            get_content_name_async("quick_draw_settings", "student_image_position"),
            get_content_description_async(
                "quick_draw_settings", "student_image_position"
            ),
            self.student_image_position_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_folder_open_20_filled"),
            get_content_name_async("quick_draw_settings", "open_student_image_folder"),
            get_content_description_async(
                "quick_draw_settings", "open_student_image_folder"
            ),
            self.open_student_image_folder_button,
        )

    def _read_setting(self, key: str, default=None):
        if self._list_name:
            return read_quick_draw_setting(self._list_name, key, default)
        return readme_settings_async("quick_draw_settings", key, default)

    def _write_setting(self, key: str, value):
        if self._list_name:
            set_quick_draw_setting_override(self._list_name, key, value)
            return
        update_settings("quick_draw_settings", key, value)

    def open_student_image_folder(self):
        """打开学生图片文件夹"""
        folder_path = get_data_path(STUDENT_IMAGE_FOLDER)
        if not folder_path.exists():
            os.makedirs(folder_path, exist_ok=True)
        if folder_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
        else:
            logger.exception("无法获取学生图片文件夹路径")


class QuickDrawListSpecificSettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from app.tools.settings_access import get_settings_signals

        self._dirty = False
        self._suppress_dirty = False
        self._last_overrides_map = None

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        self.select_list_card = GroupHeaderCardWidget(self)
        self.select_list_card.setTitle(
            get_content_name_async(
                "quick_draw_settings", "list_specific_settings_select_list"
            )
        )
        self.select_list_card.setBorderRadius(8)

        self.list_combo = ComboBox()
        self._refresh_list_combo()
        self.list_combo.currentTextChanged.connect(self._on_list_changed)

        self.sync_button = PushButton(
            get_content_pushbutton_name_async(
                "quick_draw_settings", "list_specific_settings_sync_button"
            )
        )
        self.sync_button.setEnabled(False)
        self.sync_button.clicked.connect(self._sync_to_global)

        self.select_list_card.addGroup(
            get_theme_icon("ic_fluent_class_20_filled"),
            get_content_name_async(
                "quick_draw_settings", "list_specific_settings_select_list"
            ),
            get_content_description_async(
                "quick_draw_settings", "list_specific_settings_select_list"
            ),
            self.list_combo,
        )
        self.select_list_card.addGroup(
            get_theme_icon("ic_fluent_arrow_sync_circle_20_filled"),
            get_content_name_async(
                "quick_draw_settings", "list_specific_settings_sync_button"
            ),
            get_content_description_async(
                "quick_draw_settings", "list_specific_settings_sync_button"
            ),
            self.sync_button,
        )
        self.vBoxLayout.addWidget(self.select_list_card)

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.vBoxLayout.addWidget(self.content_widget)

        settings_signals = get_settings_signals()
        settings_signals.settingChanged.connect(self._on_setting_changed)

        self._rebuild_content()

    def _refresh_list_combo(self):
        current = self.list_combo.currentText() if hasattr(self, "list_combo") else ""
        self.list_combo.blockSignals(True)
        self.list_combo.clear()
        class_list = get_class_name_list()
        self.list_combo.addItems(class_list)
        if current and current in class_list:
            self.list_combo.setCurrentText(current)
        elif class_list:
            self.list_combo.setCurrentIndex(0)
        else:
            self.list_combo.setCurrentIndex(-1)
            self.list_combo.setPlaceholderText(
                get_content_name_async("quick_draw_settings", "default_class")
            )
        self.list_combo.blockSignals(False)

    def _on_list_changed(self, _text: str):
        self._rebuild_content()

    def _on_setting_changed(self, first_level_key, second_level_key, value):
        if self._suppress_dirty:
            return
        if first_level_key != "quick_draw_list_specific_settings":
            return
        if second_level_key != "overrides":
            return

        list_name = (self.list_combo.currentText() or "").strip()
        if not list_name:
            return

        new_map = value if isinstance(value, dict) else {}
        current_overrides = new_map.get(list_name)
        self.sync_button.setEnabled(
            isinstance(current_overrides, dict) and len(current_overrides) > 0
        )
        self._last_overrides_map = new_map

    def _sync_to_global(self):
        list_name = (self.list_combo.currentText() or "").strip()
        if not list_name:
            return

        self._suppress_dirty = True
        try:
            clear_list_specific_overrides(
                "quick_draw_list_specific_settings", list_name
            )
        finally:
            self._suppress_dirty = False

        self._dirty = False
        self.sync_button.setEnabled(False)
        self._rebuild_content()

    def _rebuild_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        list_name = (self.list_combo.currentText() or "").strip()
        self._dirty = False
        self.sync_button.setEnabled(False)
        self._last_overrides_map = readme_settings_async(
            "quick_draw_list_specific_settings", "overrides", {}
        )
        if not list_name:
            return
        current_overrides = (
            self._last_overrides_map.get(list_name)
            if isinstance(self._last_overrides_map, dict)
            else None
        )
        self.sync_button.setEnabled(
            isinstance(current_overrides, dict) and len(current_overrides) > 0
        )

        self.content_layout.addWidget(
            quick_draw_extraction_function(
                self,
                list_name=list_name,
                show_default_class=False,
                enable_file_watcher=False,
            )
        )
        self.content_layout.addWidget(
            quick_draw_display_settings(self, list_name=list_name)
        )
        self.content_layout.addWidget(
            quick_draw_animation_settings(self, list_name=list_name)
        )
