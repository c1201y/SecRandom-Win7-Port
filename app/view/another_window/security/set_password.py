from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.password import (
    is_configured,
    set_password,
    verify_password,
    clear_password,
)
from app.tools.settings_access import update_settings
from app.view.components.touch_password_line_edit import TouchPasswordLineEdit


class SetPasswordWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.saved = False
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(
            get_content_name_async("basic_safety_settings", "set_password")
        )
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("basic_safety_settings", "set_password")
        )
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_description_async("basic_safety_settings", "set_password")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)

        rules_title = SubtitleLabel(
            get_content_name_async("basic_safety_settings", "password_rules")
        )
        rules_desc = BodyLabel(
            get_content_description_async("basic_safety_settings", "password_rules")
        )
        rules_desc.setWordWrap(True)
        input_layout.addWidget(rules_title)
        input_layout.addWidget(rules_desc)

        self.current_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "current_password")
        )
        self.current_edit = TouchPasswordLineEdit()
        self.new_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "new_password")
        )
        self.new_edit = TouchPasswordLineEdit()
        self.confirm_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "confirm_password")
        )
        self.confirm_edit = TouchPasswordLineEdit()

        self.strength_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "password_strength_title")
        )

        input_layout.addWidget(self.current_label)
        input_layout.addWidget(self.current_edit)
        input_layout.addWidget(self.new_label)
        input_layout.addWidget(self.new_edit)
        input_layout.addWidget(self.confirm_label)
        input_layout.addWidget(self.confirm_edit)
        input_layout.addWidget(self.strength_label)

        self.main_layout.addWidget(input_card)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        self.save_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "save_button")
        )
        self.cancel_button = PushButton(
            get_content_name_async("basic_safety_settings", "cancel_button")
        )
        self.remove_button = PushButton(
            get_content_name_async("basic_safety_settings", "remove_password")
        )
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.remove_button)
        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch(1)

        configured = False
        try:
            configured = is_configured()
        except Exception:
            configured = False
        self.current_label.setVisible(configured)
        self.current_edit.setVisible(configured)
        self.remove_button.setVisible(configured)

    def __connect_signals(self):
        self.save_button.clicked.connect(self.__save_password)
        self.cancel_button.clicked.connect(self.__cancel)
        self.new_edit.textChanged.connect(self.__update_strength)
        self.remove_button.clicked.connect(self.__remove_password)

    def _notify_error(self, text: str, duration: int = 3000):
        try:
            InfoBar.error(
                title=get_content_name_async("basic_safety_settings", "title"),
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=self,
            )
        except Exception:
            pass

    def _notify_success(self, text: str, duration: int = 3000):
        try:
            InfoBar.success(
                title=get_content_name_async("basic_safety_settings", "title"),
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=self,
            )
        except Exception:
            pass

    def __update_strength(self):
        t = self.new_edit.text() or ""
        score = 0
        if len(t) >= 8:
            score += 1
        if any(c.isdigit() for c in t):
            score += 1
        if any(c.isalpha() for c in t):
            score += 1
        if any(c in "!@#$%^&*()-_=+[]{};:'\",.<>/?|`~" for c in t):
            score += 1
        if score <= 1:
            self.strength_label.setText(
                get_content_name_async("basic_safety_settings", "strength_weak")
            )
            self.strength_label.setStyleSheet("color: #d9534f;")
        elif score <= 3:
            self.strength_label.setText(
                get_content_name_async("basic_safety_settings", "strength_medium")
            )
            self.strength_label.setStyleSheet("color: #f0ad4e;")
        else:
            self.strength_label.setText(
                get_content_name_async("basic_safety_settings", "strength_strong")
            )
            self.strength_label.setStyleSheet("color: #5cb85c;")

    def __save_password(self):
        try:
            configured = is_configured()
            if configured:
                cur = self.current_edit.text() or ""
                if not cur or not verify_password(cur):
                    self._notify_error(
                        get_content_name_async(
                            "basic_safety_settings", "error_current_password"
                        )
                    )
                    return
            newp = self.new_edit.text() or ""
            conf = self.confirm_edit.text() or ""
            if not newp or not conf or newp != conf:
                self._notify_error(
                    get_content_name_async("basic_safety_settings", "error_mismatch")
                )
                return
            c1 = len(newp) >= 8
            c2 = any(c.isdigit() for c in newp)
            c3 = any(c.isalpha() for c in newp)
            c4 = any(c in "!@#$%^&*()-_=+[]{};:'\",.<>/?|`~" for c in newp)
            if sum([c1, c2, c3, c4]) < 3:
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_strength_insufficient"
                    )
                )
                return
            set_password(newp)
            self.saved = True
            self._notify_success(
                get_content_name_async("basic_safety_settings", "success_updated")
            )
            self.__cancel()
        except Exception as e:
            self._notify_error(str(e))

    def __remove_password(self):
        try:
            if not is_configured():
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_current_password"
                    )
                )
                return
            cur = self.current_edit.text() or ""
            if not cur or not verify_password(cur):
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_current_password"
                    )
                )
                return
            dialog = MessageBox(
                get_content_name_async(
                    "basic_safety_settings", "remove_password_confirm_title"
                ),
                get_content_name_async(
                    "basic_safety_settings", "remove_password_confirm_content"
                ),
                self,
            )
            dialog.yesButton.setText(
                get_content_name_async("basic_safety_settings", "dialog_yes_text")
            )
            dialog.cancelButton.setText(
                get_content_name_async("basic_safety_settings", "dialog_cancel_text")
            )
            if dialog.exec():
                clear_password()
                update_settings("basic_safety_settings", "safety_switch", False)
                update_settings("basic_safety_settings", "totp_switch", False)
                update_settings("basic_safety_settings", "usb_switch", False)
                update_settings(
                    "basic_safety_settings", "show_hide_floating_window_switch", False
                )
                update_settings("basic_safety_settings", "restart_switch", False)
                update_settings("basic_safety_settings", "exit_switch", False)
                self._notify_success(
                    get_content_name_async(
                        "basic_safety_settings", "remove_password_success"
                    )
                )
                self.current_label.setVisible(False)
                self.current_edit.setVisible(False)
                self.new_edit.clear()
                self.confirm_edit.clear()
                self.remove_button.setVisible(False)
                self.__cancel()
        except Exception as e:
            self._notify_error(str(e))

    def __cancel(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()

    def closeEvent(self, event):
        if not self.saved:
            event.accept()
        else:
            event.accept()
