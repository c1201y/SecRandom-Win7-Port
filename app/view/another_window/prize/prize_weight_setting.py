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


class PrizeWeightSettingWindow(QWidget):
    """奖品权重设置窗口"""

    def __init__(self, parent=None, list_name=None):
        """初始化奖品权重设置窗口"""
        super().__init__(parent)

        # 初始化变量
        self.list_name = list_name
        self.saved = False
        self.initial_weights = []  # 保存初始加载的奖品权重列表

        # 初始化UI
        self.init_ui()

        # 连接信号
        self.__connect_signals()

    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(get_content_name_async("weight_setting", "title"))

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 创建标题
        self.title_label = TitleLabel(get_content_name_async("weight_setting", "title"))
        self.main_layout.addWidget(self.title_label)

        # 创建说明标签
        self.description_label = BodyLabel(
            get_content_name_async("weight_setting", "description")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        # 创建奖品权重输入区域
        self.__create_prize_weight_input_area()

        # 创建按钮区域
        self.__create_button_area()

        # 添加伸缩项
        self.main_layout.addStretch(1)

    def __create_prize_weight_input_area(self):
        """创建奖品权重输入区域"""
        # 创建卡片容器
        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)

        # 创建输入区域标题
        input_title = SubtitleLabel(
            get_content_name_async("weight_setting", "input_title")
        )
        input_layout.addWidget(input_title)

        # 创建文本编辑框
        self.text_edit = PlainTextEdit()
        self.text_edit.setPlaceholderText(
            get_content_name_async("weight_setting", "input_placeholder")
        )

        # 加载现有奖品权重
        existing_weights = self.__load_existing_weights()
        if existing_weights:
            self.text_edit.setPlainText("\n".join(existing_weights))

        input_layout.addWidget(self.text_edit)

        # 添加到主布局
        self.main_layout.addWidget(input_card)

    def __load_existing_weights(self):
        """加载现有奖品权重"""
        try:
            # 使用与保存一致的路径
            lottery_list_dir = get_data_path("list/lottery_list")

            # 从设置中获取奖池名称
            if self.list_name:
                pool_name = self.list_name
            else:
                pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            # 如果文件不存在，返回空列表
            if not list_file.exists():
                self.initial_weights = []
                return []

            # 读取文件内容
            with open_file(list_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            weights = []
            for item_name, item_info in data.items():
                if "weight" in item_info and item_info["weight"] is not None:
                    # 只显示权重值
                    weights.append(str(item_info["weight"]))

            self.initial_weights = weights.copy()

            return weights

        except Exception as e:
            logger.exception(f"加载奖品权重失败: {str(e)}")
            self.initial_weights = []
            return []

    def __create_button_area(self):
        """创建按钮区域"""
        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 伸缩项
        button_layout.addStretch(1)

        # 保存按钮
        self.save_button = PrimaryPushButton(
            get_content_name_async("weight_setting", "save_button")
        )
        self.save_button.setIcon(FluentIcon.SAVE)
        button_layout.addWidget(self.save_button)

        # 添加到主布局
        self.main_layout.addLayout(button_layout)

    def __connect_signals(self):
        """连接信号与槽"""
        self.save_button.clicked.connect(self.__save_weights)
        # 添加文本变化监听器
        self.text_edit.textChanged.connect(self.__on_text_changed)

    def __on_text_changed(self):
        """文本变化事件处理"""
        # 获取当前文本中的奖品权重
        current_text = self.text_edit.toPlainText()
        current_weights = [
            weight.strip() for weight in current_text.split("\n") if weight.strip()
        ]

        # 检查哪些初始奖品权重被删除了
        deleted_weights = [
            weight for weight in self.initial_weights if weight not in current_weights
        ]

        # 如果有奖品权重被删除，显示提示
        if deleted_weights:
            for weight in deleted_weights:
                # 显示删除提示
                config = NotificationConfig(
                    title=get_content_name_async(
                        "weight_setting", "weight_deleted_title"
                    ),
                    content=get_content_name_async(
                        "weight_setting", "weight_deleted_message"
                    ).format(weight=weight),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)

            # 更新初始奖品权重列表
            self.initial_weights = current_weights.copy()

    def __save_weights(self):
        """保存奖品权重"""
        try:
            # 获取输入的奖品权重
            weights_text = self.text_edit.toPlainText().strip()
            if not weights_text:
                # 显示错误消息
                config = NotificationConfig(
                    title=get_content_name_async("weight_setting", "error_title"),
                    content=get_content_name_async(
                        "weight_setting", "no_genders_error"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            # 分割奖品权重
            lines = [line.strip() for line in weights_text.split("\n") if line.strip()]

            # 验证性别
            invalid_weights = []
            for line in lines:
                if re.search(r'[\/\:*?"<>|]', line):
                    invalid_weights.append(line)

            if invalid_weights:
                # 显示错误消息
                config = NotificationConfig(
                    title=get_content_name_async("weight_setting", "error_title"),
                    content=get_content_name_async(
                        "weight_setting", "invalid_weights_error"
                    ).format(weights=", ".join(invalid_weights)),
                    duration=5000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            # 获取文件路径
            lottery_list_dir = get_data_path("list/lottery_list")
            lottery_list_dir.mkdir(parents=True, exist_ok=True)

            # 从设置中获取班级名称
            if self.list_name:
                pool_name = self.list_name
            else:
                pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            # 读取现有数据
            existing_data = {}
            if list_file.exists():
                with open_file(list_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            # 如果奖品权重没有新增
            existing_weights = []
            for item_name, item_info in existing_data.items():
                if "weight" in item_info and item_info["weight"] is not None:
                    # 只比较权重值
                    existing_weights.append(str(item_info["weight"]))

            if set(lines) == set(existing_weights):
                # 显示提示消息
                config = NotificationConfig(
                    title=get_content_name_async("weight_setting", "info_title"),
                    content=get_content_name_async(
                        "weight_setting", "no_new_weights_message"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)
                return

            # 更新现有数据中的奖品权重信息
            updated_data = existing_data.copy()

            # 获取现有奖品列表（按顺序）
            existing_items = list(existing_data.keys())

            # 按顺序分配权重值给奖品
            for i, line in enumerate(lines):
                if i < len(existing_items):  # 确保不超过现有奖品数量
                    try:
                        weight_val = float(line.strip())
                        item_name = existing_items[i]
                        updated_data[item_name]["weight"] = weight_val
                    except ValueError:
                        # 如果无法转换为浮点数，跳过这一行
                        continue

            # 保存到文件
            with open_file(list_file, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=4)

            # 显示保存成功通知
            config = NotificationConfig(
                title=get_content_name_async("weight_setting", "success_title"),
                content=get_content_name_async(
                    "weight_setting", "success_message"
                ).format(count=len(lines)),
                duration=3000,
            )
            show_notification(NotificationType.SUCCESS, config, parent=self)

            # 更新初始奖品权重列表
            self.initial_weights = lines.copy()

            # 标记为已保存
            self.saved = True

        except Exception as e:
            # 显示错误消息
            config = NotificationConfig(
                title=get_content_name_async("weight_setting", "error_title"),
                content=f"{get_content_name_async('weight_setting', 'save_error')}: {str(e)}",
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            logger.exception(f"保存奖品权重失败: {e}")

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
                get_content_name_async("weight_setting", "unsaved_changes_title"),
                get_content_name_async("weight_setting", "unsaved_changes_message"),
                self,
            )

            dialog.yesButton.setText(
                get_content_name_async("weight_setting", "discard_button")
            )
            dialog.cancelButton.setText(
                get_content_name_async("weight_setting", "continue_editing_button")
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
