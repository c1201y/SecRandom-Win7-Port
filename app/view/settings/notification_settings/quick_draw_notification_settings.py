# ==================================================
# 导入库
# ==================================================

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from qfluentwidgets import *

from app.common.IPC_URL.csharp_ipc_handler import CSharpIPCHandler
from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *


# ==================================================
# 闪抽通知设置类
# ==================================================
class quick_draw_notification_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加基础设置组件
        self.basic_settings_widget = basic_settings(self)
        self.vBoxLayout.addWidget(self.basic_settings_widget)

        # 添加浮窗模式设置组件
        self.floating_window_widget = floating_window_settings(self)
        self.vBoxLayout.addWidget(self.floating_window_widget)

        # 添加 ClassIsland 通知设置组件
        self.classisland_notification_widget = classisland_notification_settings(self)
        self.vBoxLayout.addWidget(self.classisland_notification_widget)


class basic_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("quick_draw_notification_settings", "basic_settings")
        )
        self.setBorderRadius(8)

        # 是否开启动画开关
        self.animation_switch = SwitchButton()
        self.animation_switch.setOffText(
            get_content_switchbutton_name_async(
                "quick_draw_notification_settings", "animation", "disable"
            )
        )
        self.animation_switch.setOnText(
            get_content_switchbutton_name_async(
                "quick_draw_notification_settings", "animation", "enable"
            )
        )
        self.animation_switch.setChecked(
            readme_settings_async("quick_draw_notification_settings", "animation")
        )
        self.animation_switch.checkedChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "animation",
                self.animation_switch.isChecked(),
            )
        )

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

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_sanitize_20_filled"),
            get_content_name_async("quick_draw_notification_settings", "animation"),
            get_content_description_async(
                "quick_draw_notification_settings", "animation"
            ),
            self.animation_switch,
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

    def _on_notification_service_type_changed(self, index):
        update_settings(
            "quick_draw_notification_settings",
            "notification_service_type",
            index,
        )
        if index == 1 or index == 2:
            service = CSharpIPCHandler.instance()
            if not service.check_ci_alive():
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
            elif not service.check_plugin_alive():
                hint_title = get_any_position_value_async(
                    "quick_draw_notification_settings",
                    "classisland_plugin_notification_hint",
                    "title",
                )
                hint_content = get_any_position_value_async(
                    "quick_draw_notification_settings",
                    "classisland_plugin_notification_hint",
                    "content",
                )
                InfoBar.warning(
                    title=hint_title,
                    content=hint_content,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self,
                )
            else:
                hint_title = get_any_position_value_async(
                    "quick_draw_notification_settings",
                    "classisland_configured_successfully",
                    "title",
                )
                hint_content = get_any_position_value_async(
                    "quick_draw_notification_settings",
                    "classisland_configured_successfully",
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


class floating_window_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_mode"
            )
        )
        self.setBorderRadius(8)

        # 窗口位置
        self.window_position_combo_box = ComboBox()
        self.window_position_combo_box.addItems(
            get_content_combo_name_async(
                "quick_draw_notification_settings", "floating_window_position"
            )
        )
        self.window_position_combo_box.setCurrentIndex(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_position"
            )
        )
        self.window_position_combo_box.currentTextChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_position",
                self.window_position_combo_box.currentIndex(),
            )
        )

        # 水平偏移值
        self.horizontal_offset_spin_spinbox = SpinBox()
        self.horizontal_offset_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.horizontal_offset_spin_spinbox.setRange(-25600, 25600)
        self.horizontal_offset_spin_spinbox.setSuffix("px")
        self.horizontal_offset_spin_spinbox.setValue(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_horizontal_offset"
            )
        )
        self.horizontal_offset_spin_spinbox.valueChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_horizontal_offset",
                self.horizontal_offset_spin_spinbox.value(),
            )
        )

        # 垂直偏移值
        self.vertical_offset_spin_spinbox = SpinBox()
        self.vertical_offset_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.vertical_offset_spin_spinbox.setRange(-25600, 25600)
        self.vertical_offset_spin_spinbox.setSuffix("px")
        self.vertical_offset_spin_spinbox.setValue(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_vertical_offset"
            )
        )
        self.vertical_offset_spin_spinbox.valueChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_vertical_offset",
                self.vertical_offset_spin_spinbox.value(),
            )
        )

        # 窗口透明度
        self.window_transparency_spin_spinbox = SpinBox()
        self.window_transparency_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.window_transparency_spin_spinbox.setRange(0, 100)
        self.window_transparency_spin_spinbox.setSuffix("%")
        self.window_transparency_spin_spinbox.setValue(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_transparency"
            )
            * 100
        )
        self.window_transparency_spin_spinbox.valueChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_transparency",
                self.window_transparency_spin_spinbox.value() / 100,
            )
        )

        # 浮窗自动关闭时间
        self.floating_window_auto_close_time_spinbox = SpinBox()
        self.floating_window_auto_close_time_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.floating_window_auto_close_time_spinbox.setRange(0, 60)
        self.floating_window_auto_close_time_spinbox.setSuffix("s")
        self.floating_window_auto_close_time_spinbox.setValue(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_auto_close_time"
            )
        )
        self.floating_window_auto_close_time_spinbox.valueChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_auto_close_time",
                self.floating_window_auto_close_time_spinbox.value(),
            )
        )

        # 选择启用的显示器下拉框
        self.enabled_monitor_combo_box = ComboBox()
        self.enabled_monitor_combo_box.addItems(self.get_monitor_list())
        if (
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_enabled_monitor"
            )
            == "OFF"
        ):
            self.enabled_monitor_combo_box.setCurrentText(self.get_monitor_list()[0])
            update_settings(
                "quick_draw_notification_settings",
                "floating_window_enabled_monitor",
                self.enabled_monitor_combo_box.currentText(),
            )
        self.enabled_monitor_combo_box.setCurrentText(
            readme_settings_async(
                "quick_draw_notification_settings", "floating_window_enabled_monitor"
            )
        )
        self.enabled_monitor_combo_box.currentTextChanged.connect(
            lambda: update_settings(
                "quick_draw_notification_settings",
                "floating_window_enabled_monitor",
                self.enabled_monitor_combo_box.currentText(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_window_text_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_enabled_monitor"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_enabled_monitor"
            ),
            self.enabled_monitor_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_position_to_back_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_position"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_position"
            ),
            self.window_position_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_align_stretch_horizontal_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_horizontal_offset"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_horizontal_offset"
            ),
            self.horizontal_offset_spin_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_align_stretch_vertical_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_vertical_offset"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_vertical_offset"
            ),
            self.vertical_offset_spin_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_transparency_square_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_transparency"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_transparency"
            ),
            self.window_transparency_spin_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_time_picker_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "floating_window_auto_close_time"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "floating_window_auto_close_time"
            ),
            self.floating_window_auto_close_time_spinbox,
        )

        # 连接屏幕变化信号
        QApplication.instance().screenAdded.connect(self.update_monitor_list)
        QApplication.instance().screenRemoved.connect(self.update_monitor_list)

    # 获取显示器列表
    def get_monitor_list(self):
        monitor_list = []
        for screen in QApplication.instance().screens():
            monitor_list.append(screen.name())
        return monitor_list

    # 更新显示器列表
    def update_monitor_list(self, screen=None):
        current_text = self.enabled_monitor_combo_box.currentText()
        self.enabled_monitor_combo_box.clear()
        self.enabled_monitor_combo_box.addItems(self.get_monitor_list())

        # 尝试保持之前选中的显示器
        index = self.enabled_monitor_combo_box.findText(current_text)
        if index >= 0:
            self.enabled_monitor_combo_box.setCurrentIndex(index)
        else:
            # 如果之前选中的显示器不存在了，使用第一个显示器
            self.enabled_monitor_combo_box.setCurrentText(self.get_monitor_list()[0])
            update_settings(
                "quick_draw_notification_settings",
                "floating_window_enabled_monitor",
                self.enabled_monitor_combo_box.currentText(),
            )


class classisland_notification_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "quick_draw_notification_settings",
                "classisland_notification_service_settings",
            )
        )
        self.setBorderRadius(8)

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
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async(
                "quick_draw_notification_settings", "notification_display_duration"
            ),
            get_content_description_async(
                "quick_draw_notification_settings", "notification_display_duration"
            ),
            self.notification_display_duration_spinbox,
        )
