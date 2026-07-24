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


class SetPoolNameWindow(QWidget):
    """奖池名称设置窗口"""

    def __init__(self, parent=None):
        """初始化奖池名称设置窗口"""
        super().__init__(parent)

        # 初始化变量
        self.saved = False
        self.initial_pool_names = []  # 保存初始加载的奖池列表

        # 初始化UI
        self.init_ui()

        # 连接信号
        self.__connect_signals()

    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(get_content_name_async("set_prize_name", "title"))

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 创建标题
        self.title_label = TitleLabel(get_content_name_async("set_prize_name", "title"))
        self.main_layout.addWidget(self.title_label)

        # 创建说明标签
        self.description_label = BodyLabel(
            get_content_name_async("set_prize_name", "description")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        # 创建奖池名称输入区域
        self.__create_pool_name_input_area()

        # 创建按钮区域
        self.__create_button_area()

        # 添加伸缩项
        self.main_layout.addStretch(1)

    def __create_pool_name_input_area(self):
        """创建奖池名称输入区域"""
        # 创建卡片容器
        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)

        # 创建输入区域标题
        input_title = SubtitleLabel(
            get_content_name_async("set_prize_name", "input_title")
        )
        input_layout.addWidget(input_title)

        # 创建文本编辑框
        self.text_edit = PlainTextEdit()
        self.text_edit.setPlaceholderText(
            get_content_name_async("set_prize_name", "input_placeholder")
        )

        # 加载现有奖池名称
        try:
            pool_names = get_pool_name_list()
            if pool_names:
                self.text_edit.setPlainText("\n".join(pool_names))
                self.initial_pool_names = pool_names.copy()  # 保存初始奖池列表
        except Exception as e:
            logger.exception(f"加载奖池名称失败: {str(e)}")
            self.initial_pool_names = []  # 出错时设为空列表

        input_layout.addWidget(self.text_edit)

        # 添加到主布局
        self.main_layout.addWidget(input_card)

    def __create_button_area(self):
        """创建按钮区域"""
        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 伸缩项
        button_layout.addStretch(1)

        # 保存按钮
        self.save_button = PrimaryPushButton(
            get_content_name_async("set_prize_name", "save_button")
        )
        self.save_button.setIcon(FluentIcon.SAVE)
        button_layout.addWidget(self.save_button)

        # 添加到主布局
        self.main_layout.addLayout(button_layout)

    def __connect_signals(self):
        """连接信号与槽"""
        self.save_button.clicked.connect(self.__save_pool_names)
        self.text_edit.textChanged.connect(self.__on_text_changed)  # 添加文本变化监听

    def __on_text_changed(self):
        """检测文本变化，提示奖池消失"""
        try:
            # 获取当前文本编辑框中的奖池名称
            current_text = self.text_edit.toPlainText().strip()
            current_pool_names = (
                [name.strip() for name in current_text.split("\n") if name.strip()]
                if current_text
                else []
            )

            # 检查是否有奖池消失（存在于初始列表但不存在于当前列表）
            disappeared_pools = [
                name
                for name in self.initial_pool_names
                if name not in current_pool_names
            ]

            # 如果有奖池消失，显示提示
            if disappeared_pools:
                if len(disappeared_pools) == 1:
                    # 单个奖池消失
                    message = get_content_name_async(
                        "set_prize_name", "prize_disappeared_message"
                    ).format(prize_name=disappeared_pools[0])
                else:
                    # 多个奖池消失
                    message = get_content_name_async(
                        "set_prize_name", "multiple_prizes_disappeared_message"
                    ).format(
                        count=len(disappeared_pools),
                        prize_names="\n".join(disappeared_pools),
                    )

                # 显示提示
                config = NotificationConfig(
                    title=get_content_name_async(
                        "set_prize_name", "prize_disappeared_title"
                    ),
                    content=message,
                    duration=3000,
                )
                show_notification(NotificationType.WARNING, config, parent=self)

                # 更新初始奖池列表为当前列表，避免重复提示
                self.initial_pool_names = current_pool_names.copy()
        except Exception as e:
            logger.exception(f"检测奖池变化失败: {e}")

    def __save_pool_names(self):
        """保存奖池名称"""
        try:
            # 获取输入的奖池名称
            pool_names_text = self.text_edit.toPlainText().strip()

            # 分割奖池名称
            pool_names = [
                name.strip() for name in pool_names_text.split("\n") if name.strip()
            ]

            # 验证奖池名称
            invalid_names = []
            for name in pool_names:
                # 检查是否包含非法字符
                if re.search(r'[\/:*?"<>|]', name):
                    invalid_names.append(name)
                # 检查是否为保留字
                elif name.lower() == "pool":
                    invalid_names.append(name)

            if invalid_names:
                # 显示错误消息
                config = NotificationConfig(
                    title=get_content_name_async("set_prize_name", "error_title"),
                    content=get_content_name_async(
                        "set_prize_name", "invalid_names_error"
                    ).format(names=", ".join(invalid_names)),
                    duration=5000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            duplicate_names = get_duplicate_names(pool_names)
            if duplicate_names:
                dialog = Dialog(
                    get_content_name_async("set_prize_name", "duplicate_names_title"),
                    get_content_name_async(
                        "set_prize_name", "duplicate_names_message"
                    ).format(
                        count=len(duplicate_names),
                        names="\n".join(duplicate_names),
                    ),
                    self,
                )
                dialog.yesButton.setText(
                    get_content_name_async(
                        "set_prize_name", "duplicate_names_rename_button"
                    )
                )
                dialog.cancelButton.setText(
                    get_content_name_async(
                        "set_prize_name", "duplicate_names_edit_button"
                    )
                )
                if dialog.exec():
                    pool_names, _ = make_unique_names(pool_names)
                    self.text_edit.setPlainText("\n".join(pool_names))
                else:
                    return

            # 获取奖池名单目录
            lottery_list_dir = get_data_path("list", "lottery_list")
            lottery_list_dir.mkdir(parents=True, exist_ok=True)

            # 获取现有的奖池名称
            existing_pool_names = get_pool_name_list()

            # 检查是否有被删除的奖池
            deleted_pools = [
                name for name in existing_pool_names if name not in pool_names
            ]

            # 如果有被删除的奖池，询问用户是否确认删除
            if deleted_pools:
                # 创建确认对话框
                if len(deleted_pools) == 1:
                    # 单个奖池删除
                    dialog = MessageBox(
                        get_content_name_async("set_prize_name", "delete_prize_title"),
                        get_content_name_async(
                            "set_prize_name", "delete_prize_message"
                        ).format(prize_name=deleted_pools[0]),
                        self,
                    )

                    dialog.yesButton.setText(
                        get_content_name_async("set_prize_name", "delete_prize_button")
                    )
                    dialog.cancelButton.setText(
                        get_content_name_async("set_prize_name", "delete_cancel_button")
                    )
                else:
                    # 多个奖池删除
                    dialog = MessageBox(
                        get_content_name_async(
                            "set_prize_name", "delete_multiple_prizes_title"
                        ),
                        get_content_name_async(
                            "set_prize_name", "delete_multiple_prizes_message"
                        ).format(
                            count=len(deleted_pools),
                            prize_names="\n".join(deleted_pools),
                        ),
                        self,
                    )

                    dialog.yesButton.setText(
                        get_content_name_async("set_prize_name", "delete_prize_button")
                    )
                    dialog.cancelButton.setText(
                        get_content_name_async("set_prize_name", "delete_cancel_button")
                    )

                # 显示对话框并获取用户选择
                if dialog.exec():
                    # 用户确认删除，删除奖池文件
                    deleted_count = 0
                    for pool_name in deleted_pools:
                        pool_file = lottery_list_dir / f"{pool_name}.json"
                        if pool_file.exists():
                            pool_file.unlink()
                            deleted_count += 1

                        # 删除对应的抽奖历史记录
                        from app.common.history import get_history_file_path

                        history_file_path = get_history_file_path("lottery", pool_name)
                        if history_file_path.exists():
                            history_file_path.unlink()
                            logger.info(f"已删除奖池 '{pool_name}' 的抽奖历史记录")

                    # 显示删除成功消息
                    if deleted_count > 0:
                        config = NotificationConfig(
                            title=get_content_name_async(
                                "set_prize_name", "delete_success_title"
                            ),
                            content=get_content_name_async(
                                "set_prize_name", "delete_success_message"
                            ).format(count=deleted_count),
                            duration=3000,
                        )
                        show_notification(NotificationType.SUCCESS, config, parent=self)
                else:
                    # 用户取消删除，不执行任何操作
                    return

            # 创建或更新奖池文件
            created_count = 0
            for pool_name in pool_names:
                pool_file = lottery_list_dir / f"{pool_name}.json"
                if not pool_file.exists():
                    # 创建空的奖池文件
                    with open_file(pool_file, "w", encoding="utf-8") as f:
                        json.dump({}, f, ensure_ascii=False, indent=4)
                    created_count += 1

            # 显示成功消息
            if created_count > 0:
                config = NotificationConfig(
                    title=get_content_name_async("set_prize_name", "success_title"),
                    content=get_content_name_async(
                        "set_prize_name", "success_message"
                    ).format(count=created_count),
                    duration=3000,
                )
                show_notification(NotificationType.SUCCESS, config, parent=self)
            elif not deleted_pools:
                # 没有创建新奖池也没有删除奖池
                config = NotificationConfig(
                    title=get_content_name_async("set_prize_name", "info_title"),
                    content=get_content_name_async(
                        "set_prize_name", "no_new_prizes_message"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)

            # 标记为已保存
            self.saved = True

        except Exception as e:
            # 显示错误消息
            config = NotificationConfig(
                title=get_content_name_async("set_prize_name", "error_title"),
                content=f"{get_content_name_async('set_prize_name', 'save_error')}: {str(e)}",
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            logger.exception(f"保存奖池名称失败: {e}")

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
                get_content_name_async("set_prize_name", "unsaved_changes_title"),
                get_content_name_async("set_prize_name", "unsaved_changes_message"),
                self,
            )

            dialog.yesButton.setText(
                get_content_name_async("set_prize_name", "discard_button")
            )
            dialog.cancelButton.setText(
                get_content_name_async("set_prize_name", "continue_editing_button")
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
