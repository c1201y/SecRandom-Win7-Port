from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from PySide2.QtCore import QObject, QTimer
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLineEdit,
    QScrollArea,
    QWidget,
)
from qfluentwidgets import Action, SystemTrayMenu

from app.Language.obtain_language import get_content_name_async
from app.common.search.settings_language_search import (
    build_settings_language_search_index,
    search_settings_language_index,
)


class SettingsSearchController(QObject):
    def __init__(
        self,
        window: QWidget,
        title_bar: QWidget,
        line_edit: QWidget,
        handle_page_request: Callable[[str], None],
        get_page_mapping: Callable[[], Dict[str, Any]],
        get_created_page: Callable[[str], Optional[QWidget]],
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._window = window
        self._title_bar = title_bar
        self._line_edit = line_edit
        self._handle_page_request = handle_page_request
        self._get_page_mapping = get_page_mapping
        self._get_created_page = get_created_page

        self._menu: Optional[SystemTrayMenu] = None
        self._index: Optional[List[Dict[str, Any]]] = None
        self._bind_enter_key()

    def on_search(self, text: str) -> None:
        query = str(text or "").strip()
        if not query:
            return

        self._ensure_index()
        results = search_settings_language_index(self._index or [], query, limit=12)
        if not results:
            self._show_empty_hint(query)
            return

        self._show_results_menu(results)

    def _bind_enter_key(self) -> None:
        targets = []

        if hasattr(self._line_edit, "returnPressed"):
            targets.append(self._line_edit)

        try:
            inner = self._line_edit.findChild(QLineEdit)
        except Exception:
            inner = None

        if inner is not None and hasattr(inner, "returnPressed"):
            targets.append(inner)

        for w in targets:
            try:
                w.returnPressed.connect(self._trigger_enter_search)
            except Exception:
                pass

    def _trigger_enter_search(self) -> None:
        self.on_search(self._get_current_text())

    def _get_current_text(self) -> str:
        try:
            if hasattr(self._line_edit, "text"):
                return str(self._line_edit.text() or "")
        except Exception:
            pass

        try:
            inner = self._line_edit.findChild(QLineEdit)
        except Exception:
            inner = None

        if inner is not None:
            try:
                return str(inner.text() or "")
            except Exception:
                return ""

        return ""

    def _ensure_index(self) -> None:
        if self._index is not None:
            return
        self._index = build_settings_language_search_index()

    def _show_empty_hint(self, query: str) -> None:
        no_result_text = get_content_name_async("settings", "search_no_result")
        menu = SystemTrayMenu(parent=self._window)
        action = Action(f"{no_result_text}: {query}")
        action.setEnabled(False)
        menu.addAction(action)
        self._popup_menu(menu)

    def _show_results_menu(self, results: List[Dict[str, Any]]) -> None:
        menu = SystemTrayMenu(parent=self._window)
        for entry in results:
            action = Action(entry.get("display") or "")
            action.triggered.connect(
                lambda checked=False, e=entry: self._jump_to_entry(e)
            )
            menu.addAction(action)
        self._popup_menu(menu)

    def _popup_menu(self, menu: SystemTrayMenu) -> None:
        old_menu = self._menu
        if old_menu is not None:
            try:
                old_menu.close()
            except Exception:
                pass
            try:
                old_menu.deleteLater()
            except Exception:
                pass

        try:
            pos = self._line_edit.mapToGlobal(self._line_edit.rect().bottomLeft())
        except Exception:
            return
        menu.popup(pos)
        self._menu = menu

    def _jump_to_entry(self, entry: Dict[str, Any]) -> None:
        page_route = entry.get("page_route")
        if not page_route:
            return

        self._handle_page_request(page_route)

        page_mapping = self._get_page_mapping() or {}
        interface_attr = page_mapping.get(page_route, (None, None))[0]
        if not interface_attr:
            return

        def try_jump(attempt: int = 0) -> None:
            page = self._get_created_page(interface_attr)
            if page is None:
                if attempt < 20:
                    QTimer.singleShot(50, lambda: try_jump(attempt + 1))
                return

            pivot = entry.get("pivot")
            if pivot:
                if hasattr(page, "switch_to_page"):
                    try:
                        page.switch_to_page(pivot)
                    except Exception:
                        pass
                else:
                    pivot_widget = getattr(page, "pivot", None)
                    if pivot_widget is not None and hasattr(
                        pivot_widget, "setCurrentItem"
                    ):
                        try:
                            pivot_widget.setCurrentItem(pivot)
                        except Exception:
                            pass

            QTimer.singleShot(50, lambda: self._scroll_to_entry(page, entry))

        QTimer.singleShot(0, lambda: try_jump(0))

    def _scroll_to_entry(self, page: QWidget, entry: Dict[str, Any]) -> None:
        first = entry.get("first")
        second = entry.get("second")
        if not first or not second:
            return

        try:
            target_text = get_content_name_async(first, second)
        except Exception:
            return
        if not target_text:
            return

        scroll_area = None
        container = None

        if hasattr(page, "pages") and hasattr(page, "current_page"):
            current = None
            try:
                current = (
                    page.get_current_page()
                    if hasattr(page, "get_current_page")
                    else page.current_page
                )
            except Exception:
                current = None
            if current:
                try:
                    scroll_area = (
                        page.get_page(current)
                        if hasattr(page, "get_page")
                        else page.pages.get(current)
                    )
                except Exception:
                    scroll_area = None
                try:
                    if current in getattr(page, "page_infos", {}):
                        container = page.page_infos[current].get("widget")
                except Exception:
                    container = None
        else:
            scroll_area = getattr(page, "_scroll_area_lazy", None)
            container = getattr(page, "contentWidget", None)

        if scroll_area is None and hasattr(page, "stackedWidget"):
            try:
                stacked = getattr(page, "stackedWidget", None)
                current_widget = (
                    stacked.currentWidget()
                    if hasattr(stacked, "currentWidget")
                    else None
                )
            except Exception:
                current_widget = None

            if current_widget is not None:
                try:
                    scroll_area = getattr(current_widget, "scrollArea", None)
                except Exception:
                    scroll_area = None

                if scroll_area is None:
                    try:
                        scroll_area = current_widget.findChild(QScrollArea)
                    except Exception:
                        scroll_area = None

                try:
                    container = container or getattr(
                        current_widget, "contentWidget", None
                    )
                except Exception:
                    pass
                try:
                    container = container or getattr(
                        current_widget, "scrollWidget", None
                    )
                except Exception:
                    pass

        if scroll_area is None:
            return

        try:
            scroll_root = (
                scroll_area.widget() if hasattr(scroll_area, "widget") else None
            )
        except Exception:
            scroll_root = None

        search_root = container or scroll_root
        if search_root is None:
            return

        target = self._find_first_widget_contains_text(search_root, target_text)
        if target is None:
            return

        try:
            scroll_area.ensureWidgetVisible(target)
        except Exception:
            pass
        self._highlight_found_widget(target, search_root)

    def _find_first_widget_contains_text(
        self, root: QWidget, target_text: str
    ) -> Optional[QWidget]:
        try:
            for w in root.findChildren(QWidget):
                if not hasattr(w, "text"):
                    continue
                try:
                    txt = str(w.text() or "")
                except Exception:
                    txt = ""
                if txt and target_text in txt:
                    return w
        except Exception:
            return None
        return None

    def _highlight_found_widget(self, target: QWidget, stop_at: QWidget) -> None:
        highlight_target = self._pick_highlight_target(target, stop_at)
        if highlight_target is None:
            return

        try:
            old_effect = highlight_target.graphicsEffect()
        except Exception:
            old_effect = None

        effect = QGraphicsDropShadowEffect(highlight_target)
        effect.setBlurRadius(34)
        effect.setOffset(0, 0)
        effect.setColor(QColor(255, 215, 0, 245))
        try:
            highlight_target.setGraphicsEffect(effect)
        except Exception:
            return

        def restore() -> None:
            try:
                if highlight_target.graphicsEffect() is effect:
                    highlight_target.setGraphicsEffect(old_effect)
            except Exception:
                return

        QTimer.singleShot(1200, restore)

    def _pick_highlight_target(self, w: QWidget, stop_at: QWidget) -> Optional[QWidget]:
        if w is None:
            return None
        best: QWidget = w
        cur: Optional[QWidget] = w
        for _ in range(10):
            if cur is None or cur is stop_at:
                break
            if isinstance(cur, QFrame):
                best = cur
            cur = cur.parentWidget()
        return best
