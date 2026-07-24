from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence, Tuple

from PySide2.QtCore import QEvent, QPoint, QRect, QRectF, QSize, Qt, Signal
from PySide2.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from qfluentwidgets import CheckBox
from qfluentwidgets.common.animation import TranslateYAnimation
from qfluentwidgets.common.font import setFont
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.common.icon import isDarkTheme
from qfluentwidgets.common.style_sheet import FluentStyleSheet
from qfluentwidgets.components.widgets.menu import MenuAnimationType, RoundMenu


@dataclass
class _CheckableComboItem:
    text: str
    user_data: Any = None
    is_enabled: bool = True
    is_checked: bool = False


class _CheckableMenuRow(QWidget):
    checkedChanged = Signal(bool)

    def __init__(
        self, text: str, checked: bool, enabled: bool, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._hover = False

        self.checkbox = CheckBox(text, self)
        self.checkbox.setChecked(bool(checked))
        self.checkbox.setEnabled(bool(enabled))
        self.checkbox.stateChanged.connect(self._on_state_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)
        layout.addWidget(self.checkbox, 1)

        self.setFixedHeight(33)

    def setChecked(self, checked: bool):
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(bool(checked))
        self.checkbox.blockSignals(False)
        self.update()

    def _on_state_changed(self, _state: int):
        self.checkedChanged.emit(bool(self.checkbox.isChecked()))
        self.update()

    def enterEvent(self, e):
        self._hover = True
        self.update()
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        return super().leaveEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        checked = bool(self.checkbox.isChecked())
        if isDarkTheme():
            hover_color = QColor(255, 255, 255, 18)
            checked_color = QColor(255, 255, 255, 26)
        else:
            hover_color = QColor(0, 0, 0, 10)
            checked_color = QColor(0, 0, 0, 18)

        if checked or self._hover:
            c = checked_color if checked else hover_color
            r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawRoundedRect(r, 6, 6)

        return super().paintEvent(e)


class MultiSelectionComboBox(QPushButton):
    checkedDataChanged = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None, minimum_checked: int = 0):
        super().__init__(parent=parent)
        self.arrowAni = TranslateYAnimation(self)
        self.isHover = False
        self.isPressed = False
        self._items: List[_CheckableComboItem] = []
        self._minimum_checked = int(max(0, minimum_checked))
        self._placeholder_text = ""
        self._placeholder_active = True
        self._menu: Optional[RoundMenu] = None
        self._chip_close_hitboxes: List[Tuple[QRect, int]] = []
        self._ignore_release_toggle = False

        FluentStyleSheet.COMBO_BOX.apply(self)
        setFont(self)
        self.installEventFilter(self)
        super().setText("")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(33)
        self.setMinimumWidth(0)

    def sizeHint(self):
        base = super().sizeHint()
        h = 33
        try:
            fm = QFontMetrics(self.font())
            if self._placeholder_active:
                t = self._placeholder_text
            else:
                selected = self.checkedTexts()
                t = "、".join(selected[:3])
            tw = fm.horizontalAdvance(t) if t else 0
            w = max(180, 40 + tw + 40)
        except Exception:
            w = 180
        return QSize(max(base.width(), w), max(base.height(), h))

    def minimumSizeHint(self):
        sh = self.sizeHint()
        return QSize(max(180, sh.width()), 33)

    def eventFilter(self, obj, e: QEvent):
        if obj is self:
            if e.type() == QEvent.Type.MouseButtonPress:
                self.isPressed = True
            elif e.type() == QEvent.Type.MouseButtonRelease:
                self.isPressed = False
            elif e.type() == QEvent.Type.Enter:
                self.isHover = True
            elif e.type() == QEvent.Type.Leave:
                self.isHover = False
        return super().eventFilter(obj, e)

    def clear(self):
        self._items.clear()
        self._ensure_minimum_checked()
        self._update_placeholder_state()
        self.update()

    def setPlaceholderText(self, text: str):
        self._placeholder_text = str(text or "")
        self._update_placeholder_state()
        self.update()

    def addItem(
        self,
        text: str,
        userData: Any = None,
        checked: bool = False,
        isEnabled: bool = True,
    ):
        key = userData if userData is not None else text
        for it in self._items:
            k = it.user_data if it.user_data is not None else it.text
            if k == key:
                return

        self._items.append(
            _CheckableComboItem(
                text=str(text),
                user_data=userData,
                is_enabled=bool(isEnabled),
                is_checked=bool(checked),
            )
        )
        self._ensure_minimum_checked()
        self._update_placeholder_state()
        self.update()

    def addItems(self, texts: Iterable[str]):
        for t in texts:
            self.addItem(str(t))

    def items(self) -> List[_CheckableComboItem]:
        return list(self._items)

    def checkedData(self) -> List[Any]:
        data: List[Any] = []
        for it in self._items:
            if it.is_checked:
                v = it.user_data if it.user_data is not None else it.text
                if v not in data:
                    data.append(v)
        return data

    def checkedTexts(self) -> List[str]:
        texts: List[str] = []
        for it in self._items:
            if it.is_checked and it.text not in texts:
                texts.append(it.text)
        return texts

    def setCheckedData(self, values: Sequence[Any]):
        wanted: List[Any] = []
        for v in list(values or []):
            if v not in wanted:
                wanted.append(v)

        for it in self._items:
            key = it.user_data if it.user_data is not None else it.text
            it.is_checked = key in wanted

        self._ensure_minimum_checked()
        self._update_placeholder_state()
        self._sync_menu_rows()
        self.update()
        try:
            self.adjustSize()
        except Exception:
            pass
        self.checkedDataChanged.emit(self.checkedData())

    def setMinimumChecked(self, n: int):
        self._minimum_checked = int(max(0, n))
        self._ensure_minimum_checked()
        self._update_placeholder_state()
        self._sync_menu_rows()
        self.update()
        try:
            self.adjustSize()
        except Exception:
            pass

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._menu is not None:
            self._ignore_release_toggle = True
            try:
                self._menu.close()
            except Exception:
                pass
            self._menu = None
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() != Qt.MouseButton.LeftButton:
            return
        if self._ignore_release_toggle:
            self._ignore_release_toggle = False
            return

        pos = e.position().toPoint()
        for rect, idx in list(self._chip_close_hitboxes):
            if rect.contains(pos):
                self._set_checked_by_index(idx, False, keep_minimum=True)
                return

        self._toggle_menu()

    def paintEvent(self, e):
        QPushButton.paintEvent(self, e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        opacity = 1.0
        if self.isHover:
            opacity = 0.8
        elif self.isPressed:
            opacity = 0.7
        painter.setOpacity(opacity)

        arrow_rect = QRectF(
            self.width() - 22, self.height() / 2 - 5 + self.arrowAni.y, 10, 10
        )
        if isDarkTheme():
            FIF.ARROW_DOWN.render(painter, arrow_rect)
        else:
            FIF.ARROW_DOWN.render(painter, arrow_rect, fill="#646464")

        content_rect = QRect(10, 0, max(1, self.width() - 10 - 28), self.height())
        self._chip_close_hitboxes.clear()

        if self._placeholder_active:
            painter.setOpacity(1.0)
            painter.setPen(
                QColor(255, 255, 255, 160) if isDarkTheme() else QColor(0, 0, 0, 140)
            )
            fm = QFontMetrics(self.font())
            text = fm.elidedText(
                self._placeholder_text,
                Qt.TextElideMode.ElideRight,
                content_rect.width(),
            )
            painter.drawText(
                content_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                text,
            )
            return

        chips = self.checkedTexts()
        if not chips:
            return

        fm = QFontMetrics(self.font())
        x = content_rect.x()
        y_center = content_rect.center().y()
        chip_h = min(24, max(18, self.height() - 10))
        radius = 6
        spacing = 6

        if isDarkTheme():
            chip_bg = QColor(255, 255, 255, 18)
            chip_bd = QColor(255, 255, 255, 30)
            chip_fg = QColor(255, 255, 255, 220)
            close_fg = QColor(255, 255, 255, 200)
        else:
            chip_bg = QColor(0, 0, 0, 8)
            chip_bd = QColor(0, 0, 0, 26)
            chip_fg = QColor(0, 0, 0, 200)
            close_fg = QColor(0, 0, 0, 160)

        max_w = content_rect.right()
        remain = 0
        for i, t in enumerate(chips):
            text_w = fm.horizontalAdvance(t)
            close_w = fm.horizontalAdvance("×")
            pad_l, pad_r = 10, 8
            inner_gap = 6
            w = pad_l + text_w + inner_gap + close_w + pad_r
            if x + w > max_w:
                remain = len(chips) - i
                break

            chip_rect = QRect(x, int(y_center - chip_h / 2), w, chip_h)
            painter.setPen(QPen(chip_bd, 1))
            painter.setBrush(chip_bg)
            painter.drawRoundedRect(
                QRectF(chip_rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius
            )

            text_rect = QRect(
                chip_rect.x() + pad_l,
                chip_rect.y(),
                chip_rect.width() - pad_l - pad_r,
                chip_rect.height(),
            )
            painter.setPen(chip_fg)
            painter.drawText(
                text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, t
            )

            close_rect = QRect(
                chip_rect.right() - pad_r - close_w,
                chip_rect.y(),
                close_w + pad_r,
                chip_rect.height(),
            )
            painter.setPen(close_fg)
            painter.drawText(
                close_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                "×",
            )
            idx = self._find_index_by_text(t)
            if idx >= 0:
                self._chip_close_hitboxes.append((close_rect, idx))

            x = chip_rect.right() + spacing

        if remain > 0 and x < max_w:
            t = f"+{remain}"
            text_w = fm.horizontalAdvance(t)
            pad_l, pad_r = 10, 10
            w = pad_l + text_w + pad_r
            if x + w > max_w:
                w = max(1, max_w - x)
            chip_rect = QRect(x, int(y_center - chip_h / 2), w, chip_h)
            painter.setPen(QPen(chip_bd, 1))
            painter.setBrush(chip_bg)
            painter.drawRoundedRect(
                QRectF(chip_rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius
            )
            painter.setPen(chip_fg)
            painter.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, t)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.update()

    def _toggle_menu(self):
        if self._menu is not None:
            try:
                self._menu.close()
            except Exception:
                pass
            self._menu = None
            return

        if not self._items:
            return

        menu = RoundMenu(parent=self)
        menu.hBoxLayout.setContentsMargins(2, 6, 2, 6)
        menu.view.setViewportMargins(0, 2, 0, 2)
        menu.setItemHeight(33)

        fm = QFontMetrics(self.font())
        max_row_w = 0
        for idx, it in enumerate(self._items):
            row = _CheckableMenuRow(it.text, it.is_checked, it.is_enabled, menu)
            row.checkedChanged.connect(
                lambda checked, i=idx: self._set_checked_by_index(
                    i, checked, keep_minimum=True
                )
            )
            try:
                text_w = fm.horizontalAdvance(it.text)
            except Exception:
                text_w = 0
            row_w = 10 + 20 + 8 + text_w + 10 + 24
            max_row_w = max(max_row_w, row_w)
            menu.addWidget(row, selectable=False)

        menu.view.setMinimumWidth(int(max(self.width(), max_row_w)))
        menu.adjustSize()

        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._on_menu_closed)
        self._menu = menu

        x = (
            -menu.width() // 2
            + menu.layout().contentsMargins().left()
            + self.width() // 2
        )
        pd = self.mapToGlobal(QPoint(x, self.height()))
        hd = menu.view.heightForAnimation(pd, MenuAnimationType.DROP_DOWN)

        pu = self.mapToGlobal(QPoint(x, 0))
        hu = menu.view.heightForAnimation(pu, MenuAnimationType.PULL_UP)

        if hd >= hu:
            menu.view.adjustSize(pd, MenuAnimationType.DROP_DOWN)
            menu.exec(pd, aniType=MenuAnimationType.DROP_DOWN)
        else:
            menu.view.adjustSize(pu, MenuAnimationType.PULL_UP)
            menu.exec(pu, aniType=MenuAnimationType.PULL_UP)

    def _on_menu_closed(self):
        self._menu = None

    def _sync_menu_rows(self):
        menu = self._menu
        if menu is None:
            return
        try:
            for i in range(len(self._items)):
                item = menu.view.item(i)
                w = menu.view.itemWidget(item)
                if isinstance(w, _CheckableMenuRow):
                    w.setChecked(bool(self._items[i].is_checked))
        except Exception:
            pass

    def _set_checked_by_index(self, index: int, checked: bool, keep_minimum: bool):
        if not 0 <= index < len(self._items):
            return

        if keep_minimum and checked is False and self._minimum_checked > 0:
            cur_checked = sum(1 for it in self._items if it.is_checked)
            if cur_checked <= self._minimum_checked:
                self._sync_menu_rows()
                return

        self._items[index].is_checked = bool(checked)
        self._ensure_minimum_checked()
        self._update_placeholder_state()
        self._sync_menu_rows()
        self.update()
        try:
            self.adjustSize()
        except Exception:
            pass
        self.checkedDataChanged.emit(self.checkedData())

    def _ensure_minimum_checked(self):
        if self._minimum_checked <= 0:
            return

        enabled_indexes = [i for i, it in enumerate(self._items) if it.is_enabled]
        if not enabled_indexes:
            return

        checked_enabled = [i for i in enabled_indexes if self._items[i].is_checked]
        if len(checked_enabled) >= self._minimum_checked:
            return

        for i in enabled_indexes:
            if not self._items[i].is_checked:
                self._items[i].is_checked = True
                checked_enabled.append(i)
                if len(checked_enabled) >= self._minimum_checked:
                    return

    def _update_placeholder_state(self):
        self._placeholder_active = len(self.checkedTexts()) == 0
        if self.property("isPlaceholderText") == self._placeholder_active:
            return
        self.setProperty("isPlaceholderText", self._placeholder_active)
        self.setStyle(QApplication.style())
        try:
            self.update()
        except Exception:
            pass

    def _find_index_by_text(self, text: str) -> int:
        for i, it in enumerate(self._items):
            if it.text == text:
                return i
        return -1


CheckableComboBox = MultiSelectionComboBox
