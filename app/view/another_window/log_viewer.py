# ==================================================
# 导入库
# ==================================================
import os
from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import get_path
from app.tools.personalised import *
from app.Language.obtain_language import *


class LogViewerWindow(QWidget):
    """日志查看窗口"""

    def __init__(self, parent=None):
        """初始化日志查看窗口"""
        super().__init__(parent)
        self._closing = False
        self.current_log_file = None
        self.hidden_keywords = ("内幕", "behind")
        self.log_level_colors = {
            "DEBUG": "#999999",
            "INFO": "#0099CC",
            "WARNING": "#FF9900",
            "ERROR": "#FF0000",
            "CRITICAL": "#8B0000",
        }
        self.file_watcher = QFileSystemWatcher(self)
        self.init_ui()
        self._load_timer = QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self.load_log_files)
        self._load_timer.start(0)

    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 创建顶部控制区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        # 创建日志文件选择下拉框
        self.log_file_combo = ComboBox()
        self.log_file_combo.setMinimumWidth(300)
        self.log_file_combo.currentIndexChanged.connect(self.on_log_file_changed)
        control_layout.addWidget(
            BodyLabel(get_content_name_async("log_viewer", "log_file_label"))
        )
        control_layout.addWidget(self.log_file_combo)

        # 创建清空日志按钮
        self.clear_button = PushButton(
            get_content_name_async("log_viewer", "clear_button")
        )
        self.clear_button.clicked.connect(self.clear_current_log)
        control_layout.addWidget(self.clear_button)

        # 创建清空全部日志按钮
        self.clear_all_button = PushButton(
            get_content_name_async("log_viewer", "clear_all_button")
        )
        self.clear_all_button.clicked.connect(self.clear_all_logs)
        control_layout.addWidget(self.clear_all_button)

        # 创建打开日志文件夹按钮
        self.open_folder_button = PushButton(
            get_content_name_async("log_viewer", "open_folder_button")
        )
        self.open_folder_button.clicked.connect(self.open_log_folder)
        control_layout.addWidget(self.open_folder_button)

        control_layout.addStretch()

        # 创建日志等级过滤
        self.log_level_combo = ComboBox()
        log_levels = get_content_combo_name_async("log_viewer", "log_levels")
        self.log_level_combo.addItems(log_levels)
        self.log_level_combo.currentIndexChanged.connect(lambda: self.filter_logs())
        control_layout.addWidget(
            BodyLabel(get_content_name_async("log_viewer", "log_level_label"))
        )
        control_layout.addWidget(self.log_level_combo)

        # 添加控制区域到主布局
        self.main_layout.addLayout(control_layout)

        # 创建日志显示文本框
        self.log_text = TextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText(
            get_content_name_async("log_viewer", "placeholder")
        )
        self.log_text.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)

        # 创建平滑滚动区域
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.log_text)

        # 添加到主布局
        self.main_layout.addWidget(scroll_area)

        # 创建状态栏
        self.status_label = BodyLabel("")
        self.main_layout.addWidget(self.status_label)

    def load_log_files(self):
        """加载日志文件列表"""
        try:
            if self._closing:
                return
            # 获取日志目录
            log_dir = get_path(LOG_DIR)
            if not os.path.exists(log_dir):
                self.status_label.setText(
                    get_content_name_async("log_viewer", "no_log_dir")
                )
                return

            # 添加文件夹监听
            if str(log_dir) not in self.file_watcher.directories():
                self.file_watcher.addPath(str(log_dir))
                self.file_watcher.directoryChanged.connect(self.on_directory_changed)

            # 获取所有日志文件
            log_files = []
            for file_name in os.listdir(log_dir):
                if file_name.endswith(".log"):
                    file_path = os.path.join(log_dir, file_name)
                    log_files.append((file_name, file_path))

            # 按修改时间排序（最新的在前）
            log_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)

            # 保存文件列表
            self.log_files = log_files

            # 更新下拉框
            self.log_file_combo.blockSignals(True)
            self.log_file_combo.clear()
            for file_name, _ in log_files:
                self.log_file_combo.addItem(file_name)
            self.log_file_combo.blockSignals(False)

            # 如果有日志文件，加载最新的
            if log_files:
                self.log_file_combo.setCurrentIndex(0)
                self.load_log_content(log_files[0][1])
            else:
                self.log_text.clear()
                self.status_label.setText(
                    get_content_name_async("log_viewer", "no_log_files")
                )

        except Exception as e:
            logger.exception(f"加载日志文件列表失败: {e}")
            self.status_label.setText(
                get_content_name_async("log_viewer", "load_failed").format(str(e))
            )

    def on_directory_changed(self):
        """文件夹变化时的处理"""
        if self._closing:
            return
        QTimer.singleShot(100, self.load_log_files)

    def on_log_file_changed(self, index):
        """日志文件改变时的处理"""
        if index >= 0 and index < len(self.log_files):
            self.load_log_content(self.log_files[index][1])

    def load_log_content(self, file_path):
        """加载日志内容"""
        try:
            if self._closing:
                return
            self.current_log_file = file_path

            # 添加文件监听
            if str(file_path) not in self.file_watcher.files():
                self.file_watcher.addPath(str(file_path))
                self.file_watcher.fileChanged.connect(self.on_file_changed)

            # 读取日志文件
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 应用过滤并显示
            self.filter_logs(lines)

            # 更新状态栏
            file_size = os.path.getsize(file_path)
            self.status_label.setText(
                get_content_name_async("log_viewer", "status").format(
                    os.path.basename(file_path), file_size
                )
            )

        except Exception as e:
            logger.exception(f"加载日志内容失败: {e}")
            self.status_label.setText(
                get_content_name_async("log_viewer", "load_failed").format(str(e))
            )

    def on_file_changed(self, file_path):
        """文件变化时的处理"""
        if self._closing:
            return
        if file_path == self.current_log_file:
            QTimer.singleShot(100, lambda: self.load_log_content(file_path))

    def filter_logs(self, lines=None):
        """过滤日志"""
        try:
            if self._closing:
                return
            # 如果没有提供 lines，则从文件读取
            if lines is None:
                if not self.current_log_file or not os.path.exists(
                    self.current_log_file
                ):
                    return
                with open(self.current_log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            lines = [
                line
                for line in lines
                if "内幕" not in line and "behind" not in line.lower()
            ]

            # 获取选择的日志等级
            level_index = self.log_level_combo.currentIndex()
            log_levels_dict = get_any_position_value_async("log_viewer", "log_levels")
            log_levels = log_levels_dict.get("combo_items", [])
            selected_level = (
                log_levels[level_index] if level_index < len(log_levels) else "DEBUG"
            )

            # 如果选择"全部"，显示所有日志
            if level_index == 0:
                self.display_colored_logs(lines)
                return

            # 等级映射（值越大，等级越高）
            level_map = {
                "DEBUG": 0,
                "INFO": 1,
                "WARNING": 2,
                "ERROR": 3,
                "CRITICAL": 4,
            }
            min_level = level_map.get(selected_level, 0)

            # 过滤日志行
            filtered_lines = []
            for line in lines:
                # 检查日志等级
                found_level = False
                for level, level_value in level_map.items():
                    # 日志格式：时间戳 | 等级(8字符左对齐) | 模块:函数:行号 - 消息
                    # 匹配模式： | DEBUG    | （等级左对齐）
                    if f" | {level:<8} | " in line:
                        # 只显示等级 >= min_level 的日志
                        if level_value >= min_level:
                            filtered_lines.append(line)
                        found_level = True
                        break

                # 如果没有找到等级标记，保留该行
                if not found_level:
                    filtered_lines.append(line)

            # 显示过滤后的日志
            self.display_colored_logs(filtered_lines)

        except Exception as e:
            logger.exception(f"过滤日志失败: {e}")

    def display_colored_logs(self, lines):
        """显示带颜色的日志"""
        try:
            # 获取当前设置的字体
            custom_font = load_custom_font()
            font_family = custom_font if custom_font else "Consolas, monospace"

            html_content = f"<html><body style='font-family: {font_family}, monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 10px;'>"

            for line in lines:
                # 转义 HTML 特殊字符
                escaped_line = (
                    line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                )

                # 检查日志等级并应用颜色
                colored_line = escaped_line
                for level, color in self.log_level_colors.items():
                    # 匹配日志等级（8字符左对齐）
                    if f" | {level:<8} | " in escaped_line:
                        # 为整行应用颜色
                        colored_line = (
                            f"<span style='color: {color};'>{escaped_line}</span>"
                        )
                        break

                html_content += colored_line + "<br>"

            html_content += "</body></html>"
            self.log_text.setHtml(html_content)

        except Exception as e:
            logger.exception(f"显示带颜色日志失败: {e}")

    def clear_current_log(self):
        """清空当前日志文件"""
        if not self.current_log_file:
            return

        try:
            # 确认对话框
            confirm = MessageBox(
                get_content_name_async("log_viewer", "clear_confirm_title"),
                get_content_name_async("log_viewer", "clear_confirm_content"),
                self,
            )
            confirm.yesButton.setText(
                get_any_position_value_async("log_viewer", "yes_button")
            )
            confirm.cancelButton.setText(
                get_any_position_value_async("log_viewer", "cancel_button")
            )
            if not confirm.exec():
                return

            # 清空日志文件
            with open(self.current_log_file, "w", encoding="utf-8") as f:
                f.write("")

            # 重新加载
            self.load_log_content(self.current_log_file)
            self.status_label.setText(
                get_content_name_async("log_viewer", "clear_success")
            )

        except Exception as e:
            logger.exception(f"清空日志文件失败: {e}")
            self.status_label.setText(
                get_content_name_async("log_viewer", "clear_failed").format(str(e))
            )

    def clear_all_logs(self):
        """清空全部日志文件"""
        try:
            # 确认对话框
            confirm = MessageBox(
                get_content_name_async("log_viewer", "clear_all_confirm_title"),
                get_content_name_async("log_viewer", "clear_all_confirm_content"),
                self,
            )
            confirm.yesButton.setText(
                get_any_position_value_async("log_viewer", "yes_button")
            )
            confirm.cancelButton.setText(
                get_any_position_value_async("log_viewer", "cancel_button")
            )
            if not confirm.exec():
                return

            # 获取日志目录
            log_dir = get_path(LOG_DIR)
            if not os.path.exists(log_dir):
                self.status_label.setText(
                    get_content_name_async("log_viewer", "no_log_dir")
                )
                return

            # 清空所有日志文件
            cleared_count = 0
            for file_name in os.listdir(log_dir):
                if file_name.endswith(".log"):
                    file_path = os.path.join(log_dir, file_name)
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write("")
                        cleared_count += 1
                    except Exception as e:
                        logger.warning(f"清空日志文件 {file_name} 失败: {e}")

            # 重新加载日志文件列表
            self.load_log_files()
            self.status_label.setText(
                get_content_name_async("log_viewer", "clear_all_success").format(
                    cleared_count
                )
            )

        except Exception as e:
            logger.error(f"清空全部日志文件失败: {e}")
            self.status_label.setText(
                get_content_name_async("log_viewer", "clear_all_failed").format(str(e))
            )

    def open_log_folder(self):
        """打开日志文件夹"""
        try:
            log_dir = get_path(LOG_DIR)
            if not os.path.exists(log_dir):
                self.status_label.setText(
                    get_content_name_async("log_viewer", "no_log_dir")
                )
                return

            # 打开文件夹
            os.startfile(log_dir)

        except Exception as e:
            logger.error(f"打开日志文件夹失败: {e}")
            self.status_label.setText(
                get_content_name_async("log_viewer", "open_folder_failed").format(
                    str(e)
                )
            )

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        self._closing = True
        try:
            if hasattr(self, "_load_timer") and self._load_timer.isActive():
                self._load_timer.stop()
        except Exception:
            pass
        try:
            self.file_watcher.directoryChanged.disconnect(self.on_directory_changed)
        except Exception:
            pass
        try:
            self.file_watcher.fileChanged.disconnect(self.on_file_changed)
        except Exception:
            pass
        try:
            paths = list(self.file_watcher.files()) + list(
                self.file_watcher.directories()
            )
            if paths:
                self.file_watcher.removePaths(paths)
        except Exception:
            pass
        super().closeEvent(event)
