import re
import json

from loguru import logger
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    Dialog,
    FluentIcon,
    PlainTextEdit,
    PrimaryPushButton,
    SubtitleLabel,
    TitleLabel,
)

from app.tools.path_utils import get_data_path, open_file
from app.tools.settings_access import readme_settings_async
from app.Language.obtain_language import get_content_name_async
from app.tools.config import NotificationConfig, NotificationType, show_notification


class PrizeCountSettingWindow(QWidget):
    def __init__(self, parent=None, list_name=None):
        super().__init__(parent)
        self.list_name = list_name
        self.saved = False
        self.initial_counts = []
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("count_setting", "title"))

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(get_content_name_async("count_setting", "title"))
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_name_async("count_setting", "description")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        self.__create_prize_count_input_area()
        self.__create_button_area()
        self.main_layout.addStretch(1)

    def __create_prize_count_input_area(self):
        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)

        input_title = SubtitleLabel(
            get_content_name_async("count_setting", "input_title")
        )
        input_layout.addWidget(input_title)

        self.text_edit = PlainTextEdit()
        self.text_edit.setPlaceholderText(
            get_content_name_async("count_setting", "input_placeholder")
        )

        existing_counts = self.__load_existing_counts()
        if existing_counts:
            self.text_edit.setPlainText("\n".join(existing_counts))

        input_layout.addWidget(self.text_edit)
        self.main_layout.addWidget(input_card)

    def __load_existing_counts(self):
        try:
            lottery_list_dir = get_data_path("list/lottery_list")

            if self.list_name:
                pool_name = self.list_name
            else:
                pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            if not list_file.exists():
                self.initial_counts = []
                return []

            with open_file(list_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            counts = []
            for _, item_info in data.items():
                raw_count = 1
                if isinstance(item_info, dict):
                    raw_count = item_info.get("count", 1)
                try:
                    count_value = int(raw_count)
                except Exception:
                    count_value = 1
                if count_value < 0:
                    count_value = 0
                counts.append(str(count_value))

            self.initial_counts = counts.copy()
            return counts
        except Exception as e:
            logger.exception(f"加载奖品数量失败: {str(e)}")
            self.initial_counts = []
            return []

    def __create_button_area(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.save_button = PrimaryPushButton(
            get_content_name_async("count_setting", "save_button")
        )
        self.save_button.setIcon(FluentIcon.SAVE)
        button_layout.addWidget(self.save_button)

        self.main_layout.addLayout(button_layout)

    def __connect_signals(self):
        self.save_button.clicked.connect(self.__save_counts)
        self.text_edit.textChanged.connect(self.__on_text_changed)

    def __on_text_changed(self):
        current_text = self.text_edit.toPlainText()
        current_counts = [
            count.strip() for count in current_text.split("\n") if count.strip()
        ]

        deleted_counts = [
            count for count in self.initial_counts if count not in current_counts
        ]
        if deleted_counts:
            for count in deleted_counts:
                config = NotificationConfig(
                    title=get_content_name_async(
                        "count_setting", "count_deleted_title"
                    ),
                    content=get_content_name_async(
                        "count_setting", "count_deleted_message"
                    ).format(count=count),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)

            self.initial_counts = current_counts.copy()

    def __save_counts(self):
        try:
            counts_text = self.text_edit.toPlainText().strip()
            if not counts_text:
                config = NotificationConfig(
                    title=get_content_name_async("count_setting", "error_title"),
                    content=get_content_name_async("count_setting", "no_counts_error"),
                    duration=3000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            lines = [line.strip() for line in counts_text.split("\n") if line.strip()]

            invalid_counts = []
            for line in lines:
                if re.search(r'[\/\:*?"<>|]', line):
                    invalid_counts.append(line)
                    continue
                try:
                    int(float(line))
                except Exception:
                    invalid_counts.append(line)

            if invalid_counts:
                config = NotificationConfig(
                    title=get_content_name_async("count_setting", "error_title"),
                    content=get_content_name_async(
                        "count_setting", "invalid_counts_error"
                    ).format(counts=", ".join(invalid_counts)),
                    duration=5000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            lottery_list_dir = get_data_path("list/lottery_list")
            lottery_list_dir.mkdir(parents=True, exist_ok=True)

            if self.list_name:
                pool_name = self.list_name
            else:
                pool_name = readme_settings_async("lottery_list", "select_pool_name")
            list_file = lottery_list_dir / f"{pool_name}.json"

            existing_data = {}
            if list_file.exists():
                with open_file(list_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            existing_counts = []
            for _, item_info in existing_data.items():
                if isinstance(item_info, dict):
                    existing_counts.append(str(item_info.get("count", 1)))
                else:
                    existing_counts.append("1")

            if set(lines) == set(existing_counts):
                config = NotificationConfig(
                    title=get_content_name_async("count_setting", "info_title"),
                    content=get_content_name_async(
                        "count_setting", "no_new_counts_message"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.INFO, config, parent=self)
                return

            updated_data = existing_data.copy()
            existing_items = list(existing_data.keys())

            for i, line in enumerate(lines):
                if i < len(existing_items):
                    try:
                        count_val = int(float(line.strip()))
                    except Exception:
                        continue
                    if count_val < 0:
                        count_val = 0
                    item_name = existing_items[i]
                    if isinstance(updated_data.get(item_name), dict):
                        updated_data[item_name]["count"] = count_val

            with open_file(list_file, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=4)

            config = NotificationConfig(
                title=get_content_name_async("count_setting", "success_title"),
                content=get_content_name_async(
                    "count_setting", "success_message"
                ).format(count=len(lines)),
                duration=3000,
            )
            show_notification(NotificationType.SUCCESS, config, parent=self)

            self.initial_counts = lines.copy()
            self.saved = True
        except Exception as e:
            config = NotificationConfig(
                title=get_content_name_async("count_setting", "error_title"),
                content=f"{get_content_name_async('count_setting', 'save_error')}: {str(e)}",
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            logger.exception(f"保存奖品数量失败: {e}")

    def __cancel(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()

    def closeEvent(self, event):
        if not self.saved:
            dialog = Dialog(
                get_content_name_async("count_setting", "unsaved_changes_title"),
                get_content_name_async("count_setting", "unsaved_changes_message"),
                self,
            )

            dialog.yesButton.setText(
                get_content_name_async("count_setting", "discard_button")
            )
            dialog.cancelButton.setText(
                get_content_name_async("count_setting", "continue_editing_button")
            )

            if dialog.exec():
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
