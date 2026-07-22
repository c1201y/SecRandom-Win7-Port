"""
剩余名单页面
用于显示未抽取的学生名单
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from PySide2.QtCore import (
    Qt,
    QThread,
    QTimer,
    Signal,
)
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    ElevatedCardWidget,
    SubtitleLabel,
    ScrollArea,
)

from app.Language.obtain_language import (
    get_any_position_value_async,
    get_content_name_async,
)
from app.tools.config import read_drawn_record, read_drawn_record_simple
from app.tools.list_specific_settings_access import read_lottery_setting
from app.tools.path_utils import get_data_path, get_path
from app.tools.personalised import load_custom_font
from app.tools.variable import (
    APP_INIT_DELAY,
    STUDENT_CARD_FIXED_HEIGHT,
    STUDENT_CARD_FIXED_WIDTH,
    STUDENT_CARD_MARGIN,
    STUDENT_CARD_SPACING,
)
from app.view.components.center_flow_layout import CenterFlowLayout


class StudentLoader(QThread):
    """在后台线程中加载并预处理学生数据。"""

    finished = Signal(list)

    def __init__(
        self,
        students_file: str,
        class_name: str,
        group_index: int,
        gender_index: int,
        group_filter: str,
        gender_filter: str,
        half_repeat: int,
        source: str,
        info_template: Optional[str],
    ) -> None:
        super().__init__()
        self._students_file = get_path(students_file)
        self._class_name = class_name
        self._is_lottery = source == "lottery"
        if self._is_lottery:
            self._group_index = 0
            self._gender_index = 0
            self._group_filter = ""
            self._gender_filter = ""
        else:
            self._group_index = int(group_index or 0)
            self._gender_index = int(gender_index or 0)
            self._group_filter = group_filter or ""
            self._gender_filter = gender_filter or ""
        self._half_repeat = max(0, int(half_repeat or 0))
        self._info_template = info_template or "{id} {gender} {group}"

    def run(self) -> None:
        """执行完整的数据准备流程。"""
        try:
            students = self._load_students()
            if self.isInterruptionRequested():
                return

            students = self._apply_group_filter(students)
            if self.isInterruptionRequested():
                return

            students = self._apply_gender_filter(students)
            if self.isInterruptionRequested():
                return

            students = self._apply_half_repeat(students)
            if self.isInterruptionRequested():
                return

            if self._is_lottery:
                for idx, student in enumerate(students, start=1):
                    student["index"] = idx
                    quantity = student.get("remaining_units", None)
                    if isinstance(quantity, int):
                        student["quantity"] = quantity
                        continue
                    try:
                        student["quantity"] = int(student.get("count", 1) or 0)
                    except Exception:
                        student["quantity"] = 1

            prepared = [self._prepare_student(student) for student in students]
        except Exception as exc:
            logger.exception("Failed to process remaining students: {}", exc)
            prepared = []

        self.finished.emit(prepared)

    def _load_students(self) -> List[Dict[str, Any]]:
        with open(self._students_file, "r", encoding="utf-8") as src:
            raw_data = json.load(src)

        students: List[Dict[str, Any]] = []
        for name, payload in raw_data.items():
            exist = payload.get("exist", True)
            if not exist:
                continue
            raw_count = payload.get("count", 1)
            try:
                count = int(raw_count)
            except Exception:
                count = 1
            if count < 0:
                count = 0
            students.append(
                {
                    "id": payload.get("id", ""),
                    "name": name,
                    "gender": payload.get("gender", ""),
                    "group": payload.get("group", ""),
                    "exist": exist,
                    "count": count,
                    "weight": payload.get("weight", 1),
                }
            )
        students.sort(key=lambda item: item.get("name", ""))
        return students

    def _apply_group_filter(
        self, students: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if self._group_index <= 0:
            return list(students)

        if self._group_index == 1:
            group_data: Dict[str, List[Dict[str, Any]]] = {}
            for student in students:
                group_name = student.get("group", "")
                if not group_name:
                    continue
                group_data.setdefault(group_name, []).append(student)

            result: List[Dict[str, Any]] = []
            for group_name in sorted(group_data):
                members = sorted(
                    group_data[group_name], key=lambda item: item.get("name", "")
                )
                result.append(
                    {
                        "id": f"GROUP_{group_name}",
                        "name": f"小组 {group_name}",
                        "gender": "",
                        "group": group_name,
                        "exist": True,
                        "is_group": True,
                        "members": members,
                    }
                )
            return result

        sorted_groups = sorted(
            {student.get("group", "") for student in students if student.get("group")}
        )
        target_index = self._group_index - 2
        if 0 <= target_index < len(sorted_groups):
            selected = sorted_groups[target_index]
            return [
                student for student in students if student.get("group", "") == selected
            ]
        return []

    def _apply_gender_filter(
        self, students: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if self._gender_index <= 0:
            return students

        genders = sorted(
            {student.get("gender", "") for student in students if student.get("gender")}
        )
        target_index = self._gender_index - 1
        if 0 <= target_index < len(genders):
            selected = genders[target_index]
            return [
                student for student in students if student.get("gender", "") == selected
            ]
        return []

    def _apply_half_repeat(
        self, students: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        try:
            if self._is_lottery:
                draw_type = 0
                try:
                    draw_type = int(
                        read_lottery_setting(self._class_name, "draw_type", 0) or 0
                    )
                except Exception:
                    draw_type = 0

                draw_mode = 0
                try:
                    draw_mode = int(
                        read_lottery_setting(self._class_name, "draw_mode", 0) or 0
                    )
                except Exception:
                    draw_mode = 0

                half_repeat = 1
                try:
                    half_repeat = int(
                        read_lottery_setting(self._class_name, "half_repeat", 1) or 1
                    )
                except Exception:
                    half_repeat = 1

                drawn_records = read_drawn_record_simple(self._class_name)
            else:
                drawn_records = read_drawn_record(
                    self._class_name, self._gender_filter, self._group_filter
                )
        except Exception as exc:
            logger.exception("Failed to read drawn records: {}", exc)
            drawn_records = []

        drawn_counts = {name: count for name, count in drawn_records}

        if self._is_lottery:
            if draw_type == 1:
                filtered: List[Dict[str, Any]] = []
                for student in students:
                    name = str(student.get("name", "") or "")
                    try:
                        base_limit = int(student.get("count", 1) or 0)
                    except Exception:
                        base_limit = 1
                    if base_limit <= 0:
                        continue

                    try:
                        drawn = int(drawn_counts.get(name, 0) or 0)
                    except Exception:
                        drawn = 0
                    remaining_units = base_limit - drawn
                    if remaining_units <= 0:
                        continue
                    item = dict(student)
                    item["remaining_units"] = remaining_units
                    filtered.append(item)
                filtered.sort(key=lambda item: item.get("name", ""))
                return filtered

            if draw_mode == 0:
                return students
            if draw_mode == 1:
                threshold = 1
            else:
                threshold = max(1, half_repeat)

            remaining: List[Dict[str, Any]] = []
            for student in students:
                name = student.get("name", "")
                if drawn_counts.get(name, 0) < threshold:
                    remaining.append(student)
            return remaining

        if self._half_repeat <= 0:
            return students

        remaining: List[Dict[str, Any]] = []
        for student in students:
            if student.get("is_group"):
                members = student.get("members", [])
                has_remaining = any(
                    drawn_counts.get(member.get("name", ""), 0) < self._half_repeat
                    for member in members
                )
                if has_remaining:
                    remaining.append(student)
            else:
                name = student.get("name", "")
                if drawn_counts.get(name, 0) < self._half_repeat:
                    remaining.append(student)
        return remaining

    def _prepare_student(self, student: Dict[str, Any]) -> Dict[str, Any]:
        prepared = dict(student)
        if prepared.get("is_group"):
            members = prepared.get("members", [])
            prepared["members_count"] = len(members)
            prepared["members_text_pre"] = self._format_members_text(members)
        else:
            prepared["info_text_pre"] = self._format_info_text(prepared)
        return prepared

    def _format_members_text(self, members: List[Dict[str, Any]]) -> str:
        names = [member.get("name", "") for member in members[:5] if member.get("name")]
        summary = "、".join(names)
        if len(members) > 5:
            summary += get_content_name_async("remaining_list", "group_summary").format(
                members=len(members) - 5
            )
        return summary

    def _format_info_text(self, student: Dict[str, Any]) -> str:
        try:
            return self._info_template.format(
                id=student.get("id", ""),
                gender=student.get("gender", ""),
                group=student.get("group", ""),
                index=student.get("index", ""),
                quantity=student.get("quantity", ""),
            )
        except Exception:
            return " ".join(
                filter(
                    None,
                    [
                        student.get("id", ""),
                        student.get("gender", ""),
                        student.get("group", ""),
                    ],
                )
            )


class RemainingListPage(QWidget):
    """剩余名单页面类"""

    count_changed = Signal(int)

    def __init__(
        self, parent: Optional[QWidget] = None, source: str = "roll_call"
    ) -> None:
        super().__init__(parent)
        self._closing = False
        self.class_name = ""
        self.group_filter = ""
        self.gender_filter = ""
        self.half_repeat = 0
        self.group_index = 0
        self.gender_index = 0
        self.source = source
        self.students: List[Dict[str, Any]] = []
        self.cards: List[ElevatedCardWidget] = []
        self._loading_thread: Optional[StudentLoader] = None

        self._load_timer = QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self.load_data)
        self._load_timer.start(APP_INIT_DELAY)

        # 布局状态
        self._last_layout_width = 0
        self._last_card_count = 0
        self._layout_update_in_progress = False
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_update_layout)

        # 缓存资源
        try:
            self._font_family = load_custom_font()
        except Exception as exc:
            logger.exception("Failed to load custom font: {}", exc)
            self._font_family = None

        self._student_info_text: Optional[str] = None
        self._lottery_info_text: Optional[str] = None
        self._title_with_class_template: Optional[str] = None
        self._count_label_template: Optional[str] = None

        self.init_ui()

    # ------------------------------------------------------------------
    # 生命周期管理
    # ------------------------------------------------------------------
    def stop_loader(self) -> None:
        if self._loading_thread is None:
            return
        try:
            try:
                self._loading_thread.finished.disconnect(self._on_students_loaded)
            except Exception:
                pass
            if self._loading_thread.isRunning():
                self._loading_thread.requestInterruption()
                self._loading_thread.wait(2000)
        except Exception as exc:
            logger.warning("Failed to stop loader thread cleanly: {}", exc)
        finally:
            # 确保线程对象被正确清理
            self._loading_thread = None

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._closing = True
        try:
            if self._load_timer.isActive():
                self._load_timer.stop()
        except Exception:
            pass
        try:
            if self._resize_timer.isActive():
                self._resize_timer.stop()
        except Exception:
            pass
        self.stop_loader()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def init_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        title_text = get_content_name_async("remaining_list", "title")
        # 根据来源选择不同的计数标签
        if self.source == "lottery":
            self._count_label_template = get_content_name_async(
                "remaining_list", "prizes_count_label"
            )
        else:
            self._count_label_template = get_content_name_async(
                "remaining_list", "count_label"
            )

        self._title_with_class_template = get_content_name_async(
            "remaining_list", "title_with_class"
        )

        self.title_label = SubtitleLabel(title_text)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(self._font_family or "", 18))
        self.main_layout.addWidget(self.title_label)

        self.count_label = BodyLabel(self._count_label_template.format(count=0))
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setFont(QFont(self._font_family or "", 12))
        self.main_layout.addWidget(self.count_label)

        # 滚动区域
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.main_layout.addWidget(self.scroll_area)

        # 滚动区域内部容器
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        # 流式布局
        self.flow_layout = CenterFlowLayout(self.scroll_content)
        self.flow_layout.setHorizontalSpacing(STUDENT_CARD_SPACING)
        self.flow_layout.setVerticalSpacing(STUDENT_CARD_SPACING)
        self.flow_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.flow_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_content.setLayout(self.flow_layout)

        try:
            self._student_info_text = get_any_position_value_async(
                "remaining_list", "student_info", "name"
            )
        except Exception:
            self._student_info_text = "{id} {gender} {group}"

        try:
            self._lottery_info_text = get_any_position_value_async(
                "remaining_list", "lottery_info", "name"
            )
        except Exception:
            self._lottery_info_text = "序号: {index}\n数量: {quantity}"

    # ------------------------------------------------------------------
    # 数据加载
    # ------------------------------------------------------------------
    def get_students_file(self) -> Optional[Path]:
        class_name = (self.class_name or "").strip()
        if not class_name:
            return None

        roll_call_list_dir = get_data_path("list", "roll_call_list")
        lottery_list_dir = get_data_path("list/lottery_list")

        # 根据source优先查找对应的文件
        if self.source == "lottery":
            lottery_file = lottery_list_dir / f"{class_name}.json"
            if lottery_file.exists():
                return lottery_file
            roll_file = roll_call_list_dir / f"{class_name}.json"
            if roll_file.exists():
                return roll_file
        else:
            roll_file = roll_call_list_dir / f"{class_name}.json"
            if roll_file.exists():
                return roll_file
            lottery_file = lottery_list_dir / f"{class_name}.json"
            if lottery_file.exists():
                return lottery_file

        logger.warning("未找到班级/奖池对应的名单文件: {}", class_name)
        return None

    def load_data(self) -> None:
        if self._closing:
            return
        if not self.class_name:
            logger.debug("跳过剩余名单加载：class_name 为空")
            return

        self.stop_loader()
        data_file = self.get_students_file()
        if not data_file:
            self.students = []
            self._clear_cards()
            self.count_label.setText(self._count_label_template.format(count=0))
            return

        loader = StudentLoader(
            str(data_file),
            self.class_name,
            self.group_index,
            self.gender_index,
            self.group_filter,
            self.gender_filter,
            self.half_repeat,
            self.source,
            self._lottery_info_text
            if self.source == "lottery"
            else self._student_info_text,
        )
        loader.finished.connect(self._on_students_loaded)
        loader.finished.connect(loader.deleteLater)
        self._loading_thread = loader
        loader.start()

    def _on_students_loaded(self, students_list: List[Dict[str, Any]]) -> None:
        if self._closing:
            self._loading_thread = None
            return
        self.students = list(students_list or [])
        self.update_ui()
        self.count_changed.emit(self._calculate_remaining_count())
        self._loading_thread = None

    # ------------------------------------------------------------------
    # UI 更新
    # ------------------------------------------------------------------
    def _ensure_templates(self) -> None:
        if not self._title_with_class_template:
            try:
                self._title_with_class_template = get_content_name_async(
                    "remaining_list", "title_with_class"
                )
            except Exception:
                self._title_with_class_template = "{class_name}"
        # 总是根据source更新计数标签模板
        if self.source == "lottery":
            self._count_label_template = get_content_name_async(
                "remaining_list", "prizes_count_label"
            )
        else:
            self._count_label_template = get_content_name_async(
                "remaining_list", "count_label"
            )

    def _calculate_remaining_count(self) -> int:
        if not self.students:
            return 0
        if self.source == "lottery" and any(
            isinstance(student.get("remaining_units"), int) for student in self.students
        ):
            total = 0
            for student in self.students:
                try:
                    total += int(student.get("remaining_units", 0) or 0)
                except Exception:
                    pass
            return total
        if any(student.get("is_group", False) for student in self.students):
            total = 0
            for student in self.students:
                if student.get("is_group"):
                    total += student.get("members_count") or len(
                        student.get("members", [])
                    )
                else:
                    total += 1
            return total
        return len(self.students)

    def update_ui(self) -> None:
        self._ensure_templates()
        self.title_label.setText(
            self._title_with_class_template.format(class_name=self.class_name or "")
        )
        remaining_count = self._calculate_remaining_count()
        self.count_label.setText(
            self._count_label_template.format(count=remaining_count)
        )

        # 清空现有卡片
        self._clear_cards()

        # 创建卡片
        for student in self.students:
            card = self._create_student_card(student)
            if card:
                self.cards.append(card)

        # 更新布局
        self._update_grid_layout()

    def _clear_cards(self) -> None:
        for card in self.cards:
            try:
                card.hide()
                card.deleteLater()
            except Exception:
                pass
        self.cards.clear()

        if hasattr(self, "flow_layout") and self.flow_layout is not None:
            self.flow_layout.removeAllWidgets()

    def _update_grid_layout(self) -> None:
        if not self.cards:
            return

        if not hasattr(self, "flow_layout") or self.flow_layout is None:
            return

        self.flow_layout.removeAllWidgets()
        for card in self.cards:
            self.flow_layout.addWidget(card)
            card.show()

        self._last_layout_width = self.scroll_area.width()
        self._last_card_count = len(self.cards)

    def _create_student_card(
        self, student: Dict[str, Any]
    ) -> Optional[ElevatedCardWidget]:
        """创建学生卡片"""
        is_group = student.get("is_group", False)

        card = ElevatedCardWidget()
        card.setProperty("is_group", is_group)

        if is_group:
            card.setMinimumSize(STUDENT_CARD_FIXED_WIDTH, 0)
            card.setMaximumSize(STUDENT_CARD_FIXED_WIDTH, 500)
            layout = QVBoxLayout(card)
            layout.setContentsMargins(
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
            )
            layout.setSpacing(8)

            # 小组名称
            name_label = BodyLabel(student["name"])
            if self._font_family:
                name_label.setFont(QFont(self._font_family, 16, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            layout.addWidget(name_label)

            # 成员数量
            members = student.get("members", [])
            count_label = BodyLabel(f"成员数量: {len(members)}")
            if self._font_family:
                count_label.setFont(QFont(self._font_family, 10))
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(count_label)

            # 成员列表
            members_text = student.get("members_text_pre", "")
            if not members_text and members:
                members_names = [member.get("name", "") for member in members[:5]]
                members_text = "、".join(members_names)
                if len(members) > 5:
                    members_text += f" 等{len(members) - 5}名成员"

            members_label = BodyLabel(members_text)
            if self._font_family:
                members_label.setFont(QFont(self._font_family, 9))
            members_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            members_label.setWordWrap(True)
            layout.addWidget(members_label)
        else:
            card.setFixedSize(STUDENT_CARD_FIXED_WIDTH, STUDENT_CARD_FIXED_HEIGHT)

            layout = QVBoxLayout(card)
            layout.setContentsMargins(
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
                STUDENT_CARD_MARGIN,
            )
            layout.setSpacing(5)

            # 学生姓名
            name_label = BodyLabel(student.get("name", ""))
            if self._font_family:
                name_label.setFont(QFont(self._font_family, 14))
            else:
                name_label.setFont(QFont("", 14))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(name_label)

            # 学生信息
            info_text = student.get("info_text_pre", "")
            if not info_text:
                if self.source == "lottery":
                    template = (
                        self._lottery_info_text or "序号: {index}\n数量: {quantity}"
                    )
                else:
                    template = self._student_info_text or "{id} {gender} {group}"
                try:
                    info_text = template.format(
                        id=student.get("id", ""),
                        gender=student.get("gender", ""),
                        group=student.get("group", ""),
                        index=student.get("index", ""),
                        quantity=student.get("quantity", ""),
                    )
                except Exception:
                    info_text = f"{student.get('id', '')} {student.get('gender', '')} {student.get('group', '')}"

            info_label = BodyLabel(info_text)
            if self._font_family:
                info_label.setFont(QFont(self._font_family, 9))
            else:
                info_label.setFont(QFont("", 9))
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)

        return card

    # ------------------------------------------------------------------
    # 窗口大小处理
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:  # type: ignore[override]
        new_size = event.size()
        old_size = event.oldSize()

        if new_size == old_size:
            return

        width_change = abs(new_size.width() - self._last_layout_width)
        if width_change < 5:
            return

        if self._resize_timer is not None:
            self._resize_timer.stop()
        self._resize_timer.start(200)
        super().resizeEvent(event)

    def _delayed_update_layout(self) -> None:
        try:
            if self.isVisible() and self.cards:
                self._update_grid_layout()
        except RuntimeError as e:
            logger.exception(f"延迟布局更新错误: {e}")

    # ------------------------------------------------------------------
    # 外部接口
    # ------------------------------------------------------------------
    def update_remaining_list(
        self,
        class_name: str,
        group_filter: str,
        gender_filter: str,
        half_repeat: int = 0,
        group_index: int = 0,
        gender_index: int = 0,
        emit_signal: bool = True,
        source: str = "roll_call",
    ) -> None:
        self.class_name = class_name
        self.group_filter = group_filter
        self.gender_filter = gender_filter
        self.half_repeat = half_repeat
        self.group_index = group_index
        self.gender_index = gender_index
        self.source = source
        self._last_layout_width = 0
        self._last_card_count = 0
        self.load_data()

    def refresh(self) -> None:
        if self.class_name:
            self._last_layout_width = 0
            self._last_card_count = 0
            self.load_data()

    def on_count_changed(self, count: int) -> None:  # noqa: ARG002
        if self.class_name:
            self.load_data()

    def set_source(self, source: str) -> None:
        """全局设置source参数"""
        self.source = source
        # 更新模板以匹配新的source
        self._ensure_templates()
        # 重新加载数据
        if self.class_name:
            self.load_data()
