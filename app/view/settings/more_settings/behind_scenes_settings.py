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
from app.common.data.list import *
from app.common.safety.secure_store import (
    read_behind_scenes_settings,
    write_behind_scenes_settings,
)
from app.common.behind_scenes.behind_scenes_utils import BehindScenesUtils
from app.view.settings.list_management.shared_file_watcher import (
    get_shared_file_watcher,
)


# ==================================================
# 后台加载工作线程
# ==================================================
class LoadDataWorker(QThread):
    """后台加载数据的工作线程"""

    finished = Signal(object, object, object)  # students, prob_data, prize_list

    def __init__(self, list_name, mode, pool_name=None):
        super().__init__()
        self.list_name = list_name
        self.mode = mode
        self.pool_name = pool_name

    def run(self):
        """在后台线程中执行数据加载"""
        try:
            # 加载学生列表
            students = get_student_list(self.list_name)

            # 加载概率设置数据
            prob_data = read_behind_scenes_settings()
            if not prob_data or not isinstance(prob_data, dict):
                prob_data = {}

            # 清除横幅点击次数
            if prob_data.get("banner_click_count", 0) > 0:
                prob_data["banner_click_count"] = 0
                write_behind_scenes_settings(prob_data)

            # 如果是抽奖模式，加载奖品列表
            prize_list = []
            if self.mode == 1 and self.pool_name:
                try:
                    prizes = get_pool_list(self.pool_name)
                    prize_list = [
                        p.get("name", "") for p in prizes if p.get("exist", True)
                    ]
                except Exception as e:
                    logger.exception(f"获取奖品列表失败: {e}")

            self.finished.emit(students, prob_data, prize_list)
        except Exception as e:
            logger.exception(f"后台加载数据失败: {e}")
            self.finished.emit([], {}, [])


# ==================================================
# 概率设置
# ==================================================
class behind_scenes_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加内幕设置表格组件
        self.behind_scenes_settings_widget = behind_scenes_settings_table(self)
        self.vBoxLayout.addWidget(self.behind_scenes_settings_widget)


class behind_scenes_settings_table(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("behind_scenes_settings", "title"))
        self.setBorderRadius(8)

        # 初始化数据
        self.current_list_name = ""
        self.current_class_name = ""
        self.current_mode = 0  # 0: 点名, 1: 抽奖
        self.probability_data = {}

        # 创建模式选择区域
        QTimer.singleShot(APPLY_DELAY, self.create_class_selection)

        # 创建表格区域
        QTimer.singleShot(APPLY_DELAY, self.create_table)

        # 初始化名单列表
        QTimer.singleShot(APPLY_DELAY, self.init_list_data)

        # 设置文件系统监视器
        QTimer.singleShot(APPLY_DELAY, self.setup_file_watcher)

        # 初始化数据
        QTimer.singleShot(APPLY_DELAY, self.refresh_data)

    def create_class_selection(self):
        """创建班级选择区域"""
        self.enabled_global_switch = SwitchButton()
        self.enabled_global_switch.setOffText(
            get_content_switchbutton_name_async(
                "behind_scenes_settings", "enabled_global", "disable"
            )
        )
        self.enabled_global_switch.setOnText(
            get_content_switchbutton_name_async(
                "behind_scenes_settings", "enabled_global", "enable"
            )
        )
        self.enabled_global_switch.setChecked(self._get_enabled_global_value())
        self.enabled_global_switch.checkedChanged.connect(
            self.on_enabled_global_changed
        )

        # 模式选择（点名/抽奖）
        self.mode_comboBox = ComboBox()
        self.mode_comboBox.addItems(
            get_content_combo_name_async("behind_scenes_settings", "mode_options")
        )
        self.mode_comboBox.setCurrentIndex(0)
        self.mode_comboBox.currentIndexChanged.connect(self.on_mode_changed)

        # 名单选择（班级/奖池）
        self.list_comboBox = ComboBox()
        # 初始填充班级列表
        class_list = get_class_name_list()
        self.list_comboBox.addItems(class_list)
        if class_list:
            self.list_comboBox.setCurrentIndex(0)
            self.current_list_name = class_list[0]
        else:
            self.list_comboBox.setPlaceholderText(
                get_content_name_async("behind_scenes_settings", "select_class_name")
            )
            self.current_list_name = ""
        self.list_comboBox.currentIndexChanged.connect(self.on_list_changed)

        # 奖池选择（抽奖模式专用）
        self.pool_comboBox = ComboBox()
        self.pool_comboBox.setVisible(False)
        self.pool_comboBox.currentIndexChanged.connect(self.refresh_data)

        self.addGroup(
            get_theme_icon("ic_fluent_power_20_filled"),
            get_content_name_async("behind_scenes_settings", "enabled_global"),
            get_content_description_async("behind_scenes_settings", "enabled_global"),
            self.enabled_global_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_lottery_20_filled"),
            get_content_name_async("behind_scenes_settings", "select_mode"),
            get_content_description_async("behind_scenes_settings", "select_mode"),
            self.mode_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_class_20_filled"),
            get_content_name_async("behind_scenes_settings", "select_list"),
            get_content_description_async("behind_scenes_settings", "select_list"),
            self.list_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_gift_20_filled"),
            get_content_name_async("behind_scenes_settings", "select_pool_name"),
            get_content_description_async("behind_scenes_settings", "select_pool_name"),
            self.pool_comboBox,
        )

    def _get_enabled_global_value(self) -> bool:
        try:
            settings = read_behind_scenes_settings()
            if not settings or not isinstance(settings, dict):
                return True
            return bool(settings.get("enabled_global", True))
        except Exception:
            return True

    def on_enabled_global_changed(self):
        try:
            settings = read_behind_scenes_settings()
            if not settings or not isinstance(settings, dict):
                settings = {}
            settings["enabled_global"] = bool(self.enabled_global_switch.isChecked())
            write_behind_scenes_settings(settings)
            BehindScenesUtils.clear_cache()
        except Exception as e:
            logger.exception(f"保存内幕总开关失败: {e}")

    def on_mode_changed(self):
        """当模式改变时，更新名单下拉框"""
        mode = self.mode_comboBox.currentIndex()
        self.current_mode = mode

        # 清空名单下拉框
        self.list_comboBox.clear()
        self.pool_comboBox.clear()

        if mode == 0:
            # 点名模式：显示班级列表，隐藏奖池选择和奖品列
            self.pool_comboBox.setVisible(False)
            self.table.setColumnHidden(3, True)  # 隐藏奖品列

            class_list = get_class_name_list()
            self.list_comboBox.addItems(class_list)
            # 设置默认选择
            if class_list:
                self.list_comboBox.setCurrentIndex(0)
                self.current_list_name = class_list[0]
            else:
                self.list_comboBox.setPlaceholderText(
                    get_content_name_async(
                        "behind_scenes_settings", "select_class_name"
                    )
                )
                self.list_comboBox.setCurrentIndex(-1)
                self.current_list_name = ""
        else:
            # 抽奖模式：显示班级列表和奖池列表，显示奖品列
            self.pool_comboBox.setVisible(True)
            self.table.setColumnHidden(3, False)  # 显示奖品列

            # 填充班级列表（用于选择学生）
            class_list = get_class_name_list()
            self.list_comboBox.addItems(class_list)
            if class_list:
                self.list_comboBox.setCurrentIndex(0)
                self.current_class_name = class_list[0]
            else:
                self.list_comboBox.setPlaceholderText(
                    get_content_name_async(
                        "behind_scenes_settings", "select_class_name"
                    )
                )
                self.list_comboBox.setCurrentIndex(-1)
                self.current_class_name = ""

            # 填充奖池列表（用于选择奖品）
            pool_list = get_pool_name_list()
            self.pool_comboBox.addItems(pool_list)
            if pool_list:
                self.pool_comboBox.setCurrentIndex(0)
                self.current_list_name = pool_list[0]
            else:
                self.pool_comboBox.setPlaceholderText(
                    get_content_name_async("behind_scenes_settings", "select_pool_name")
                )
                self.pool_comboBox.setCurrentIndex(-1)
                self.current_list_name = ""

        # 刷新表格数据
        self.refresh_data()

    def on_list_changed(self):
        """当班级选择改变时"""
        if self.current_mode == 0:
            # 点名模式：更新班级名称
            self.current_list_name = self.list_comboBox.currentText()
        else:
            # 抽奖模式：更新班级名称（用于选择学生）
            self.current_class_name = self.list_comboBox.currentText()

        # 刷新表格数据
        self.refresh_data()

    def init_list_data(self):
        """初始化名单数据"""
        # 根据当前模式加载对应的名单
        self.on_mode_changed()

    def create_table(self):
        """创建表格区域"""
        # 创建表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()

        # 设置表格头
        headers = [
            get_content_name_async("behind_scenes_settings", "enabled"),
            get_content_name_async("behind_scenes_settings", "id"),
            get_content_name_async("behind_scenes_settings", "name"),
            get_content_name_async("behind_scenes_settings", "prize"),
            get_content_name_async("behind_scenes_settings", "probability"),
        ]
        self.table.setHorizontalHeaderLabels(headers)

        # 初始隐藏奖品列（点名模式下）
        self.table.setColumnHidden(3, True)

        # 设置表格属性
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().resizeSection(0, 80)
        for i in range(1, 5):
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )
        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

        # 连接单元格修改信号
        self.table.cellChanged.connect(self.save_table_data)

        self.layout().addWidget(self.table)

    def setup_file_watcher(self):
        """设置文件系统监视器，监控班级名单和奖池名单文件夹的变化"""
        roll_call_list_dir = get_data_path("list", "roll_call_list")
        lottery_list_dir = get_data_path("list", "lottery_list")

        if not roll_call_list_dir.exists():
            logger.warning(f"班级名单文件夹不存在: {roll_call_list_dir}")

        if not lottery_list_dir.exists():
            logger.warning(f"奖池名单文件夹不存在: {lottery_list_dir}")

        self._shared_watcher = get_shared_file_watcher()

        if roll_call_list_dir.exists():
            self._shared_watcher.add_watcher(
                str(roll_call_list_dir), self.on_directory_changed
            )

        if lottery_list_dir.exists():
            self._shared_watcher.add_watcher(
                str(lottery_list_dir), self.on_directory_changed
            )

    def on_directory_changed(self, path):
        """当目录内容发生变化时调用此方法"""
        QTimer.singleShot(1000, self.refresh_list)

    def refresh_list(self):
        """刷新名单下拉框列表"""
        if not hasattr(self, "list_comboBox") or self.list_comboBox is None:
            return

        try:
            # 保存当前选择的名单名称和索引
            current_list_name = self.list_comboBox.currentText()
            current_index = self.list_comboBox.currentIndex()

            # 根据当前模式获取对应的列表
            if self.current_mode == 0:
                # 点名模式：获取班级列表
                list_data = get_class_name_list()
            else:
                # 抽奖模式：获取奖池列表
                list_data = get_pool_name_list()

            # 清空并重新填充下拉框
            self.list_comboBox.clear()
            self.list_comboBox.addItems(list_data)

            # 如果之前选择的名单还在列表中，则重新选择它
            if current_list_name and current_list_name in list_data:
                index = list_data.index(current_list_name)
                self.list_comboBox.setCurrentIndex(index)
                self.current_list_name = current_list_name
            elif list_data and current_index >= 0 and current_index < len(list_data):
                # 如果之前选择的索引仍然有效，使用相同的索引
                self.list_comboBox.setCurrentIndex(current_index)
                self.current_list_name = list_data[current_index]
            elif list_data:
                # 如果之前选择的名单不在列表中，选择第一个
                self.list_comboBox.setCurrentIndex(0)
                self.current_list_name = list_data[0]
            else:
                # 如果没有名单，设置占位符
                self.list_comboBox.setCurrentIndex(-1)
                if self.current_mode == 0:
                    self.list_comboBox.setPlaceholderText(
                        get_content_name_async(
                            "behind_scenes_settings", "select_class_name"
                        )
                    )
                else:
                    self.list_comboBox.setPlaceholderText(
                        get_content_name_async(
                            "behind_scenes_settings", "select_pool_name"
                        )
                    )
                self.current_list_name = ""

            # 刷新表格数据
            if hasattr(self, "table") and self.table is not None:
                self.refresh_data()
        except RuntimeError as e:
            logger.exception(f"刷新名单列表时发生错误: {e}")
        except Exception as e:
            logger.exception(f"刷新名单列表时发生未知错误: {e}")

    def refresh_data(self):
        """刷新表格数据"""
        if not hasattr(self, "table") or self.table is None:
            return

        if not hasattr(self, "list_comboBox") or self.list_comboBox is None:
            return

        if self.current_mode == 1 and (
            not hasattr(self, "pool_comboBox") or self.pool_comboBox is None
        ):
            return

        try:
            list_name = self.list_comboBox.currentText()
        except RuntimeError:
            logger.exception("名单下拉框已被销毁")
            return

        if not list_name:
            self.table.setRowCount(0)
            return

        self.current_list_name = list_name
        self.current_mode = self.mode_comboBox.currentIndex()

        # 停止之前的加载线程（如果存在）
        if hasattr(self, "load_worker") and self.load_worker is not None:
            if self.load_worker.isRunning():
                self.load_worker.quit()
                self.load_worker.wait()
            self.load_worker.deleteLater()

        # 使用后台线程加载数据，避免界面卡顿
        pool_name = self.pool_comboBox.currentText() if self.current_mode == 1 else None
        self.load_worker = LoadDataWorker(list_name, self.current_mode, pool_name)
        self.load_worker.finished.connect(self.on_data_loaded)
        self.load_worker.start()

    def on_data_loaded(self, students, prob_data, prize_list):
        """数据加载完成后的回调"""
        try:
            self.probability_data = prob_data

            # 临时阻止信号，避免初始化时触发保存操作
            self.table.blockSignals(True)

            # 两种模式都显示学生数据
            if not students or students is None:
                self.table.setRowCount(0)
                self.table.blockSignals(False)
                return

            self.table.setRowCount(len(students))

            for row, student in enumerate(students):
                student_name = student.get("name", "")
                student_id = student.get("id", row + 1)

                # 启用勾选框
                checkbox_item = QTableWidgetItem()
                prob_data_item = self.probability_data.get(student_name, {})

                if self.current_mode == 0:
                    # 点名模式
                    is_enabled = prob_data_item.get("roll_call", {}).get(
                        "enabled", False
                    )
                else:
                    # 抽奖模式
                    pool_name = self.pool_comboBox.currentText()
                    lottery_settings = prob_data_item.get("lottery", {})
                    if pool_name in lottery_settings:
                        is_enabled = lottery_settings[pool_name].get("enabled", False)
                    else:
                        is_enabled = False

                checkbox_item.setCheckState(
                    Qt.CheckState.Checked if is_enabled else Qt.CheckState.Unchecked
                )
                checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, checkbox_item)

                # 学号
                id_item = QTableWidgetItem(str(student_id))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, id_item)

                # 姓名
                name_item = QTableWidgetItem(student_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, name_item)

                # 奖品（仅抽奖模式）
                if self.current_mode == 1:
                    # 抽奖模式：显示奖品下拉框
                    pool_name = self.pool_comboBox.currentText()
                    prize_combobox = ComboBox()
                    prize_combobox.setPlaceholderText(
                        get_content_name_async(
                            "behind_scenes_settings", "select_pool_name"
                        )
                    )

                    # 获取奖池中的奖品列表
                    if prize_list:
                        prize_combobox.addItems(prize_list)

                    # 设置当前选中的奖品
                    lottery_settings = prob_data_item.get("lottery", {})
                    if pool_name in lottery_settings:
                        selected_prize = lottery_settings[pool_name].get("prize", "")
                        if selected_prize:
                            index = prize_combobox.findText(selected_prize)
                            if index >= 0:
                                prize_combobox.setCurrentIndex(index)

                    # 连接信号
                    prize_combobox.currentTextChanged.connect(
                        lambda text, name=student_name: self.save_prize(name, text)
                    )

                    self.table.setCellWidget(row, 3, prize_combobox)
                else:
                    # 点名模式：显示空单元格
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(
                        empty_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )
                    empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, 3, empty_item)

                # 概率
                if self.current_mode == 0:
                    # 点名模式
                    probability_value = prob_data_item.get("roll_call", {}).get(
                        "probability", 1.0
                    )
                else:
                    # 抽奖模式
                    pool_name = self.pool_comboBox.currentText()
                    lottery_settings = prob_data_item.get("lottery", {})
                    if pool_name in lottery_settings:
                        probability_value = lottery_settings[pool_name].get(
                            "probability", 1.0
                        )
                    else:
                        probability_value = 1.0

                probability_spin = DoubleSpinBox()
                probability_spin.setRange(0, 1000)
                probability_spin.setSingleStep(0.1)
                probability_spin.setDecimals(1)
                probability_spin.setValue(probability_value)
                probability_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # 连接信号
                probability_spin.valueChanged.connect(
                    lambda value, name=student_name: self.save_probability(name, value)
                )
                self.table.setCellWidget(row, 4, probability_spin)

            # 调整列宽
            self.table.horizontalHeader().resizeSection(0, 80)
            self.table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
            for i in range(1, 5):
                self.table.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Stretch
                )

        except Exception as e:
            logger.exception(f"刷新表格数据失败: {str(e)}")
        finally:
            self.table.blockSignals(False)

    def save_probability_data(self):
        """保存概率设置数据"""
        try:
            write_behind_scenes_settings(self.probability_data)
        except Exception as e:
            logger.exception(f"保存概率设置数据失败: {e}")

    def save_table_data(self, row, col):
        """保存表格编辑的数据"""
        if not self.current_list_name:
            return

        if col != 0:  # 只处理启用勾选框列
            return

        checkbox_item = self.table.item(row, 0)
        if not checkbox_item:
            return

        name_item = self.table.item(row, 2)
        if not name_item:
            return

        name = name_item.text()

        if name not in self.probability_data:
            self.probability_data[name] = {
                "roll_call": {"enabled": False, "probability": 1.0},
                "lottery": {},
            }

        is_enabled = checkbox_item.checkState() == Qt.CheckState.Checked

        if self.current_mode == 0:
            # 点名模式
            self.probability_data[name]["roll_call"]["enabled"] = is_enabled
        else:
            # 抽奖模式
            pool_name = self.pool_comboBox.currentText()
            if "lottery" not in self.probability_data[name]:
                self.probability_data[name]["lottery"] = {}

            if pool_name not in self.probability_data[name]["lottery"]:
                self.probability_data[name]["lottery"][pool_name] = {
                    "enabled": False,
                    "probability": 1.0,
                }

            self.probability_data[name]["lottery"][pool_name]["enabled"] = is_enabled

        self.save_probability_data()

    def save_probability(self, name, value):
        """保存概率设置

        Args:
            name: 学生/奖品名称
            value: 概率权重值
        """
        if not self.current_list_name:
            return

        if name not in self.probability_data:
            self.probability_data[name] = {
                "roll_call": {"enabled": False, "probability": 1.0},
                "lottery": {},
            }

        if self.current_mode == 0:
            # 点名模式
            self.probability_data[name]["roll_call"]["probability"] = value
        else:
            # 抽奖模式
            pool_name = self.pool_comboBox.currentText()
            if "lottery" not in self.probability_data[name]:
                self.probability_data[name]["lottery"] = {}

            if pool_name not in self.probability_data[name]["lottery"]:
                self.probability_data[name]["lottery"][pool_name] = {
                    "enabled": False,
                    "probability": 1.0,
                }

            self.probability_data[name]["lottery"][pool_name]["probability"] = value

        self.save_probability_data()

    def save_prize(self, name, prize_name):
        """保存奖品关联

        Args:
            name: 学生名称
            prize_name: 奖品名称
        """
        if not self.current_list_name:
            return

        if name not in self.probability_data:
            self.probability_data[name] = {
                "roll_call": {"enabled": False, "probability": 1.0},
                "lottery": {},
            }

        if self.current_mode == 1:
            # 抽奖模式
            pool_name = self.pool_comboBox.currentText()
            if "lottery" not in self.probability_data[name]:
                self.probability_data[name]["lottery"] = {}

            if pool_name not in self.probability_data[name]["lottery"]:
                self.probability_data[name]["lottery"][pool_name] = {
                    "enabled": False,
                    "probability": 1.0,
                    "prize": "",
                }

            self.probability_data[name]["lottery"][pool_name]["prize"] = prize_name

        self.save_probability_data()

    def cleanup_file_watcher(self):
        """清理文件系统监视器"""
        if hasattr(self, "_shared_watcher"):
            roll_call_list_dir = get_data_path("list", "roll_call_list")
            if roll_call_list_dir.exists():
                self._shared_watcher.remove_watcher(
                    str(roll_call_list_dir), self.on_directory_changed
                )
            lottery_list_dir = get_data_path("list", "lottery_list")
            if lottery_list_dir.exists():
                self._shared_watcher.remove_watcher(
                    str(lottery_list_dir), self.on_directory_changed
                )

    def closeEvent(self, event):
        """窗口关闭事件，确保线程被正确停止"""
        # 停止加载线程（如果存在）
        if hasattr(self, "load_worker") and self.load_worker is not None:
            if self.load_worker.isRunning():
                self.load_worker.quit()
                self.load_worker.wait()
            self.load_worker.deleteLater()

        # 清理文件监视器
        self.cleanup_file_watcher()

        super().closeEvent(event)

    def __del__(self):
        """析构函数，确保清理资源"""
        try:
            # 停止加载线程（如果存在）
            if hasattr(self, "load_worker") and self.load_worker is not None:
                if self.load_worker.isRunning():
                    self.load_worker.quit()
                    self.load_worker.wait()
                self.load_worker.deleteLater()

            # 清理文件监视器
            self.cleanup_file_watcher()
        except Exception:
            pass
