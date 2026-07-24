from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any

from loguru import logger
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy
from PySide2.QtWidgets import QTableWidgetItem
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    Dialog,
    FluentIcon,
    PrimaryPushButton,
    TableWidget,
    TitleLabel,
)

from app.Language.obtain_language import get_content_name_async
from app.tools.config import NotificationConfig, NotificationType, show_notification
from app.tools.path_utils import get_data_path, open_file
from app.tools.settings_access import readme_settings_async


class PrizeTagSettingWindow(QWidget):
    def __init__(self, parent=None, list_name: str | None = None):
        super().__init__(parent)
        self.list_name = list_name
        self.saved = False
        self._loading = False
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._init_ui()
        self._load_data()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.setWindowTitle(get_content_name_async("prize_tag_setting", "title"))

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("prize_tag_setting", "title")
        )
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_name_async("prize_tag_setting", "description")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            get_content_name_async("prize_tag_setting", "header_labels")
        )
        self.table.verticalHeader().hide()
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().resizeSection(0, 80)
        self.table.horizontalHeader().resizeSection(1, 220)
        self.table.setMinimumHeight(200)
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

        card_layout.addWidget(self.table, 1)
        self.main_layout.addWidget(card, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        self.save_button = PrimaryPushButton(
            get_content_name_async("prize_tag_setting", "save_button")
        )
        self.save_button.setIcon(FluentIcon.SAVE)
        button_layout.addWidget(self.save_button)
        self.main_layout.addLayout(button_layout)

        self.main_layout.setStretchFactor(card, 1)

    def _connect_signals(self) -> None:
        self.save_button.clicked.connect(self._save)

    def _split_tags(self, raw: str) -> list[str]:
        raw = str(raw or "").strip()
        if not raw or raw.lower() == "nan":
            return []
        for sep in ["，", ",", "；", ";", "|", "/", "\\", "\n", "\t"]:
            raw = raw.replace(sep, " ")
        tags: list[str] = []
        for item in raw.split(" "):
            item = item.strip()
            if item and item not in tags:
                tags.append(item)
        return tags

    def _get_pool_name(self) -> str:
        if self.list_name:
            return str(self.list_name or "").strip()
        return str(
            readme_settings_async("lottery_list", "select_pool_name") or ""
        ).strip()

    def _get_list_file(self):
        pool_name = self._get_pool_name()
        return get_data_path("list/lottery_list") / f"{pool_name}.json"

    def _load_data(self) -> None:
        pool_name = self._get_pool_name()
        if not pool_name:
            self._data = OrderedDict()
            self._render_table()
            return

        list_file = self._get_list_file()
        if not list_file.exists():
            self._data = OrderedDict()
            self._render_table()
            return

        try:
            with open_file(list_file, "r", encoding="utf-8") as f:
                raw = json.load(f, object_pairs_hook=OrderedDict)
            self._data = raw if isinstance(raw, OrderedDict) else OrderedDict(raw)
        except Exception as e:
            logger.exception(f"加载奖品标签失败: {e}")
            self._data = OrderedDict()
        self._render_table()

    def _render_table(self) -> None:
        self._loading = True
        try:
            self.table.setRowCount(0)
            rows = []
            for name, info in self._data.items():
                if not isinstance(info, dict):
                    continue
                rows.append((name, info))

            self.table.setRowCount(len(rows))
            for row, (name, info) in enumerate(rows):
                raw_id = info.get("id", "")
                raw_tags = info.get("tags", [])
                tags_text = (
                    ", ".join([str(t).strip() for t in raw_tags if str(t).strip()])
                    if isinstance(raw_tags, list)
                    else str(raw_tags or "")
                )

                id_item = QTableWidgetItem(str(raw_id))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, id_item)

                name_item = QTableWidgetItem(str(name))
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, name_item)

                tag_item = QTableWidgetItem(tags_text)
                tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, tag_item)
        finally:
            self._loading = False

    def _save(self) -> None:
        try:
            pool_name = self._get_pool_name()
            if not pool_name:
                config = NotificationConfig(
                    title=get_content_name_async("prize_tag_setting", "error_title"),
                    content=get_content_name_async(
                        "prize_tag_setting", "no_list_selected"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.WARNING, config, parent=self)
                return

            list_file = self._get_list_file()
            if not list_file.exists():
                config = NotificationConfig(
                    title=get_content_name_async("prize_tag_setting", "error_title"),
                    content=get_content_name_async(
                        "prize_tag_setting", "list_file_missing"
                    ),
                    duration=3000,
                )
                show_notification(NotificationType.ERROR, config, parent=self)
                return

            try:
                with open_file(list_file, "r", encoding="utf-8") as f:
                    existing = json.load(f, object_pairs_hook=OrderedDict)
                if not isinstance(existing, OrderedDict):
                    existing = OrderedDict(existing)
            except Exception:
                existing = OrderedDict()

            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 1)
                tags_item = self.table.item(row, 2)
                if not name_item or not tags_item:
                    continue
                name = str(name_item.text() or "").strip()
                if not name or name not in existing:
                    continue
                info = existing.get(name)
                if not isinstance(info, dict):
                    continue
                info["tags"] = self._split_tags(tags_item.text())

            with open_file(list_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=4)

            config = NotificationConfig(
                title=get_content_name_async("prize_tag_setting", "success_title"),
                content=get_content_name_async("prize_tag_setting", "success_message"),
                duration=3000,
            )
            show_notification(NotificationType.SUCCESS, config, parent=self)
            self.saved = True
        except Exception as e:
            config = NotificationConfig(
                title=get_content_name_async("prize_tag_setting", "error_title"),
                content=f"{get_content_name_async('prize_tag_setting', 'save_error')}: {str(e)}",
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            logger.exception(f"保存奖品标签失败: {e}")

    def closeEvent(self, event):
        if not self.saved:
            dialog = Dialog(
                get_content_name_async("prize_tag_setting", "unsaved_changes_title"),
                get_content_name_async("prize_tag_setting", "unsaved_changes_message"),
                self,
            )

            dialog.yesButton.setText(
                get_content_name_async("prize_tag_setting", "discard_button")
            )
            dialog.cancelButton.setText(
                get_content_name_async("prize_tag_setting", "continue_editing_button")
            )

            if dialog.exec():
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
