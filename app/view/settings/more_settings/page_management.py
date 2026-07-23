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
from loguru import logger
import time
import weakref


# ==================================================
# 页面管理
# ==================================================
class page_management(QWidget):
    # 添加一个信号，当设置发生变化时发出
    settingsChanged = Signal(str, str, object)  # (group, key, value)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 延迟创建子组件：先插入占位容器并注册创建工厂，避免一次性阻塞
        self._deferred_factories = {}
        # 使用弱引用来跟踪自身，避免循环引用
        self._self_ref = weakref.ref(self)

        def make_placeholder(attr_name: str):
            w = QWidget()
            w.setObjectName(attr_name)
            layout = QVBoxLayout(w)
            layout.setContentsMargins(0, 0, 0, 0)
            self.vBoxLayout.addWidget(w)
            return w

        # create placeholders
        self.page_management_roll_call = make_placeholder("page_management_roll_call")
        self._deferred_factories["page_management_roll_call"] = (
            lambda parent=self: page_management_roll_call(parent)
        )

        self.page_management_lottery = make_placeholder("page_management_lottery")
        self._deferred_factories["page_management_lottery"] = (
            lambda parent=self: page_management_lottery(parent)
        )

        # 分批异步创建真实子组件，间隔以减少主线程瞬时负载
        try:
            for i, name in enumerate(list(self._deferred_factories.keys())):
                # 使用QTimer.singleShot创建定时器
                QTimer.singleShot(150 * i, lambda n=name: self._safe_create_deferred(n))
        except Exception as e:
            logger.exception(f"调度延迟创建子组件失败: {e}")

    def _safe_create_deferred(self, name: str):
        """安全地创建延迟注册的子组件，使用弱引用避免访问已销毁的对象"""
        try:
            # 使用弱引用检查对象是否仍然有效
            self_ref = getattr(self, "_self_ref", None)
            if self_ref is None or self_ref() is None:
                logger.debug(f"对象已销毁，取消创建子组件 {name}")
                return

            # 检查布局是否存在
            if not hasattr(self, "vBoxLayout") or not self.vBoxLayout:
                return

            self._create_deferred(name)
        except RuntimeError as e:
            if "already deleted" in str(e):
                logger.debug(f"对象已销毁，取消创建子组件 {name}")
                return
            else:
                logger.exception(f"创建子组件 {name} 时发生运行时错误: {e}")
                return
        except Exception as e:
            logger.exception(f"创建子组件 {name} 时发生未知错误: {e}")
            return

    def _create_deferred(self, name: str):
        """按需创建延迟注册的子组件并替换占位容器"""
        # 更严格的防护：在 factory 调用前后都检查父对象与占位状态
        factories = getattr(self, "_deferred_factories", {})
        if name not in factories:
            return

        # 尝试从 factories 中弹出 factory，若并发已移除则安全返回
        try:
            factory = factories.pop(name)
        except Exception:
            return

        # 快速检查当前窗口对象是否还存在（避免在被销毁时创建）
        self_ref = getattr(self, "_self_ref", None)
        if self_ref is None or self_ref() is None:
            return

        # 创建真实 widget 的过程可能在这段时间父对象被销毁，保护 factory 调用
        try:
            start = time.perf_counter()
            real_widget = factory()
            elapsed = time.perf_counter() - start
        except Exception as e:
            logger.exception(f"创建子组件 {name} 失败: {e}")
            return

        # 再次检查对象是否仍然有效
        if self_ref is None or self_ref() is None:
            # 如果对象已经销毁，则立即清理新创建的组件
            if "real_widget" in locals():
                real_widget.deleteLater()
            return

        # 获取占位容器
        placeholder = getattr(self, name, None)

        # 如果没有占位符，直接添加到主布局
        if placeholder is None:
            try:
                # 检查self是否仍然有效
                if self_ref is None or self_ref() is None:
                    if "real_widget" in locals():
                        real_widget.deleteLater()
                    return
                self.vBoxLayout.addWidget(real_widget)
                setattr(self, name, real_widget)
                logger.debug(f"延迟创建子组件 {name} 耗时: {elapsed:.3f}s")
            except RuntimeError as e:
                logger.exception(f"将子组件 {name} 插入主布局失败: {e}")
            return

        # 尝试获取占位符的布局
        layout = None
        try:
            layout = placeholder.layout()
        except Exception:
            pass

        # 如果有布局，添加到布局中
        if layout is not None:
            try:
                # 检查widget是否仍然有效
                if self_ref is None or self_ref() is None:
                    if "real_widget" in locals():
                        real_widget.deleteLater()
                    return
                layout.addWidget(real_widget)
                setattr(self, name, real_widget)
                logger.debug(f"延迟创建子组件 {name} 耗时: {elapsed:.3f}s")
            except RuntimeError as e:
                logger.exception(f"绑定子组件 {name} 到占位容器失败: {e}")
        else:
            # 没有布局，尝试替换占位符
            try:
                index = -1
                for i in range(self.vBoxLayout.count()):
                    item = self.vBoxLayout.itemAt(i)
                    if item and item.widget() is placeholder:
                        index = i
                        break

                if index >= 0:
                    # 移除占位并在同位置插入真实 widget
                    item = self.vBoxLayout.takeAt(index)
                    widget = item.widget() if item else None
                    if widget is not None:
                        widget.deleteLater()
                    self.vBoxLayout.insertWidget(index, real_widget)
                    setattr(self, name, real_widget)
                    logger.debug(f"延迟创建子组件 {name} 耗时: {elapsed:.3f}s")
                else:
                    # 未找到占位，回退到追加
                    self.vBoxLayout.addWidget(real_widget)
                    setattr(self, name, real_widget)
                    logger.debug(f"延迟创建子组件 {name} 耗时: {elapsed:.3f}s")
            except RuntimeError as e:
                logger.exception(f"替换占位 {name} 失败: {e}")


class page_management_roll_call(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setTitle(get_content_name_async("page_management", "roll_call"))
        self.setBorderRadius(8)

        # 点名控制面板位置下拉框
        self.roll_call_method_combo = ComboBox()
        self.roll_call_method_combo.addItems(
            get_content_combo_name_async("page_management", "roll_call_method")
        )
        self.roll_call_method_combo.setCurrentIndex(
            readme_settings_async("page_management", "roll_call_method")
        )
        self.roll_call_method_combo.currentIndexChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_method",
                self.roll_call_method_combo.currentIndex(),
            )
        )

        # 重置已抽取名单按钮是否显示开关
        self.roll_call_reset_button_switch = SwitchButton()
        self.roll_call_reset_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_reset_button", "disable"
            )
        )
        self.roll_call_reset_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_reset_button", "enable"
            )
        )
        self.roll_call_reset_button_switch.setChecked(
            readme_settings_async("page_management", "roll_call_reset_button")
        )
        self.roll_call_reset_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_reset_button",
                self.roll_call_reset_button_switch.isChecked(),
            )
        )

        # 增加/减少抽取数量控制条是否显示开关
        self.roll_call_quantity_control_switch = SwitchButton()
        self.roll_call_quantity_control_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_quantity_control", "disable"
            )
        )
        self.roll_call_quantity_control_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_quantity_control", "enable"
            )
        )
        self.roll_call_quantity_control_switch.setChecked(
            readme_settings_async("page_management", "roll_call_quantity_control")
        )
        self.roll_call_quantity_control_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_quantity_control",
                self.roll_call_quantity_control_switch.isChecked(),
            )
        )

        # 开始按钮是否显示开关
        self.roll_call_start_button_switch = SwitchButton()
        self.roll_call_start_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_start_button", "disable"
            )
        )
        self.roll_call_start_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_start_button", "enable"
            )
        )
        self.roll_call_start_button_switch.setChecked(
            readme_settings_async("page_management", "roll_call_start_button")
        )
        self.roll_call_start_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_start_button",
                self.roll_call_start_button_switch.isChecked(),
            )
        )

        # 名单切换下拉框是否显示开关
        self.roll_call_list_combo_switch = SwitchButton()
        self.roll_call_list_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_list", "disable"
            )
        )
        self.roll_call_list_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_list", "enable"
            )
        )
        self.roll_call_list_combo_switch.setChecked(
            readme_settings_async("page_management", "roll_call_list")
        )
        self.roll_call_list_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_list",
                self.roll_call_list_combo_switch.isChecked(),
            )
        )

        # 抽取范围下拉框是否显示开关
        self.roll_call_range_combo_switch = SwitchButton()
        self.roll_call_range_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_range", "disable"
            )
        )
        self.roll_call_range_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_range", "enable"
            )
        )
        self.roll_call_range_combo_switch.setChecked(
            readme_settings_async("page_management", "roll_call_range")
        )
        self.roll_call_range_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_range",
                self.roll_call_range_combo_switch.isChecked(),
            )
        )

        # 抽取性别下拉框是否显示开关
        self.roll_call_gender_combo_switch = SwitchButton()
        self.roll_call_gender_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_gender", "disable"
            )
        )
        self.roll_call_gender_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_gender", "enable"
            )
        )
        self.roll_call_gender_combo_switch.setChecked(
            readme_settings_async("page_management", "roll_call_gender")
        )
        self.roll_call_gender_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_gender",
                self.roll_call_gender_combo_switch.isChecked(),
            )
        )

        # 班级人数/组数标签显示方式下拉框
        self.roll_call_quantity_label_combo = ComboBox()
        self.roll_call_quantity_label_combo.addItems(
            get_content_combo_name_async("page_management", "roll_call_quantity_label")
        )
        self.roll_call_quantity_label_combo.setCurrentIndex(
            readme_settings_async("page_management", "roll_call_quantity_label")
        )
        self.roll_call_quantity_label_combo.currentIndexChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_quantity_label",
                self.roll_call_quantity_label_combo.currentIndex(),
            )
        )

        # 查看剩余名单按钮是否显示开关
        self.roll_call_remaining_button_switch = SwitchButton()
        self.roll_call_remaining_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_remaining_button", "disable"
            )
        )
        self.roll_call_remaining_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "roll_call_remaining_button", "enable"
            )
        )
        self.roll_call_remaining_button_switch.setChecked(
            readme_settings_async("page_management", "roll_call_remaining_button")
        )
        self.roll_call_remaining_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "roll_call_remaining_button",
                self.roll_call_remaining_button_switch.isChecked(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_window_multiple_swap_20_filled"),
            get_content_name_async("page_management", "roll_call_method"),
            get_content_description_async("page_management", "roll_call_method"),
            self.roll_call_method_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async("page_management", "roll_call_reset_button"),
            get_content_description_async("page_management", "roll_call_reset_button"),
            self.roll_call_reset_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_autofit_content_20_filled"),
            get_content_name_async("page_management", "roll_call_quantity_control"),
            get_content_description_async(
                "page_management", "roll_call_quantity_control"
            ),
            self.roll_call_quantity_control_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_play_20_filled"),
            get_content_name_async("page_management", "roll_call_start_button"),
            get_content_description_async("page_management", "roll_call_start_button"),
            self.roll_call_start_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_notepad_person_20_filled"),
            get_content_name_async("page_management", "roll_call_list"),
            get_content_description_async("page_management", "roll_call_list"),
            self.roll_call_list_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_convert_range_20_filled"),
            get_content_name_async("page_management", "roll_call_range"),
            get_content_description_async("page_management", "roll_call_range"),
            self.roll_call_range_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_video_person_sparkle_20_filled"),
            get_content_name_async("page_management", "roll_call_gender"),
            get_content_description_async("page_management", "roll_call_gender"),
            self.roll_call_gender_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_people_list_20_filled"),
            get_content_name_async("page_management", "roll_call_remaining_button"),
            get_content_description_async(
                "page_management", "roll_call_remaining_button"
            ),
            self.roll_call_remaining_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_text_person_20_filled"),
            get_content_name_async("page_management", "roll_call_quantity_label"),
            get_content_description_async(
                "page_management", "roll_call_quantity_label"
            ),
            self.roll_call_quantity_label_combo,
        )

    def _update_settings_and_notify(self, group, key, value):
        """更新设置并通知父组件"""
        update_settings(group, key, value)
        if hasattr(self.parent, "settingsChanged"):
            self.parent.settingsChanged.emit(group, key, value)


class page_management_lottery(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setTitle(get_content_name_async("page_management", "lottery"))
        self.setBorderRadius(8)

        # 抽奖控制面板位置下拉框
        self.lottery_method_combo = ComboBox()
        self.lottery_method_combo.addItems(
            get_content_combo_name_async("page_management", "lottery_method")
        )
        self.lottery_method_combo.setCurrentIndex(
            readme_settings_async("page_management", "lottery_method")
        )
        self.lottery_method_combo.currentIndexChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_method",
                self.lottery_method_combo.currentIndex(),
            )
        )

        # 重置已抽取名单按钮是否显示开关
        self.lottery_reset_button_button_switch = SwitchButton()
        self.lottery_reset_button_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_reset_button", "disable"
            )
        )
        self.lottery_reset_button_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_reset_button", "enable"
            )
        )
        self.lottery_reset_button_button_switch.setChecked(
            readme_settings_async("page_management", "lottery_reset_button")
        )
        self.lottery_reset_button_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_reset_button",
                self.lottery_reset_button_button_switch.isChecked(),
            )
        )

        # 增加/减少抽取数量控制条是否显示开关
        self.lottery_quantity_control_switch = SwitchButton()
        self.lottery_quantity_control_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_quantity_control", "disable"
            )
        )
        self.lottery_quantity_control_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_quantity_control", "enable"
            )
        )
        self.lottery_quantity_control_switch.setChecked(
            readme_settings_async("page_management", "lottery_quantity_control")
        )
        self.lottery_quantity_control_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_quantity_control",
                self.lottery_quantity_control_switch.isChecked(),
            )
        )

        # 开始按钮是否显示开关
        self.lottery_start_button_switch = SwitchButton()
        self.lottery_start_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_start_button", "disable"
            )
        )
        self.lottery_start_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_start_button", "enable"
            )
        )
        self.lottery_start_button_switch.setChecked(
            readme_settings_async("page_management", "lottery_start_button")
        )
        self.lottery_start_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_start_button",
                self.lottery_start_button_switch.isChecked(),
            )
        )

        # 名单切换下拉框是否显示开关
        self.lottery_list_combo_switch = SwitchButton()
        self.lottery_list_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_list", "disable"
            )
        )
        self.lottery_list_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_list", "enable"
            )
        )
        self.lottery_list_combo_switch.setChecked(
            readme_settings_async("page_management", "lottery_list")
        )
        self.lottery_list_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_list",
                self.lottery_list_combo_switch.isChecked(),
            )
        )

        # 名单切换下拉框是否显示开关
        self.lottery_roll_call_list_combo_switch = SwitchButton()
        self.lottery_roll_call_list_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_list", "disable"
            )
        )
        self.lottery_roll_call_list_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_list", "enable"
            )
        )
        self.lottery_roll_call_list_combo_switch.setChecked(
            readme_settings_async("page_management", "lottery_roll_call_list")
        )
        self.lottery_roll_call_list_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_roll_call_list",
                self.lottery_roll_call_list_combo_switch.isChecked(),
            )
        )

        # 抽取范围下拉框是否显示开关
        self.lottery_roll_call_range_combo_switch = SwitchButton()
        self.lottery_roll_call_range_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_range", "disable"
            )
        )
        self.lottery_roll_call_range_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_range", "enable"
            )
        )
        self.lottery_roll_call_range_combo_switch.setChecked(
            readme_settings_async("page_management", "lottery_roll_call_range")
        )
        self.lottery_roll_call_range_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_roll_call_range",
                self.lottery_roll_call_range_combo_switch.isChecked(),
            )
        )

        # 抽取性别下拉框是否显示开关
        self.lottery_roll_call_gender_combo_switch = SwitchButton()
        self.lottery_roll_call_gender_combo_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_gender", "disable"
            )
        )
        self.lottery_roll_call_gender_combo_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_roll_call_gender", "enable"
            )
        )
        self.lottery_roll_call_gender_combo_switch.setChecked(
            readme_settings_async("page_management", "lottery_roll_call_gender")
        )
        self.lottery_roll_call_gender_combo_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_roll_call_gender",
                self.lottery_roll_call_gender_combo_switch.isChecked(),
            )
        )

        # 奖品数量标签显示方式下拉框
        self.lottery_quantity_label_combo = ComboBox()
        self.lottery_quantity_label_combo.addItems(
            get_content_combo_name_async("page_management", "lottery_quantity_label")
        )
        self.lottery_quantity_label_combo.setCurrentIndex(
            readme_settings_async("page_management", "lottery_quantity_label")
        )
        self.lottery_quantity_label_combo.currentIndexChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_quantity_label",
                self.lottery_quantity_label_combo.currentIndex(),
            )
        )

        # 查看剩余名单按钮是否显示开关
        self.lottery_remaining_button_switch = SwitchButton()
        self.lottery_remaining_button_switch.setOffText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_remaining_button", "disable"
            )
        )
        self.lottery_remaining_button_switch.setOnText(
            get_content_switchbutton_name_async(
                "page_management", "lottery_remaining_button", "enable"
            )
        )
        self.lottery_remaining_button_switch.setChecked(
            readme_settings_async("page_management", "lottery_remaining_button")
        )
        self.lottery_remaining_button_switch.checkedChanged.connect(
            lambda: self._update_settings_and_notify(
                "page_management",
                "lottery_remaining_button",
                self.lottery_remaining_button_switch.isChecked(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_window_multiple_swap_20_filled"),
            get_content_name_async("page_management", "lottery_method"),
            get_content_description_async("page_management", "lottery_method"),
            self.lottery_method_combo,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async("page_management", "lottery_reset_button"),
            get_content_description_async("page_management", "lottery_reset_button"),
            self.lottery_reset_button_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_autofit_content_20_filled"),
            get_content_name_async("page_management", "lottery_quantity_control"),
            get_content_description_async(
                "page_management", "lottery_quantity_control"
            ),
            self.lottery_quantity_control_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_play_20_filled"),
            get_content_name_async("page_management", "lottery_start_button"),
            get_content_description_async("page_management", "lottery_start_button"),
            self.lottery_start_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_notepad_person_20_filled"),
            get_content_name_async("page_management", "lottery_list"),
            get_content_description_async("page_management", "lottery_list"),
            self.lottery_list_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_notepad_person_20_filled"),
            get_content_name_async("page_management", "roll_call_list"),
            get_content_description_async("page_management", "roll_call_list"),
            self.lottery_roll_call_list_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_convert_range_20_filled"),
            get_content_name_async("page_management", "roll_call_range"),
            get_content_description_async("page_management", "roll_call_range"),
            self.lottery_roll_call_range_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_video_person_sparkle_20_filled"),
            get_content_name_async("page_management", "roll_call_gender"),
            get_content_description_async("page_management", "roll_call_gender"),
            self.lottery_roll_call_gender_combo_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_people_list_20_filled"),
            get_content_name_async("page_management", "lottery_remaining_button"),
            get_content_description_async(
                "page_management", "lottery_remaining_button"
            ),
            self.lottery_remaining_button_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_slide_text_person_20_filled"),
            get_content_name_async("page_management", "lottery_quantity_label"),
            get_content_description_async("page_management", "lottery_quantity_label"),
            self.lottery_quantity_label_combo,
        )

    def _update_settings_and_notify(self, group, key, value):
        """更新设置并通知父组件"""
        update_settings(group, key, value)
        if hasattr(self.parent, "settingsChanged"):
            self.parent.settingsChanged.emit(group, key, value)
