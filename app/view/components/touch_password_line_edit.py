from PySide2.QtCore import QEvent, QPointF, Qt, QTimer
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QLineEdit, QWidget
from qfluentwidgets import PasswordLineEdit


class TouchPasswordLineEdit(PasswordLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._reveal_active = False
        self._reveal_grabber = None
        try:
            self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        except Exception:
            pass
        self._install_filters()
        try:
            QTimer.singleShot(0, self._install_filters)
        except Exception:
            pass

    def _install_filters(self):
        try:
            self.installEventFilter(self)
        except Exception:
            pass
        try:
            for w in self.findChildren(QLineEdit):
                try:
                    w.installEventFilter(self)
                except Exception:
                    pass
        except Exception:
            pass

    def _set_revealed(self, revealed: bool):
        mode = QLineEdit.EchoMode.Normal if revealed else QLineEdit.EchoMode.Password
        try:
            self.setEchoMode(mode)
        except Exception:
            pass
        try:
            for w in self.findChildren(QLineEdit):
                try:
                    w.setEchoMode(mode)
                except Exception:
                    pass
        except Exception:
            pass

    def _is_eye_hit(self, obj: QWidget, pos: QPointF) -> bool:
        try:
            edge = int(max(36, obj.height()))
            return int(pos.x()) >= int(obj.width() - edge)
        except Exception:
            return False

    def _start_reveal(self, grabber: QWidget):
        self._reveal_active = True
        self._reveal_grabber = grabber
        try:
            grabber.grabMouse()
        except Exception:
            pass
        self._set_revealed(True)

    def _stop_reveal(self):
        self._reveal_active = False
        try:
            g = getattr(self, "_reveal_grabber", None)
            if g is not None:
                g.releaseMouse()
        except Exception:
            pass
        self._reveal_grabber = None
        self._set_revealed(False)

    def event(self, event):
        try:
            if event.type() == QEvent.Type.TouchBegin:
                try:
                    pts = event.points()
                    if pts:
                        pos = pts[0].position()
                        if self._is_eye_hit(self, pos):
                            self._start_reveal(self)
                            event.accept()
                            return True
                except Exception:
                    pass
            if event.type() in (QEvent.Type.TouchEnd, QEvent.Type.TouchCancel):
                if self._reveal_active:
                    self._stop_reveal()
                    event.accept()
                    return True
        except Exception:
            pass
        return super().event(event)

    def eventFilter(self, obj, event):
        try:
            if isinstance(obj, (TouchPasswordLineEdit, QLineEdit)):
                if event.type() == QEvent.Type.MouseButtonPress:
                    try:
                        if (
                            event.button() == Qt.MouseButton.LeftButton
                            and self._is_eye_hit(obj, event.position())
                        ):
                            self._start_reveal(obj)
                            return True
                    except Exception:
                        pass
                if event.type() == QEvent.Type.MouseButtonRelease:
                    if self._reveal_active:
                        self._stop_reveal()
                        return True
                if event.type() in (QEvent.Type.Leave, QEvent.Type.FocusOut):
                    if self._reveal_active:
                        self._stop_reveal()
                        return False
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: QMouseEvent):
        try:
            if event.button() == Qt.MouseButton.LeftButton and self._is_eye_hit(
                self, event.position()
            ):
                self._start_reveal(self)
                return
        except Exception:
            pass
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._reveal_active:
            self._stop_reveal()
            return
        return super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._reveal_active:
            self._stop_reveal()
        return super().leaveEvent(event)

    def focusOutEvent(self, event):
        if self._reveal_active:
            self._stop_reveal()
        return super().focusOutEvent(event)
