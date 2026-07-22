# ==================================================
# 导入库
# ==================================================
from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.Language.obtain_language import *

import os
from app.common.extraction.cses_parser import CSESParser


class CurrentConfigViewerWindow(QWidget):
    """当前配置查看器窗口"""

    def __init__(self, parent=None):
        """初始化当前配置查看器窗口"""
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(
            get_content_name_async("linkage_settings", "template_title")
        )

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 创建标题标签
        title_label = BodyLabel(
            get_content_name_async("linkage_settings", "cses_import_settings", "name")
        )

        # 创建表格控件
        self.table_widget = TableWidget()
        self.table_widget.setBorderVisible(True)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setWordWrap(False)
        self.table_widget.setColumnCount(5)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_widget.verticalHeader().hide()
        self.table_widget.setHorizontalHeaderLabels(
            get_content_name_async("linkage_settings", "table_headers")
        )
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 加载当前配置
        self.load_current_config()

        # 创建平滑滚动区域
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)

        # 添加到主布局
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(scroll_area)

    def load_current_config(self):
        """加载当前配置"""
        try:
            # 获取data/CSES文件夹路径
            cses_dir = get_data_path("CSES")
            if not os.path.exists(cses_dir):
                self.table_widget.setRowCount(1)
                self.table_widget.setItem(
                    0,
                    0,
                    QTableWidgetItem(
                        get_content_name_async("linkage_settings", "no_cses_folder")
                    ),
                )
                return

            # 获取CSES文件夹中的所有文件
            cses_files = [
                f for f in os.listdir(cses_dir) if f.endswith((".yaml", ".yml"))
            ]
            if not cses_files:
                self.table_widget.setRowCount(1)
                self.table_widget.setItem(
                    0,
                    0,
                    QTableWidgetItem(
                        get_content_name_async("linkage_settings", "no_schedule_file")
                    ),
                )
                return

            # 准备数据
            data = []
            for file_name in cses_files:
                file_path = os.path.join(cses_dir, file_name)
                try:
                    # 创建CSES解析器
                    parser = CSESParser()
                    if parser.load_from_file(file_path):
                        # 获取课程信息
                        class_info_list = parser.get_class_info()
                        for class_info in class_info_list:
                            # 转换星期
                            day_map = get_content_name_async(
                                "linkage_settings", "day_map"
                            )
                            day_of_week = str(class_info.get("day_of_week", 0))
                            day = day_map.get(
                                day_of_week,
                                get_content_name_async("linkage_settings", "unknown"),
                            )

                            data.append(
                                [
                                    day,
                                    class_info.get(
                                        "name",
                                        get_content_name_async(
                                            "linkage_settings", "unknown_course"
                                        ),
                                    ),
                                    class_info.get("start_time", ""),
                                    class_info.get("end_time", ""),
                                    class_info.get("teacher", ""),
                                ]
                            )
                except Exception as e:
                    logger.exception(f"解析文件{file_name}失败: {e}")
                    data.append(
                        [
                            "",
                            get_content_name_async("linkage_settings", "parse_failed"),
                            "",
                            "",
                            "",
                        ]
                    )

            # 设置表格列数和标题
            self.table_widget.setColumnCount(5)
            self.table_widget.setHorizontalHeaderLabels(
                get_content_name_async("linkage_settings", "table_headers")
            )
            self.table_widget.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch
            )
            # 设置表格内容居中
            self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

            # 设置表格行数
            self.table_widget.setRowCount(len(data))

            # 填充表格数据
            for row, (day, name, start, end, teacher) in enumerate(data):
                # 创建表格项并设置居中
                day_item = QTableWidgetItem(day)
                day_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 0, day_item)

                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 1, name_item)

                start_item = QTableWidgetItem(start)
                start_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 2, start_item)

                end_item = QTableWidgetItem(end)
                end_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 3, end_item)

                teacher_item = QTableWidgetItem(teacher)
                teacher_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 4, teacher_item)

        except Exception as e:
            logger.exception(f"加载当前配置失败: {e}")
            self.table_widget.setRowCount(1)
            self.table_widget.setItem(
                0,
                0,
                QTableWidgetItem(
                    get_content_name_async(
                        "linkage_settings", "load_config_failed"
                    ).format(str(e))
                ),
            )

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        super().closeEvent(event)
