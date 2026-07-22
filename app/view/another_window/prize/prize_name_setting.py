# ==================================================
# 导入库
# ==================================================
import re
import json

from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.config import *
from app.common.data.list import *


class PrizeNameSettingWindow(QWidget):
    """奖品名称设置窗口"""

    def __init__(self, parent=None, list_name=None):
        """初始化奖品名称设置窗口"""
        super().__init__(parent)

        # 初始化变量
        self.list_name = list_name
        self.saved = False
        self.initial_names = []  # 保存初始加载的奖品名称列表

        # 初始化UI
        self.init_ui()

        # 连接信号
        self.__connect_signals()

    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(get_content_name_async("lottery_name_setting", "title"))

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 创建标题
        self.title_label = TitleLabel(
            get_content_name_async("lottery_name_setting", "title")
        )
        self.main_layout.addWidget(self.title_label)

        # 创建说明标签
        self.description_label = BodyLabel(
            get_content_name_async("lottery_name_setting", "description")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        # 创建奖品名称输入区域
        self.__create_prize_name_input_area()

        # 创建按钮区域
        self.__create_button_area()

        # 添加伸缩项
        self.main_layout.addStretch(1)

    def __create_prize_name_input_area(self):
        """创建奖品名称输入区域"""
        # 创建卡片容器
        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)

        # 创建输入区域标题
        input_title = SubtitleLabel(
            get_content_name_async("lottery_name_setting", "input_title")
        )
        input_layout.addWidget(input_title)

        # 创建文本编辑框
        self.text_edit = PlainTextEdit()
        self.text_edit.setPlaceholderText(
            get_content_name_async("lottery_name_setting", "input_placeholder")
        )

        # 加载现有奖品名称
        existing_names = self.__load_existing_prize_names()
        if existing_names:
            self.text_edit.setPlainText("\n".join(existing_names))

        input_layout.addWidget(self.text_edit)

        # 添加到主布局
        self.main_layout.addWidget(input_card)

    def __load_existing_prize_names(self):
        """加载现有奖品名称"""
        try:
            # 获取奖池名单目录
            lottery_list_dir = get_data_path("list", "lottery_list")

            # 从设置中获取奖池名称
            if self.list_name:
                pool_name = self.list_name
            else:
                pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            # 如果文件不存在，返回空列表
            if not list_file.exists():
                self.initial_names = []
                return []

            # 读取文件内容
            with open_file(list_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 获取所有名称（字典的键）
            names = list(data.keys())
            # 保存到initial_names变量
            self.initial_names = names.copy()

            return names

        except Exception as e:
            logger.exception(f"加载奖品名称失败: {str(e)}")
            self.initial_names = []
            return []

    def __create_button_area(self):
        """创建按钮区域"""
        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 伸缩项
        button_layout.addStretch(1)

        # 保存按钮
        self.save_button = PrimaryPushButton(
            get_content_name_async("lottery_name_setting", "save_button")
        )
        self.save_button.setIcon(FluentIcon.SAVE)
        button_layout.addWidget(self.save_button)

        # 添加到主布局
        self.main_layout.addLayout(button_layout)

    def __connect_signals(self):
        """连接信号与槽"""
        self.save_button.clicked.connect(self.__save_names)
        # 添加文本变化监听器
        self.text_edit.textChanged.connect(self.__on_text_changed)

    def __on_text_changed(self):
        """文本变化事件处理"""
        # 获取当前文本中的名称
        current_text = self.text_edit.toPlainText()
        current_prize_names = [
            name.strip() for name in current_text.split("\n") if name.strip()
        ]

        # 检查哪些初始奖品名称被删除了
        deleted_prize_names = [
            name for name in self.initial_names if name not in current_prize_names
        ]

        # 如果有奖品名称被删除，显示提示
        if deleted_prize_names:
            for name in deleted_prize_names:
                # 显示删除提示
                config = NotificationConfig(
                    title=get_content_name_async(
                        "lottery_name_setting", "name_deleted_title"
                    ),
                    content=get_content_name_async(
                        "lottery_name_setting", "name_deleted_message"
                    ).format(name=name),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)

            # 更新初始奖品名称列表为当前列表，避免重复提示
            self.initial_names = current_prize_names.copy()

    def __save_names(self):
        """保存奖品名称"""
        try:
            # 获取输入的奖品名称
            prize_names_text = self.text_edit.toPlainText().strip()
            if not prize_names_text:
                # 显示错误消息
                config = NotificationConfig(
                    title=get_content_name_async("lottery_name_setting", "error_title"),
                    content=get_content_name_async(
                        "lottery_name_setting", "no_names_error"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            # 分割奖品名称
            prize_names = [
                name.strip() for name in prize_names_text.split("\n") if name.strip()
            ]

            # 验证奖品名称
            invalid_prize_names = []
            for name in prize_names:
                # 检查是否包含非法字符
                if re.search(r'[\/:*?"<>|]', name):
                    invalid_prize_names.append(name)
                # 检查是否为保留字
                elif name.lower() == "class":
                    invalid_prize_names.append(name)

            if invalid_prize_names:
                # 显示错误消息
                config = NotificationConfig(
                    title=get_content_name_async("lottery_name_setting", "error_title"),
                    content=get_content_name_async(
                        "lottery_name_setting", "invalid_names_error"
                    ).format(names=", ".join(invalid_prize_names)),
                    duration=5000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            duplicate_names = get_duplicate_names(prize_names)
            if duplicate_names:
                dialog = Dialog(
                    get_content_name_async(
                        "lottery_name_setting", "duplicate_names_title"
                    ),
                    get_content_name_async(
                        "lottery_name_setting", "duplicate_names_message"
                    ).format(
                        count=len(duplicate_names),
                        names="\n".join(duplicate_names),
                    ),
                    self,
                )
                dialog.yesButton.setText(
                    get_content_name_async(
                        "lottery_name_setting", "duplicate_names_rename_button"
                    )
                )
                dialog.cancelButton.setText(
                    get_content_name_async(
                        "lottery_name_setting", "duplicate_names_edit_button"
                    )
                )
                if dialog.exec():
                    prize_names, _ = make_unique_names(prize_names)
                    self.text_edit.setPlainText("\n".join(prize_names))
                else:
                    return

            # 获取文件路径
            lottery_list_dir = get_data_path("list", "lottery_list")
            lottery_list_dir.mkdir(parents=True, exist_ok=True)

            # 从设置中获取奖池名称
            pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            # 读取现有数据
            existing_data = {}
            if list_file.exists():
                with open_file(list_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            # 如果奖品名称没有新增
            if set(prize_names) == set(existing_data.keys()):
                # 显示提示消息
                config = NotificationConfig(
                    title=get_content_name_async("lottery_name_setting", "info_title"),
                    content=get_content_name_async(
                        "lottery_name_setting", "no_new_names_message"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)
                return

            # 创建新的学生数据字典
            new_data = {}

            # 为新奖品名称分配学号（从1开始递增）
            for i, name in enumerate(prize_names, 1):
                # 如果奖品名称已存在于现有数据中，保留原有信息
                if name in existing_data:
                    new_data[name] = existing_data[name]
                else:
                    # 新增的奖品名称，分配新的学号和默认值
                    new_data[name] = {
                        "id": i,
                        "weight": 1,
                        "exist": True,
                        "count": 1,
                        "tags": [],
                    }

            # 保存到文件
            with open_file(list_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)

            # 显示保存成功通知
            config = NotificationConfig(
                title=get_content_name_async("lottery_name_setting", "success_title"),
                content=get_content_name_async(
                    "lottery_name_setting", "success_message"
                ).format(count=len(prize_names)),
                duration=3000,
            )
            show_notification(NotificationType.SUCCESS, config, parent=self)

            # 标记为已保存
            self.saved = True

        except Exception as e:
            # 显示错误消息
            config = NotificationConfig(
                title=get_content_name_async("lottery_name_setting", "error_title"),
                content=f"{get_content_name_async('lottery_name_setting', 'save_error')}: {str(e)}",
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            logger.exception(f"保存奖品名称失败: {e}")

    def __cancel(self):
        """取消操作"""
        # 获取父窗口并关闭
        parent = self.parent()
        while parent:
            # 查找SimpleWindowTemplate类型的父窗口
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if not self.saved:
            # 创建确认对话框
            dialog = Dialog(
                get_content_name_async("lottery_name_setting", "unsaved_changes_title"),
                get_content_name_async(
                    "lottery_name_setting", "unsaved_changes_message"
                ),
                self,
            )

            dialog.yesButton.setText(
                get_content_name_async("lottery_name_setting", "discard_button")
            )
            dialog.cancelButton.setText(
                get_content_name_async(
                    "lottery_name_setting", "continue_editing_button"
                )
            )

            # 显示对话框并获取用户选择
            if dialog.exec():
                # 用户选择放弃更改，关闭窗口
                event.accept()
            else:
                # 用户选择继续编辑，取消关闭事件
                event.ignore()
        else:
            # 已保存，直接关闭
            event.accept()
