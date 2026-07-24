# ==================================================
# 导入库
# ==================================================

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
from app.common.data.list import (
    get_class_name_list,
    get_pool_name_list,
    get_student_list,
    get_pool_list,
)


# ==================================================
# 语音播报设置主类
# ==================================================
class specific_announcements(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 只添加TTS别名管理表格组件（整合所有功能）
        self.main_settings_widget = voice_announcement_main(self)
        self.vBoxLayout.addWidget(self.main_settings_widget)


# ==================================================
# TTS管理表格组件（整合所有功能）
# ==================================================
class voice_announcement_main(GroupHeaderCardWidget):
    """TTS管理表格，整合所有语音播报设置功能"""

    refresh_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("specific_announcements", "title"))
        self.setBorderRadius(8)

        # 初始化数据加载器
        self.current_mode = 0  # 0: 点名模式, 1: 抽奖模式
        class_history = get_class_name_list()
        self.current_class_name = class_history[0] if class_history else ""

        # 启用/禁用语音播报开关
        self.enabled_switch = SwitchButton()
        self.enabled_switch.setOffText(
            get_content_switchbutton_name_async(
                "specific_announcements", "enabled", "disable"
            )
        )
        self.enabled_switch.setOnText(
            get_content_switchbutton_name_async(
                "specific_announcements", "enabled", "enable"
            )
        )
        self.enabled_switch.setChecked(
            readme_settings_async("specific_announcements", "enabled")
        )
        self.enabled_switch.checkedChanged.connect(
            lambda state: update_settings("specific_announcements", "enabled", state)
        )

        # 模式选择下拉框
        self.mode_comboBox = ComboBox()
        self.mode_comboBox.addItems(
            get_content_combo_name_async("specific_announcements", "mode")
        )
        self.mode_comboBox.setCurrentIndex(
            readme_settings_async("specific_announcements", "default_mode")
        )
        self.mode_comboBox.currentIndexChanged.connect(
            lambda index: [
                update_settings("specific_announcements", "default_mode", index),
                self.on_mode_changed(index),
            ]
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_speaker_2_20_filled"),
            get_content_name_async("specific_announcements", "enabled"),
            get_content_description_async("specific_announcements", "enabled"),
            self.enabled_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_voicemail_20_filled"),
            get_content_name_async("specific_announcements", "mode"),
            get_content_description_async("specific_announcements", "mode"),
            self.mode_comboBox,
        )

        # 创建班级选择区域
        QTimer.singleShot(APPLY_DELAY, self.create_class_selection)

        # 创建表格区域
        QTimer.singleShot(APPLY_DELAY, self.create_table)

        # 初始化班级列表
        QTimer.singleShot(APPLY_DELAY, self.refresh_class_history)

        # 设置文件系统监视器
        QTimer.singleShot(APPLY_DELAY, self.setup_file_watcher)

        # 初始化数据
        QTimer.singleShot(APPLY_DELAY, self.refresh_data)

        # 连接信号
        self.refresh_signal.connect(self.refresh_data)

    def on_mode_changed(self, mode):
        """模式切换时的处理函数

        Args:
            mode: 0表示点名模式，1表示抽奖模式
        """
        self.current_mode = mode
        self.refresh_class_history()
        self.refresh_data()

    def create_class_selection(self):
        """创建班级选择区域"""
        self.class_comboBox = ComboBox()

        # 获取对应模式的历史列表并填充下拉框
        if self.current_mode == 0:  # 点名模式
            class_history = get_class_name_list()
        else:  # 抽奖模式
            class_history = get_pool_name_list()
        self.class_comboBox.addItems(class_history)

        # 设置默认选择
        if class_history:
            self.class_comboBox.setCurrentIndex(0)
            self.current_class_name = class_history[0]
        else:
            # 如果没有历史记录，设置占位符
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(
                get_content_name_async("specific_announcements", "select_class_name")
            )
            self.current_class_name = ""

        self.class_comboBox.currentIndexChanged.connect(self.on_class_changed)

        # 添加到分组
        self.addGroup(
            get_theme_icon("ic_fluent_class_20_filled"),
            get_content_name_async("specific_announcements", "select_class_name"),
            get_content_description_async(
                "specific_announcements", "select_class_name"
            ),
            self.class_comboBox,
        )

    def create_table(self):
        """创建表格区域"""
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()

        # 根据模式设置表格头
        if self.current_mode == 0:  # 点名模式
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                [
                    get_content_name_async("specific_announcements", "header"),
                    get_content_name_async("specific_announcements", "id_field"),
                    get_content_name_async("specific_announcements", "name_field"),
                    get_content_name_async("specific_announcements", "tts_alias"),
                    get_content_name_async("specific_announcements", "prefix_field"),
                    get_content_name_async("specific_announcements", "suffix_field"),
                ]
            )
        else:  # 抽奖模式
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                [
                    get_content_name_async("specific_announcements", "header"),
                    get_content_name_async(
                        "specific_announcements", "lottery_id_field"
                    ),
                    get_content_name_async(
                        "specific_announcements", "lottery_name_field"
                    ),
                    get_content_name_async("specific_announcements", "tts_alias"),
                    get_content_name_async(
                        "specific_announcements", "lottery_prefix_field"
                    ),
                    get_content_name_async(
                        "specific_announcements", "lottery_suffix_field"
                    ),
                ]
            )

        # 设置表格属性
        for i in range(self.table.columnCount()):
            if i == 0:  # 启用列
                self.table.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.ResizeToContents
                )
                self.table.setColumnWidth(i, 80)  # 缩小列宽
            else:
                self.table.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Stretch
                )
            self.table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

        # 设置不可编辑列（学号/序号和姓名/名称）
        self.table.itemChanged.connect(self.on_item_changed)

        self.layout().addWidget(self.table)

    def on_item_changed(self, item):
        """处理表格项变化"""
        # 只允许编辑第0列（启用状态）和第3-5列（替换名称、前缀、后缀）
        if item.column() == 1 or item.column() == 2:
            # 撤销编辑
            self.table.blockSignals(True)
            self.table.setItem(
                item.row(),
                item.column(),
                self.original_items[item.row()][item.column()],
            )
            self.table.blockSignals(False)
            return

        # 获取行数据
        enabled_item = self.table.item(item.row(), 0)
        id_field = self.table.item(item.row(), 1).text()
        name_field = self.table.item(item.row(), 2).text()

        # 获取其他列数据
        tts_alias_item = self.table.item(item.row(), 3)
        prefix_item = self.table.item(item.row(), 4)
        suffix_item = self.table.item(item.row(), 5)

        enabled = (
            enabled_item.checkState() == Qt.CheckState.Checked if enabled_item else True
        )
        tts_alias = tts_alias_item.text() if tts_alias_item else ""
        prefix = prefix_item.text() if prefix_item else ""
        suffix = suffix_item.text() if suffix_item else ""

        # 保存到音频设置文件
        try:
            # 获取音频设置文件路径
            audio_data_path = get_audio_path()
            if not audio_data_path.exists():
                audio_data_path.mkdir(parents=True, exist_ok=True)

            audio_file = audio_data_path / f"{self.current_class_name}.json"

            # 读取现有音频设置数据
            audio_data = {}
            if audio_file.exists():
                with open_file(audio_file, "r", encoding="utf-8") as f:
                    audio_data = json.load(f)

            # 更新音频设置数据（只保存需要的字段，不保存学号/序号）
            audio_data[name_field] = {
                "tts_alias": tts_alias,
                "prefix": prefix,
                "suffix": suffix,
                "announcement_enabled": enabled,
            }

            # 保存到音频设置文件
            with open_file(audio_file, "w", encoding="utf-8") as f:
                json.dump(audio_data, f, indent=4, ensure_ascii=False)

            item_type = "学生" if self.current_mode == 0 else "奖品"
            logger.debug(f"已更新{item_type} {name_field} 的语音播报设置")
        except Exception as e:
            logger.exception(f"更新语音播报设置失败: {e}")

    def setup_file_watcher(self):
        """设置文件系统监视器，监控历史记录文件夹的变化"""
        if self.current_mode == 0:  # 点名模式
            history_dir = get_data_path("history/roll_call_history")
        else:  # 抽奖模式
            history_dir = get_data_path("history/lottery_history")

        if not history_dir.exists():
            logger.warning(f"历史记录文件夹不存在: {history_dir}")
            return

        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(str(history_dir))
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)

    def on_directory_changed(self, path):
        """当目录内容发生变化时调用此方法"""
        QTimer.singleShot(1000, self.refresh_class_history)

    def refresh_class_history(self):
        """刷新下拉框列表"""
        if not hasattr(self, "class_comboBox"):
            return

        # 保存当前选择的名称
        current_class_name = self.class_comboBox.currentText()

        # 获取对应模式的最新历史列表
        if self.current_mode == 0:  # 点名模式
            class_history = get_class_name_list()
        else:  # 抽奖模式
            class_history = get_pool_name_list()

        # 清空并重新填充下拉框
        self.class_comboBox.clear()
        self.class_comboBox.addItems(class_history)

        # 如果之前选择的名称还在列表中，则重新选择它
        if current_class_name and current_class_name in class_history:
            index = class_history.index(current_class_name)
            self.class_comboBox.setCurrentIndex(index)
            # 更新current_class_name
            self.current_class_name = current_class_name
        elif class_history:
            # 如果之前选择的名称不在列表中，选择第一个
            self.class_comboBox.setCurrentIndex(0)
            # 更新current_class_name
            self.current_class_name = class_history[0]
        else:
            # 如果没有历史记录，设置占位符
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(
                get_content_name_async("specific_announcements", "select_class_name")
            )
            # 更新current_class_name
            self.current_class_name = ""

    def on_class_changed(self, index):
        """班级选择变化时刷新表格数据"""
        if not hasattr(self, "class_comboBox"):
            return

        # 更新当前班级名称
        self.current_class_name = self.class_comboBox.currentText()

        # 刷新表格数据
        self.refresh_data()

    def refresh_data(self):
        """刷新表格数据"""
        # 确保表格已经创建
        if not hasattr(self, "table"):
            return
        if not hasattr(self, "class_comboBox"):
            return

        class_name = self.class_comboBox.currentText()
        if not class_name:
            self.table.setRowCount(0)
            return

        # 临时阻止信号，避免初始化时触发保存操作
        self.table.blockSignals(True)

        try:
            # 根据模式获取数据
            if self.current_mode == 0:  # 点名模式
                items_list = get_student_list(class_name)
            else:  # 抽奖模式
                items_list = get_pool_list(class_name)

            # 过滤掉不存在的项目
            cleaned_items = [item for item in items_list if item.get("exist", True)]

            # 读取音频设置数据
            audio_data = {}
            audio_file = get_audio_path(f"{class_name}.json")
            if audio_file.exists():
                with open_file(audio_file, "r", encoding="utf-8") as f:
                    audio_data = json.load(f)

            # 设置表格行数
            self.table.setRowCount(len(cleaned_items))

            # 填充表格数据
            for row, item in enumerate(cleaned_items):
                name = item.get("name", "")

                # 获取对应的音频设置，如果不存在则使用默认值
                audio_settings = audio_data.get(
                    name,
                    {
                        "tts_alias": "",
                        "prefix": "",
                        "suffix": "",
                        "announcement_enabled": True,
                    },
                )

                # 启用状态（可编辑）
                enabled_item = QTableWidgetItem()
                enabled_item.setCheckState(
                    Qt.CheckState.Checked
                    if audio_settings["announcement_enabled"]
                    else Qt.CheckState.Unchecked
                )
                enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, enabled_item)

                # 学号/序号（不可编辑）
                id_item = QTableWidgetItem(str(item.get("id", row + 1)))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, id_item)

                # 姓名/名称（不可编辑）
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, name_item)

                # 替换名称（可编辑）
                alias_item = QTableWidgetItem(audio_settings["tts_alias"])
                alias_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, alias_item)

                # 前缀（可编辑）
                prefix_item = QTableWidgetItem(audio_settings["prefix"])
                prefix_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, prefix_item)

                # 后缀（可编辑）
                suffix_item = QTableWidgetItem(audio_settings["suffix"])
                suffix_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 5, suffix_item)

            # 保存原始数据，用于撤销编辑
            self.original_items = []
            for i in range(self.table.rowCount()):
                row_items = []
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    row_items.append(item.clone() if item else QTableWidgetItem(""))
                self.original_items.append(row_items)

        except Exception as e:
            logger.exception(f"刷新表格数据失败: {str(e)}")
        finally:
            # 恢复信号
            self.table.blockSignals(False)


# ==================================================
# TTS发音优化函数
# ==================================================
def get_tts_pronunciation(name, id_field="", tts_alias="", prefix="", suffix=""):
    """获取TTS发音文本

    Args:
        name: 原始姓名
        id_field: 学号/序号
        tts_alias: TTS别名
        prefix: 前缀文本
        suffix: 后缀文本

    Returns:
        str: 用于TTS发音的文本，格式为：前缀 + 学号/序号 + 替换名称/姓名 + 后缀
    """
    # 确定使用的名称（优先使用别名）
    used_name = tts_alias if tts_alias else name

    # 构建播报文本：前缀 + 学号/序号 + 名称 + 后缀
    pronunciation_parts = []

    # 添加前缀
    if prefix:
        pronunciation_parts.append(prefix)

    # 添加学号/序号
    if id_field:
        pronunciation_parts.append(id_field)

    # 添加名称
    pronunciation_parts.append(used_name)

    # 添加后缀
    if suffix:
        pronunciation_parts.append(suffix)

    return " ".join(pronunciation_parts)
