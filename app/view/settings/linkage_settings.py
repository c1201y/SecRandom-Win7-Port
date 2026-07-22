# ==================================================
# 导入库
# ==================================================
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
from app.Language.obtain_language import *
from app.common.extraction.extract import import_cses_schedule
from app.page_building.another_window import create_current_config_viewer_window

from app.common.extraction.cses_parser import CSESParser


# ==================================================
# 联动设置
# ==================================================
class linkage_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加数据源设置组件
        self.data_source_widget = data_source_settings(self)
        self.vBoxLayout.addWidget(self.data_source_widget)

        # 添加CSES导入组件
        self.cses_import_widget = cses_import_settings(self)
        self.vBoxLayout.addWidget(self.cses_import_widget)

        # 添加课间禁用设置组件
        self.class_break_widget = class_break_settings(self)
        self.vBoxLayout.addWidget(self.class_break_widget)

        # 添加课前重置设置组件
        self.pre_class_reset_widget = pre_class_reset_settings(self)
        self.vBoxLayout.addWidget(self.pre_class_reset_widget)

        # 添加科目历史记录过滤组件
        self.subject_history_filter_widget = subject_history_filter_settings(self)
        self.vBoxLayout.addWidget(self.subject_history_filter_widget)


class data_source_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("linkage_settings", "data_source_settings", "name")
        )
        self.setBorderRadius(8)

        # 数据源选择下拉框
        self.data_source_combo = ComboBox()
        self.data_source_combo.addItems(
            get_content_combo_name_async("linkage_settings", "data_source_function")
        )
        data_source = readme_settings_async("linkage_settings", "data_source")
        self.data_source_combo.setCurrentIndex(data_source)
        self.data_source_combo.currentIndexChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "data_source",
                self.data_source_combo.currentIndex(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_database_20_filled"),
            get_content_name_async("linkage_settings", "data_source_function"),
            get_content_description_async("linkage_settings", "data_source_function"),
            self.data_source_combo,
        )


class cses_import_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("linkage_settings", "cses_import_settings", "name")
        )
        self.setBorderRadius(8)

        # 导入文件按钮
        self.import_file_button = PushButton(
            get_content_name_async("linkage_settings", "import_from_file")
        )
        self.import_file_button.setIcon(
            get_theme_icon("ic_fluent_folder_open_20_filled")
        )
        self.import_file_button.clicked.connect(self.on_import_file_clicked)

        # 查看当前配置按钮
        self.view_current_config_button = PushButton(
            get_content_name_async("linkage_settings", "view_current_config")
        )
        self.view_current_config_button.setIcon(
            get_theme_icon("ic_fluent_document_20_filled")
        )
        self.view_current_config_button.clicked.connect(
            self.on_view_current_config_clicked
        )

        self.clear_cses_schedule_button = PushButton(
            get_content_name_async("linkage_settings", "clear_cses_schedule")
        )
        self.clear_cses_schedule_button.setIcon(
            get_theme_icon("ic_fluent_delete_20_filled")
        )
        self.clear_cses_schedule_button.clicked.connect(self.on_clear_cses_clicked)

        # 当前课程表信息标签
        self.schedule_info_label = BodyLabel(
            get_content_name_async("linkage_settings", "no_schedule_imported")
        )
        self._update_schedule_info()

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_file_button)
        button_layout.addWidget(self.view_current_config_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_cses_schedule_button)

        # 创建信息布局
        info_layout = QVBoxLayout()
        info_layout.addLayout(button_layout)
        info_layout.addWidget(self.schedule_info_label)

        # 创建容器控件来包含布局
        info_widget = QWidget()
        info_widget.setLayout(info_layout)

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_calendar_ltr_20_filled"),
            get_content_name_async("linkage_settings", "cses_import", "name"),
            get_content_name_async("linkage_settings", "cses_import", "description"),
            info_widget,
        )

    def _update_schedule_info(self):
        """更新课程表信息显示"""
        try:
            total_class_periods = 0

            # 检查data/CSES文件夹中是否有课程表文件
            cses_dir = get_data_path("CSES")
            if os.path.exists(cses_dir):
                cses_files = [
                    f for f in os.listdir(cses_dir) if f.endswith((".yaml", ".yml"))
                ]
                if cses_files:
                    # 解析每个课程表文件，计算总上课时间段
                    for file_name in cses_files:
                        file_path = os.path.join(cses_dir, file_name)
                        try:
                            parser = CSESParser()
                            if parser.load_from_file(file_path):
                                class_info = parser.get_class_info()
                                total_class_periods += len(class_info)
                        except Exception as e:
                            logger.error(f"解析文件{file_name}失败: {e}")

            # 判断是否有课程表数据
            if total_class_periods > 0:
                # 使用上课时间段数量
                count = total_class_periods

                self.schedule_info_label.setText(
                    get_content_name_async(
                        "linkage_settings", "schedule_imported"
                    ).format(count)
                )
            else:
                self.schedule_info_label.setText(
                    get_content_name_async("linkage_settings", "no_schedule_imported")
                )

        except Exception as e:
            logger.exception(f"更新课程表信息失败: {e}")
            self.schedule_info_label.setText("获取课程表信息失败")

    def on_clear_cses_clicked(self):
        try:
            cses_dir = get_data_path("CSES")
            try:
                ensure_dir(cses_dir)
            except Exception:
                pass

            deleted = 0
            if os.path.exists(cses_dir):
                for file_name in os.listdir(cses_dir):
                    if not file_name.endswith((".yaml", ".yml")):
                        continue
                    file_path = os.path.join(cses_dir, file_name)
                    try:
                        if remove_file(file_path):
                            deleted += 1
                    except Exception:
                        pass

            self._update_schedule_info()

            InfoBar.success(
                title=get_content_name_async("linkage_settings", "clear_cses_success"),
                content=get_content_name_async(
                    "linkage_settings", "clear_cses_success_content"
                ).format(deleted),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
        except Exception as e:
            logger.exception(f"清除CSES文件失败: {e}")
            InfoBar.error(
                title=get_content_name_async("linkage_settings", "clear_cses_failed"),
                content=get_content_name_async(
                    "linkage_settings", "clear_cses_failed_content"
                ).format(str(e)),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )

    def on_import_file_clicked(self):
        """当点击导入文件按钮时的处理"""
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_content_name_async("linkage_settings", "select_cses_file"),
            "",
            f"{get_content_name_async('linkage_settings', 'yaml_files')};;{get_content_name_async('linkage_settings', 'all_files')}",
        )

        if file_path:
            self._import_cses_file(file_path)

    def _import_cses_file(self, file_path: str):
        """导入CSES文件"""
        try:
            # 显示等待对话框
            self.import_file_button.setEnabled(False)
            self.import_file_button.setText(
                get_content_name_async("linkage_settings", "importing")
            )

            # 调用导入函数
            success, message = import_cses_schedule(file_path)

            if success:
                # 显示成功信息
                InfoBar.success(
                    title=get_content_name_async("linkage_settings", "import_success"),
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self,
                )

                # 更新课程表信息
                self._update_schedule_info()

            else:
                # 显示错误信息
                InfoBar.error(
                    title=get_content_name_async("linkage_settings", "import_failed"),
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self,
                )

        except Exception as e:
            logger.exception(f"导入CSES文件失败: {e}")
            import_error_msg = get_content_name_async(
                "linkage_settings", "import_error"
            )
            if "{}" in import_error_msg:
                error_content = import_error_msg.format(str(e))
            else:
                error_content = import_error_msg
            import_failed_title = get_content_name_async(
                "linkage_settings", "import_failed"
            )
            # 确保标题不包含意外的格式化占位符
            if "{}" in import_failed_title:
                import_failed_title = import_failed_title.format("")
            InfoBar.error(
                title=import_failed_title,
                content=error_content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )

        finally:
            # 恢复按钮状态
            self.import_file_button.setEnabled(True)
            self.import_file_button.setText(
                get_content_name_async("linkage_settings", "import_from_file")
            )

    def on_view_current_config_clicked(self):
        """当点击查看当前配置按钮时的处理"""
        try:
            # 使用独立窗口模板创建当前配置查看器
            create_current_config_viewer_window()

        except Exception as e:
            logger.exception(f"显示当前配置失败: {e}")
            InfoBar.error(
                title=get_content_name_async("linkage_settings", "import_failed"),
                content=f"无法显示当前配置: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )


class class_break_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("linkage_settings", "class_break_settings", "name")
        )
        self.setBorderRadius(8)

        # 课间禁用开关
        self.class_break_switch = SwitchButton()
        self.class_break_switch.setOffText(
            get_content_name_async("linkage_settings", "disable")
        )
        self.class_break_switch.setOnText(
            get_content_name_async("linkage_settings", "enable")
        )
        instant_draw_disable = readme_settings_async(
            "linkage_settings", "instant_draw_disable"
        )
        self.class_break_switch.setChecked(instant_draw_disable)
        self.class_break_switch.checkedChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "instant_draw_disable",
                self.class_break_switch.isChecked(),
            )
        )

        # 验证流程开关
        self.verification_switch = SwitchButton()
        self.verification_switch.setOffText(
            get_content_name_async("linkage_settings", "disable")
        )
        self.verification_switch.setOnText(
            get_content_name_async("linkage_settings", "enable")
        )
        verification_required = readme_settings_async(
            "linkage_settings", "verification_required"
        )
        self.verification_switch.setChecked(verification_required)
        self.verification_switch.checkedChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "verification_required",
                self.verification_switch.isChecked(),
            )
        )

        # 上课前提前解禁时间微调框
        self.pre_class_enable_spinbox = SpinBox()
        self.pre_class_enable_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.pre_class_enable_spinbox.setRange(0, 1440)
        self.pre_class_enable_spinbox.setSingleStep(1)
        self.pre_class_enable_spinbox.setSuffix(" s")
        pre_class_enable_time = readme_settings_async(
            "linkage_settings", "pre_class_enable_time"
        )
        self.pre_class_enable_spinbox.setValue(pre_class_enable_time)
        self.pre_class_enable_spinbox.valueChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "pre_class_enable_time",
                self.pre_class_enable_spinbox.value(),
            )
        )

        self.post_class_disable_delay_spinbox = SpinBox()
        self.post_class_disable_delay_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.post_class_disable_delay_spinbox.setRange(0, 1440)
        self.post_class_disable_delay_spinbox.setSingleStep(1)
        self.post_class_disable_delay_spinbox.setSuffix(" s")
        post_class_disable_delay = readme_settings_async(
            "linkage_settings", "post_class_disable_delay"
        )
        self.post_class_disable_delay_spinbox.setValue(post_class_disable_delay)
        self.post_class_disable_delay_spinbox.valueChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "post_class_disable_delay",
                self.post_class_disable_delay_spinbox.value(),
            )
        )

        # 下课隐藏浮窗开关
        self.hide_floating_on_class_end_switch = SwitchButton()
        self.hide_floating_on_class_end_switch.setOffText(
            get_content_name_async("linkage_settings", "disable")
        )
        self.hide_floating_on_class_end_switch.setOnText(
            get_content_name_async("linkage_settings", "enable")
        )
        hide_on_class_end = readme_settings_async(
            "linkage_settings", "hide_floating_window_on_class_end"
        )
        self.hide_floating_on_class_end_switch.setChecked(bool(hide_on_class_end))
        self.hide_floating_on_class_end_switch.checkedChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "hide_floating_window_on_class_end",
                self.hide_floating_on_class_end_switch.isChecked(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_clock_lock_20_filled"),
            get_content_name_async("linkage_settings", "class_break_function"),
            get_content_description_async("linkage_settings", "class_break_function"),
            self.class_break_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_shield_lock_20_filled"),
            get_content_name_async("linkage_settings", "verification_function"),
            get_content_description_async("linkage_settings", "verification_function"),
            self.verification_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async("linkage_settings", "pre_class_enable_time"),
            get_content_description_async("linkage_settings", "pre_class_enable_time"),
            self.pre_class_enable_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async("linkage_settings", "post_class_disable_delay"),
            get_content_description_async(
                "linkage_settings", "post_class_disable_delay"
            ),
            self.post_class_disable_delay_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_window_shield_20_filled"),
            get_content_name_async(
                "linkage_settings", "hide_floating_window_on_class_end"
            ),
            get_content_description_async(
                "linkage_settings", "hide_floating_window_on_class_end"
            ),
            self.hide_floating_on_class_end_switch,
        )


class pre_class_reset_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "linkage_settings", "pre_class_reset_settings", "name"
            )
        )
        self.setBorderRadius(8)

        # 课前重置开关
        self.pre_class_reset_switch = SwitchButton()
        self.pre_class_reset_switch.setOffText(
            get_content_name_async("linkage_settings", "disable")
        )
        self.pre_class_reset_switch.setOnText(
            get_content_name_async("linkage_settings", "enable")
        )
        pre_class_reset_enabled = readme_settings_async(
            "linkage_settings", "pre_class_reset_enabled"
        )
        self.pre_class_reset_switch.setChecked(pre_class_reset_enabled)
        self.pre_class_reset_switch.checkedChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "pre_class_reset_enabled",
                self.pre_class_reset_switch.isChecked(),
            )
        )

        # 课前重置时间微调框
        self.pre_class_reset_spinbox = SpinBox()
        self.pre_class_reset_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.pre_class_reset_spinbox.setRange(1, 1440)
        self.pre_class_reset_spinbox.setSingleStep(1)
        self.pre_class_reset_spinbox.setSuffix(" s")
        pre_class_reset_time = readme_settings_async(
            "linkage_settings", "pre_class_reset_time"
        )
        self.pre_class_reset_spinbox.setValue(pre_class_reset_time)
        self.pre_class_reset_spinbox.valueChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "pre_class_reset_time",
                self.pre_class_reset_spinbox.value(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async("linkage_settings", "pre_class_reset_function"),
            get_content_description_async(
                "linkage_settings", "pre_class_reset_function"
            ),
            self.pre_class_reset_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_clock_20_filled"),
            get_content_name_async("linkage_settings", "pre_class_reset_time"),
            get_content_description_async("linkage_settings", "pre_class_reset_time"),
            self.pre_class_reset_spinbox,
        )


class subject_history_filter_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async(
                "linkage_settings", "subject_history_filter_settings", "name"
            )
        )
        self.setBorderRadius(8)

        # 科目历史记录过滤开关
        self.subject_history_filter_switch = SwitchButton()
        self.subject_history_filter_switch.setOffText(
            get_content_name_async("linkage_settings", "disable")
        )
        self.subject_history_filter_switch.setOnText(
            get_content_name_async("linkage_settings", "enable")
        )
        subject_history_filter_enabled = readme_settings_async(
            "linkage_settings", "subject_history_filter_enabled"
        )
        self.subject_history_filter_switch.setChecked(subject_history_filter_enabled)
        self.subject_history_filter_switch.checkedChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "subject_history_filter_enabled",
                self.subject_history_filter_switch.isChecked(),
            )
        )

        self.break_subject_assignment_combo = ComboBox()
        self.break_subject_assignment_combo.setFixedWidth(WIDTH_SPINBOX)
        self.break_subject_assignment_combo.addItems(
            get_content_combo_name_async(
                "linkage_settings", "subject_history_break_assignment"
            )
        )
        self.break_subject_assignment_combo.setCurrentIndex(
            readme_settings_async(
                "linkage_settings", "subject_history_break_assignment"
            )
        )
        self.break_subject_assignment_combo.currentIndexChanged.connect(
            lambda: update_settings(
                "linkage_settings",
                "subject_history_break_assignment",
                self.break_subject_assignment_combo.currentIndex(),
            )
        )
        self.break_subject_assignment_combo.setEnabled(subject_history_filter_enabled)
        self.subject_history_filter_switch.checkedChanged.connect(
            lambda: self.break_subject_assignment_combo.setEnabled(
                self.subject_history_filter_switch.isChecked()
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_filter_20_filled"),
            get_content_name_async(
                "linkage_settings", "subject_history_filter_function"
            ),
            get_content_description_async(
                "linkage_settings", "subject_history_filter_function"
            ),
            self.subject_history_filter_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_filter_20_filled"),
            get_content_name_async(
                "linkage_settings", "subject_history_break_assignment"
            ),
            get_content_description_async(
                "linkage_settings", "subject_history_break_assignment"
            ),
            self.break_subject_assignment_combo,
        )
