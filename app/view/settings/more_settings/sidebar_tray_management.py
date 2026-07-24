# ==================================================
# 导入库
# ==================================================

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
from app.Language.obtain_language import *


# ==================================================
# 页面管理
# ==================================================
class sidebar_tray_management(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 使用占位与延迟创建以减少首次打开时的卡顿
        self._deferred_factories = {}

        def make_placeholder(attr_name: str):
            w = QWidget()
            w.setObjectName(attr_name)
            layout = QVBoxLayout(w)
            layout.setContentsMargins(0, 0, 0, 0)
            self.vBoxLayout.addWidget(w)
            return w

        self.sidebar_management_window = make_placeholder("sidebar_management_window")
        self._deferred_factories["sidebar_management_window"] = (
            lambda: sidebar_management_window(self)
        )

        self.tray_management = make_placeholder("tray_management")
        self._deferred_factories["tray_management"] = lambda: tray_management(self)

        # 分批异步创建真实子组件
        try:
            for i, name in enumerate(list(self._deferred_factories.keys())):
                QTimer.singleShot(120 * i, lambda n=name: self._create_deferred(n))
        except Exception as e:
            from loguru import logger

            logger.exception("Error reading tray management settings: {}", e)

    def _create_deferred(self, name: str):
        factories = getattr(self, "_deferred_factories", {})
        if name not in factories:
            return
        try:
            factory = factories.pop(name)
        except Exception:
            return
        try:
            real_widget = factory()
        except Exception:
            return

        placeholder = getattr(self, name, None)
        if placeholder is None:
            try:
                self.vBoxLayout.addWidget(real_widget)
            except Exception as e:
                from loguru import logger

                logger.exception("Error handling tray action: {}", e)
            setattr(self, name, real_widget)
            return

        layout = None
        try:
            layout = placeholder.layout()
        except Exception:
            layout = None

        if layout is None:
            try:
                index = -1
                for i in range(self.vBoxLayout.count()):
                    item = self.vBoxLayout.itemAt(i)
                    if item and item.widget() is placeholder:
                        index = i
                        break
                if index >= 0:
                    try:
                        item = self.vBoxLayout.takeAt(index)
                        widget = item.widget() if item else None
                        if widget is not None:
                            widget.deleteLater()
                        self.vBoxLayout.insertWidget(index, real_widget)
                    except Exception:
                        self.vBoxLayout.addWidget(real_widget)
                else:
                    self.vBoxLayout.addWidget(real_widget)
            except Exception:
                try:
                    self.vBoxLayout.addWidget(real_widget)
                except Exception as e:
                    from loguru import logger

                    logger.exception("Error in tray sub-action: {}", e)
            setattr(self, name, real_widget)
            return

        try:
            layout.addWidget(real_widget)
            setattr(self, name, real_widget)
        except Exception as e:
            try:
                self.vBoxLayout.addWidget(real_widget)
                setattr(self, name, real_widget)
            except Exception as inner_e:
                from loguru import logger

                logger.exception(
                    "Error adding real_widget as fallback in sidebar_tray_management: {}",
                    inner_e,
                )


class sidebar_management_window(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("sidebar_management_window", "title"))
        self.setBorderRadius(8)

        # 点名侧边栏位置下拉框
        self.roll_call_sidebar_position_comboBox = ComboBox(self)
        self.roll_call_sidebar_position_comboBox.addItems(
            get_content_combo_name_async(
                "sidebar_management_window", "roll_call_sidebar_position"
            )
        )
        self.roll_call_sidebar_position_comboBox.setCurrentIndex(
            readme_settings_async(
                "sidebar_management_window", "roll_call_sidebar_position"
            )
        )
        self.roll_call_sidebar_position_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "sidebar_management_window",
                "roll_call_sidebar_position",
                self.roll_call_sidebar_position_comboBox.currentIndex(),
            )
        )

        # 抽奖侧边栏位置下拉框
        self.lottery_sidebar_position_comboBox = ComboBox(self)
        self.lottery_sidebar_position_comboBox.addItems(
            get_content_combo_name_async(
                "sidebar_management_window", "lottery_sidebar_position"
            )
        )
        self.lottery_sidebar_position_comboBox.setCurrentIndex(
            readme_settings_async(
                "sidebar_management_window", "lottery_sidebar_position"
            )
        )
        self.lottery_sidebar_position_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "sidebar_management_window",
                "lottery_sidebar_position",
                self.lottery_sidebar_position_comboBox.currentIndex(),
            )
        )

        self.camera_preview_sidebar_position_comboBox = ComboBox(self)
        self.camera_preview_sidebar_position_comboBox.addItems(
            get_content_combo_name_async(
                "sidebar_management_window", "camera_preview_sidebar_position"
            )
        )
        self.camera_preview_sidebar_position_comboBox.setCurrentIndex(
            readme_settings_async(
                "sidebar_management_window", "camera_preview_sidebar_position"
            )
        )
        self.camera_preview_sidebar_position_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "sidebar_management_window",
                "camera_preview_sidebar_position",
                self.camera_preview_sidebar_position_comboBox.currentIndex(),
            )
        )

        # 主窗口历史记录下拉框
        self.main_window_history_comboBox = ComboBox(self)
        self.main_window_history_comboBox.addItems(
            get_content_combo_name_async(
                "sidebar_management_window", "main_window_history"
            )
        )
        self.main_window_history_comboBox.setCurrentIndex(
            readme_settings_async("sidebar_management_window", "main_window_history")
        )
        self.main_window_history_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "sidebar_management_window",
                "main_window_history",
                self.main_window_history_comboBox.currentIndex(),
            )
        )

        # 设置图标下拉框
        self.settings_icon_comboBox = ComboBox(self)
        self.settings_icon_comboBox.addItems(
            get_content_combo_name_async("sidebar_management_window", "settings_icon")
        )
        self.settings_icon_comboBox.setCurrentIndex(
            readme_settings_async("sidebar_management_window", "settings_icon")
        )
        self.settings_icon_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "sidebar_management_window",
                "settings_icon",
                self.settings_icon_comboBox.currentIndex(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_people_community_20_filled"),
            get_content_name_async(
                "sidebar_management_window", "roll_call_sidebar_position"
            ),
            get_content_description_async(
                "sidebar_management_window", "roll_call_sidebar_position"
            ),
            self.roll_call_sidebar_position_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_gift_20_filled"),
            get_content_name_async(
                "sidebar_management_window", "lottery_sidebar_position"
            ),
            get_content_description_async(
                "sidebar_management_window", "lottery_sidebar_position"
            ),
            self.lottery_sidebar_position_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_video_person_sparkle_20_filled"),
            get_content_name_async(
                "sidebar_management_window", "camera_preview_sidebar_position"
            ),
            get_content_description_async(
                "sidebar_management_window", "camera_preview_sidebar_position"
            ),
            self.camera_preview_sidebar_position_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_chat_history_20_filled"),
            get_content_name_async("sidebar_management_window", "main_window_history"),
            get_content_description_async(
                "sidebar_management_window", "main_window_history"
            ),
            self.main_window_history_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_settings_20_filled"),
            get_content_name_async("sidebar_management_window", "settings_icon"),
            get_content_description_async("sidebar_management_window", "settings_icon"),
            self.settings_icon_comboBox,
        )


class tray_management(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("tray_management", "title"))
        self.setBorderRadius(8)

        # 暂时显示/隐藏主界面 按钮开关
        self.show_hide_main_window_switch = SwitchButton(self)
        self.show_hide_main_window_switch.setOffText(
            get_content_switchbutton_name_async(
                "tray_management", "show_hide_main_window", "disable"
            )
        )
        self.show_hide_main_window_switch.setOnText(
            get_content_switchbutton_name_async(
                "tray_management", "show_hide_main_window", "enable"
            )
        )
        self.show_hide_main_window_switch.setChecked(
            readme_settings_async("tray_management", "show_hide_main_window")
        )
        self.show_hide_main_window_switch.checkedChanged.connect(
            lambda: update_settings(
                "tray_management",
                "show_hide_main_window",
                self.show_hide_main_window_switch.isChecked(),
            )
        )

        # 打开设置界面 按钮开关
        self.open_settings_switch = SwitchButton(self)
        self.open_settings_switch.setOffText(
            get_content_switchbutton_name_async(
                "tray_management", "open_settings", "disable"
            )
        )
        self.open_settings_switch.setOnText(
            get_content_switchbutton_name_async(
                "tray_management", "open_settings", "enable"
            )
        )
        self.open_settings_switch.setChecked(
            readme_settings_async("tray_management", "open_settings")
        )
        self.open_settings_switch.checkedChanged.connect(
            lambda: update_settings(
                "tray_management",
                "open_settings",
                self.open_settings_switch.isChecked(),
            )
        )

        # 暂时显示/隐藏浮窗 按钮开关
        self.show_hide_float_window_switch = SwitchButton(self)
        self.show_hide_float_window_switch.setOffText(
            get_content_switchbutton_name_async(
                "tray_management", "show_hide_float_window", "disable"
            )
        )
        self.show_hide_float_window_switch.setOnText(
            get_content_switchbutton_name_async(
                "tray_management", "show_hide_float_window", "enable"
            )
        )
        self.show_hide_float_window_switch.setChecked(
            readme_settings_async("tray_management", "show_hide_float_window")
        )
        self.show_hide_float_window_switch.checkedChanged.connect(
            lambda: update_settings(
                "tray_management",
                "show_hide_float_window",
                self.show_hide_float_window_switch.isChecked(),
            )
        )

        # 重启 按钮开关
        self.restart_switch = SwitchButton(self)
        self.restart_switch.setOffText(
            get_content_switchbutton_name_async("tray_management", "restart", "disable")
        )
        self.restart_switch.setOnText(
            get_content_switchbutton_name_async("tray_management", "restart", "enable")
        )
        self.restart_switch.setChecked(
            readme_settings_async("tray_management", "restart")
        )
        self.restart_switch.checkedChanged.connect(
            lambda: update_settings(
                "tray_management", "restart", self.restart_switch.isChecked()
            )
        )

        # 退出 按钮开关
        self.exit_switch = SwitchButton(self)
        self.exit_switch.setOffText(
            get_content_switchbutton_name_async("tray_management", "exit", "disable")
        )
        self.exit_switch.setOnText(
            get_content_switchbutton_name_async("tray_management", "exit", "enable")
        )
        self.exit_switch.setChecked(readme_settings_async("tray_management", "exit"))
        self.exit_switch.checkedChanged.connect(
            lambda: update_settings(
                "tray_management", "exit", self.exit_switch.isChecked()
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_window_text_20_filled"),
            get_content_name_async("tray_management", "show_hide_main_window"),
            get_content_description_async("tray_management", "show_hide_main_window"),
            self.show_hide_main_window_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_settings_20_filled"),
            get_content_name_async("tray_management", "open_settings"),
            get_content_description_async("tray_management", "open_settings"),
            self.open_settings_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_window_ad_20_filled"),
            get_content_name_async("tray_management", "show_hide_float_window"),
            get_content_description_async("tray_management", "show_hide_float_window"),
            self.show_hide_float_window_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async("tray_management", "restart"),
            get_content_description_async("tray_management", "restart"),
            self.restart_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_exit_20_filled"),
            get_content_name_async("tray_management", "exit"),
            get_content_description_async("tray_management", "exit"),
            self.exit_switch,
        )
