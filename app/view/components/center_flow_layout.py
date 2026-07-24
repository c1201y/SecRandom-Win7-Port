from __future__ import annotations

from PySide2.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QTimer,
)
from PySide2.QtWidgets import (
    QLayout,
    QLayoutItem,
    QWidget,
    QWidgetItem,
)


class CenterFlowLayout(QLayout):
    def __init__(self, parent: QWidget | None = None, needAni: bool | None = None):
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing: int = -1
        self._v_spacing: int = -1
        self._anim_duration: int = 300
        self._anim_easing = QEasingCurve.Linear
        self._need_ani: bool = bool(needAni) if needAni is not None else False
        self._anis: list[QPropertyAnimation] = []
        self._ani_group = QParallelAnimationGroup(self)
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(
            lambda: self._do_layout(self.geometry(), move=True)
        )
        self._w_parent: QObject | None = None
        self._is_installed_event_filter = False
        self._alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft

    def _resolve_parent_widget(self) -> QWidget | None:
        parent = self.parentWidget()
        if parent is not None:
            return parent
        obj = self.parent()
        while obj is not None:
            if isinstance(obj, QWidget):
                return obj
            obj = obj.parent()
        return None

    def _ensure_event_filter_installed(self, w: QWidget) -> None:
        if self._is_installed_event_filter:
            return
        try:
            p = w.parent()
            if p is not None:
                self._w_parent = p
                p.installEventFilter(self)
            else:
                w.installEventFilter(self)
            self._is_installed_event_filter = True
        except Exception:
            self._is_installed_event_filter = False

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if (
            obj in [it.widget() for it in self._items if it.widget() is not None]
            and event.type() == QEvent.Type.ParentChange
        ):
            try:
                self._w_parent = obj.parent()
                if self._w_parent is not None:
                    self._w_parent.installEventFilter(self)
                self._is_installed_event_filter = True
            except Exception:
                pass

        if obj == self._w_parent and event.type() == QEvent.Type.Show:
            self._do_layout(self.geometry(), move=True)
            self._is_installed_event_filter = True

        return super().eventFilter(obj, event)

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)
        self.invalidate()

    def addWidget(self, widget: QWidget) -> None:
        try:
            self.addChildWidget(widget)
        except Exception:
            pass
        self._ensure_event_filter_installed(widget)
        item = QWidgetItem(widget)
        self._items.append(item)
        self._on_widget_added(widget)
        self.invalidate()

    def _on_widget_added(self, widget: QWidget, index: int | None = None) -> None:
        if not self._need_ani:
            return
        ani = QPropertyAnimation(widget, b"geometry", self)
        ani.setEndValue(QRect(QPoint(0, 0), widget.size()))
        ani.setDuration(self._anim_duration)
        ani.setEasingCurve(self._anim_easing)
        widget.setProperty("flowAni", ani)
        self._ani_group.addAnimation(ani)
        if index is None:
            self._anis.append(ani)
        else:
            self._anis.insert(index, ani)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            w = item.widget()
            if w is not None:
                ani = w.property("flowAni")
                if isinstance(ani, QPropertyAnimation):
                    try:
                        self._anis.remove(ani)
                    except ValueError:
                        pass
                    try:
                        self._ani_group.removeAnimation(ani)
                    except Exception:
                        pass
                    ani.deleteLater()
            self.invalidate()
            return item
        return None

    def removeAllWidgets(self) -> None:
        while self._items:
            self.takeAt(0)

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), move=False)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        if self._need_ani:
            self._debounce_timer.start(80)
        else:
            self._do_layout(rect, move=True)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def horizontalSpacing(self) -> int:
        if self._h_spacing >= 0:
            return self._h_spacing
        return self.spacing()

    def verticalSpacing(self) -> int:
        if self._v_spacing >= 0:
            return self._v_spacing
        return self.spacing()

    def setHorizontalSpacing(self, spacing: int) -> None:
        self._h_spacing = spacing
        self.invalidate()

    def setVerticalSpacing(self, spacing: int) -> None:
        self._v_spacing = spacing
        self.invalidate()

    def setAlignment(self, alignment: Qt.AlignmentFlag | Qt.Alignment) -> None:
        self._alignment = Qt.AlignmentFlag(int(alignment))
        self.invalidate()

    def alignment(self) -> Qt.AlignmentFlag:
        return self._alignment

    def setAnimation(self, duration: int, easing_curve=QEasingCurve.Linear) -> None:
        self._anim_duration = int(duration) if duration is not None else 0
        self._anim_easing = (
            easing_curve if easing_curve is not None else QEasingCurve.Linear
        )
        for ani in self._anis:
            ani.setDuration(self._anim_duration)
            ani.setEasingCurve(self._anim_easing)
        self.invalidate()

    def setAnimationStyle(self, style: int) -> None:
        enabled = False if style is None else bool(int(style))
        if enabled == self._need_ani:
            return
        self._need_ani = enabled
        if not self._need_ani:
            try:
                self._ani_group.stop()
            except Exception:
                pass
            self.invalidate()
            return

        for i, item in enumerate(self._items):
            w = item.widget()
            if w is None:
                continue
            ani = w.property("flowAni")
            if not isinstance(ani, QPropertyAnimation):
                self._on_widget_added(w, index=i)
            else:
                if ani not in self._anis:
                    self._anis.insert(i, ani)
                try:
                    self._ani_group.addAnimation(ani)
                except Exception:
                    pass
        self.invalidate()

    def _build_lines(
        self, available_width: int
    ) -> list[tuple[list[tuple[int, QLayoutItem, QSize]], int, int]]:
        h_space = self.horizontalSpacing()
        lines: list[tuple[list[tuple[int, QLayoutItem, QSize]], int, int]] = []
        line_items: list[tuple[int, QLayoutItem, QSize]] = []
        line_width = 0
        line_height = 0

        for i, item in enumerate(self._items):
            item_size = item.sizeHint()
            next_width = (
                item_size.width() if not line_items else (h_space + item_size.width())
            )
            if line_items and (line_width + next_width > available_width):
                lines.append((line_items, line_height, line_width))
                line_items = []
                line_width = 0
                line_height = 0
                next_width = item_size.width()

            line_items.append((i, item, item_size))
            line_width += next_width
            line_height = max(line_height, item_size.height())

        if line_items:
            lines.append((line_items, line_height, line_width))

        return lines

    def _do_layout(self, rect: QRect, move: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(left, top, -right, -bottom)

        h_space = self.horizontalSpacing()
        v_space = self.verticalSpacing()

        lines = self._build_lines(effective.width())
        content_height = sum(line_height for _, line_height, _ in lines)
        if len(lines) > 1:
            content_height += v_space * (len(lines) - 1)

        if not move:
            return content_height + top + bottom

        extra_y = effective.height() - content_height
        if extra_y < 0:
            extra_y = 0

        align = self._alignment
        if align & Qt.AlignmentFlag.AlignVCenter:
            y = effective.y() + (extra_y // 2)
        elif align & Qt.AlignmentFlag.AlignBottom:
            y = effective.y() + extra_y
        else:
            y = effective.y()

        ani_restart = False
        for index, (line_items, line_height, line_width) in enumerate(lines):
            extra_x = effective.width() - line_width
            if extra_x < 0:
                extra_x = 0

            if align & Qt.AlignmentFlag.AlignHCenter:
                x_offset = extra_x // 2
            elif align & Qt.AlignmentFlag.AlignRight:
                x_offset = extra_x
            else:
                x_offset = 0

            cx = effective.x() + x_offset
            for i, item, item_size in line_items:
                target = QRect(QPoint(cx, y), item_size)
                if not self._need_ani:
                    item.setGeometry(target)
                else:
                    if 0 <= i < len(self._anis):
                        ani = self._anis[i]
                    else:
                        w = item.widget()
                        if w is not None:
                            self._on_widget_added(w, index=i)
                            ani = self._anis[i] if 0 <= i < len(self._anis) else None
                        else:
                            ani = None
                    if isinstance(ani, QPropertyAnimation) and target != ani.endValue():
                        ani.stop()
                        ani.setEndValue(target)
                        ani_restart = True
                cx += item_size.width() + h_space

            y += line_height
            if index != len(lines) - 1:
                y += v_space

        if self._need_ani and ani_restart:
            self._ani_group.stop()
            self._ani_group.start()

        return content_height + top + bottom
