from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *
from loguru import logger


from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.password import (
    verify_password,
    is_configured as password_is_configured,
)
from app.common.safety.totp import (
    is_configured as totp_is_configured,
    verify as verify_totp,
)
from app.common.safety.usb import is_bound_connected, is_bound_present
from app.tools.settings_access import readme_settings_async
from app.view.components.touch_password_line_edit import TouchPasswordLineEdit


class UsbStatusThread(QThread):
    statusReady = Signal(bool, bool)

    def run(self):
        try:
            p = bool(is_bound_present())
            c = bool(is_bound_connected())
            self.statusReady.emit(p, c)
        except Exception:
            self.statusReady.emit(False, False)


class VerifyWorker(QThread):
    resultReady = Signal(bool, bool)

    def __init__(self, plain: str, code: str, do_pwd: bool, do_totp: bool):
        super().__init__()
        self._plain = plain
        self._code = code
        self._do_pwd = do_pwd
        self._do_totp = do_totp

    def run(self):
        try:
            ok_pwd = False
            ok_totp = False
            if self._do_pwd and self._plain:
                ok_pwd = bool(verify_password(self._plain))
            if self._do_totp and self._code:
                ok_totp = bool(verify_totp(self._code))
            self.resultReady.emit(ok_pwd, ok_totp)
        except Exception:
            self.resultReady.emit(False, False)


class VerifyPasswordWindow(QWidget):
    verified = Signal()
    previewRequested = Signal()

    def __init__(self, parent=None, operation_type=None):
        super().__init__(parent)
        self.operation_type = operation_type
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(
            get_content_name_async("basic_safety_settings", "safety_switch")
        )
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("basic_safety_settings", "safety_switch")
        )
        self.main_layout.addWidget(self.title_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        self.password_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "current_password")
        )
        self.password_edit = TouchPasswordLineEdit()
        try:
            self.password_edit.setPlaceholderText(
                get_content_name_async(
                    "basic_safety_settings", "password_input_placeholder"
                )
            )
        except Exception:
            pass
        self.totp_label = BodyLabel(
            get_content_name_async("basic_safety_settings", "verify_totp_code")
        )
        self.totp_edit = LineEdit()
        self.totp_edit.setPlaceholderText(
            get_content_name_async("basic_safety_settings", "totp_input_placeholder")
        )
        self.usb_status_label = BodyLabel("")
        self.usb_refresh_button = TransparentToolButton()
        try:
            self.usb_refresh_button.setIcon(FluentIcon.SYNC.icon())
        except Exception:
            pass
        usb_row = QHBoxLayout()
        usb_row.addWidget(self.usb_status_label)
        usb_row.addWidget(self.usb_refresh_button)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.totp_label)
        layout.addWidget(self.totp_edit)
        layout.addLayout(usb_row)

        self.main_layout.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.progress_ring = ProgressRing()
        self.progress_ring.setRange(0, 0)
        self.progress_ring.setValue(0)
        self.progress_ring.setTextVisible(True)
        self.progress_ring.setFixedSize(24, 24)
        self.progress_ring.setStrokeWidth(3)
        self.progress_ring.setFormat("0/0")
        self.ok_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "dialog_yes_text")
        )
        self.preview_button = PushButton(
            get_content_name_async("basic_safety_settings", "preview_settings")
        )
        self.cancel_button = PushButton(
            get_content_name_async("basic_safety_settings", "dialog_cancel_text")
        )

        # 只在打开设置时显示预览按钮，并且预览设置开关已启用
        is_open_settings = self.operation_type == "open_settings"
        preview_enabled = bool(
            readme_settings_async("basic_safety_settings", "preview_settings_switch")
        )
        self.preview_button.setVisible(is_open_settings and preview_enabled)

        btns.addWidget(self.progress_ring)
        btns.addWidget(self.ok_button)
        btns.addWidget(self.preview_button)
        btns.addWidget(self.cancel_button)
        self.main_layout.addLayout(btns)
        self.main_layout.addStretch(1)

        self._configure_methods()

    def __connect_signals(self):
        self.ok_button.clicked.connect(self.__on_ok)
        self.preview_button.clicked.connect(self.__on_preview)
        self.cancel_button.clicked.connect(self.__cancel)
        try:
            self.usb_refresh_button.clicked.connect(self.__refresh_usb)
        except Exception:
            pass
        try:
            self.password_edit.returnPressed.connect(self.__on_return_from_password)
        except Exception:
            pass
        try:
            self.totp_edit.returnPressed.connect(self.__on_return_from_totp)
        except Exception:
            pass
        try:
            self.password_edit.textChanged.connect(self._update_progress)
        except Exception:
            pass
        try:
            self.totp_edit.textChanged.connect(self._update_progress)
        except Exception:
            pass
        try:
            self.password_edit.textChanged.connect(self._on_text_changed)
        except Exception:
            pass
        try:
            self.totp_edit.textChanged.connect(self._on_text_changed)
        except Exception:
            pass
        try:
            if not hasattr(self, "_verify_timer"):
                self._verify_timer = QTimer(self)
                self._verify_timer.setInterval(1500)
                self._verify_timer.setSingleShot(True)
                self._verify_timer.timeout.connect(self.__run_verify_async)
        except Exception:
            pass

    def _configure_methods(self):
        mode = int(
            readme_settings_async("basic_safety_settings", "verification_process") or 0
        )
        totp_enabled = (
            bool(readme_settings_async("basic_safety_settings", "totp_switch"))
            and totp_is_configured()
        )
        usb_enabled = bool(readme_settings_async("basic_safety_settings", "usb_switch"))
        pwd_enabled = password_is_configured()

        self._required = []
        if mode == 0:
            available = []
            if pwd_enabled:
                available.append("password")
            if totp_enabled:
                available.append("totp")
            if usb_enabled:
                available.append("usb")
            if not available:
                available = ["password"]
            self._required = available
            self._any_one = True
        elif mode == 1:
            self._required = ["password"]
            self._any_one = False
        elif mode == 2:
            self._required = ["totp"] if totp_enabled else ["password"]
            self._any_one = False
        elif mode == 3:
            self._required = ["usb"] if usb_enabled else ["password"]
            self._any_one = False
        elif mode == 4:
            r = ["password", "totp" if totp_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        elif mode == 5:
            r = ["password", "usb" if usb_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        elif mode == 6:
            r = [
                "totp" if totp_enabled else "password",
                "usb" if usb_enabled else "password",
            ]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        else:
            r = [
                "password",
                "totp" if totp_enabled else "password",
                "usb" if usb_enabled else "password",
            ]
            self._required = list(dict.fromkeys(r))
            self._any_one = False

        # 只在需要密码验证时显示密码控件
        password_visible = "password" in self._required
        self.password_label.setVisible(password_visible)
        self.password_edit.setVisible(password_visible)
        # 只在需要TOTP验证时显示TOTP控件
        totp_visible = "totp" in self._required
        self.totp_label.setVisible(totp_visible)
        self.totp_edit.setVisible(totp_visible)
        # 只在需要USB验证时显示USB控件
        usb_visible = "usb" in self._required
        self.usb_status_label.setVisible(usb_visible)
        self.usb_refresh_button.setVisible(usb_visible)
        present = bool(is_bound_present())
        self._last_usb_present = present
        self.usb_status_label.setText(
            get_content_name_async("basic_safety_settings", "usb_status_connected")
            if present
            else get_content_name_async(
                "basic_safety_settings", "usb_status_disconnected"
            )
        )

        # 初始化或更新当前验证状态
        self._states = {"password": False, "totp": False, "usb": False}
        logger.debug(f"验证窗口：需求={self._required}, 任意一种={self._any_one}")
        if "usb" in self._required:
            self._states["usb"] = bool(present)
        if "password" in self._required:
            plain = self.password_edit.text() or ""
            self._states["password"] = bool(len(plain) > 0)
        if "totp" in self._required:
            code = self.totp_edit.text() or ""
            self._states["totp"] = bool(len(code) >= 6)

        if self.progress_ring:
            total = int(len(self._required))
            done = int(sum(1 for k in self._required if self._states.get(k)))
            self.progress_ring.setRange(0, total)
            self.progress_ring.setValue(done)
            self.progress_ring.setFormat(f"{done}/{total}")
            logger.debug(f"验证进度：{done}/{total}")
            if self._any_one or len(self._required) <= 1:
                self.progress_ring.hide()
            else:
                self.progress_ring.show()

        # 只在打开设置时显示预览按钮，并且预览设置开关已启用
        is_open_settings = self.operation_type == "open_settings"
        preview_enabled = bool(
            readme_settings_async("basic_safety_settings", "preview_settings_switch")
        )
        self.preview_button.setVisible(is_open_settings and preview_enabled)

        try:
            if not hasattr(self, "usb_poll_timer"):
                self.usb_poll_timer = QTimer(self)
                self.usb_poll_timer.setInterval(15000)
                self.usb_poll_timer.timeout.connect(self.__refresh_usb)
            self.usb_poll_timer.start()
        except Exception:
            pass

    def __on_ok(self):
        if getattr(self, "_verify_running", False):
            try:
                InfoBar.warning(
                    title=get_content_name_async(
                        "basic_safety_settings", "error_title"
                    ),
                    content=get_content_name_async(
                        "basic_safety_settings", "verify_in_progress"
                    ),
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self,
                )
            except Exception:
                pass
            return
        self._verify_running = True
        try:
            self.ok_button.setEnabled(False)
        except Exception:
            pass
        plain = self.password_edit.text() or ""
        code = self.totp_edit.text() or ""
        do_pwd = "password" in self._required
        do_totp = "totp" in self._required
        try:
            if hasattr(self, "_verify_thread") and isinstance(
                self._verify_thread, QThread
            ):
                try:
                    if self._verify_thread.isRunning():
                        self._verify_thread.quit()
                        self._verify_thread.wait(500)
                except Exception:
                    pass
        except Exception:
            pass
        self._verify_thread = VerifyWorker(plain, code, do_pwd, do_totp)

        def _done(ok_pwd: bool, ok_totp: bool):
            try:
                results = {}
                if "password" in self._required:
                    results["password"] = bool(ok_pwd)
                if "totp" in self._required:
                    results["totp"] = bool(ok_totp)
                if "usb" in self._required:
                    results["usb"] = bool(is_bound_present())
                # 更新状态与进度
                if "password" in self._required:
                    self._states["password"] = bool(results.get("password", False))
                if "totp" in self._required:
                    self._states["totp"] = bool(results.get("totp", False))
                if "usb" in self._required:
                    self._states["usb"] = bool(results.get("usb", False))
                if self.progress_ring:
                    total = int(len(self._required))
                    done = int(sum(1 for k in self._required if self._states.get(k)))
                    self.progress_ring.setRange(0, total)
                    self.progress_ring.setValue(done)
                    self.progress_ring.setFormat(f"{done}/{total}")
                if self._any_one:
                    passed = any(results.get(k, False) for k in self._required)
                else:
                    passed = all(results.get(k, False) for k in self._required)
                logger.debug(f"验证结果：任意一种={self._any_one}, 通过={passed}")
                if not passed:
                    InfoBar.error(
                        title=get_content_name_async(
                            "basic_safety_settings", "error_title"
                        ),
                        content=get_content_name_async(
                            "basic_safety_settings", "verify_failed_generic"
                        ),
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self,
                    )
                    return
                self.verified.emit()
                self.__cancel()
            finally:
                self._verify_running = False
                try:
                    self.ok_button.setEnabled(True)
                except Exception:
                    pass

        self._verify_thread.resultReady.connect(_done)
        self._verify_thread.finished.connect(
            lambda: setattr(self, "_verify_running", False)
        )
        self._verify_thread.start()

    def __refresh_usb(self):
        try:
            if getattr(self, "_usb_task_running", False):
                return
            self._usb_task_running = True
            if not hasattr(self, "_usb_thread"):
                self._usb_thread = UsbStatusThread()
                self._usb_thread.statusReady.connect(self.__on_usb_status_ready)
            self._usb_thread.start()
        except Exception:
            self._usb_task_running = False

    def __on_usb_status_ready(self, present: bool, connected: bool):
        try:
            changed = True
            try:
                changed = present != getattr(self, "_last_usb_present", None)
            except Exception:
                pass
            if changed:
                self._last_usb_present = present
                self.usb_status_label.setText(
                    get_content_name_async(
                        "basic_safety_settings", "usb_status_connected"
                    )
                    if present
                    else get_content_name_async(
                        "basic_safety_settings", "usb_status_disconnected"
                    )
                )
                logger.debug(f"USB状态已刷新：已连接={present}")
                if "usb" in getattr(self, "_required", []):
                    self._states["usb"] = bool(present)
                    if self.progress_ring:
                        total = int(len(self._required))
                        done = int(
                            sum(1 for k in self._required if self._states.get(k))
                        )
                        self.progress_ring.setRange(0, total)
                        self.progress_ring.setValue(done)
                        self.progress_ring.setFormat(f"{done}/{total}")
        except Exception:
            pass
        finally:
            self._usb_task_running = False

    def __on_return_from_password(self):
        try:
            if "totp" in self._required and self.totp_edit.isVisible():
                self.totp_edit.setFocus()
                return
            if "usb" in self._required:
                self.__on_ok()
                return
            self.__on_ok()
        except Exception:
            self.__on_ok()

    def __on_return_from_totp(self):
        try:
            if "usb" in self._required:
                self.__on_ok()
                return
            self.__on_ok()
        except Exception:
            self.__on_ok()

    def _update_progress(self):
        try:
            if not hasattr(self, "_states"):
                return
            try:
                if "password" in self._required:
                    plain = self.password_edit.text() or ""
                    self._states["password"] = bool(len(plain) > 0)
                if "totp" in self._required:
                    code = self.totp_edit.text() or ""
                    self._states["totp"] = bool(len(code) >= 6)
            except Exception:
                pass
            if self.progress_ring:
                total = int(len(self._required))
                done = int(sum(1 for k in self._required if self._states.get(k)))
                self.progress_ring.setRange(0, total)
                self.progress_ring.setValue(done)
                self.progress_ring.setFormat(f"{done}/{total}")
                if self._any_one or len(self._required) <= 1:
                    self.progress_ring.hide()
                else:
                    self.progress_ring.show()
        except Exception:
            pass

    def _on_text_changed(self):
        try:
            self._update_progress()
            if not hasattr(self, "_verify_timer"):
                return
            self._verify_timer.stop()
            plain = self.password_edit.text() or ""
            code = self.totp_edit.text() or ""
            need_pwd = ("password" in self._required) and bool(plain)
            need_totp = ("totp" in self._required) and bool(len(code) >= 6)
            need_usb = ("usb" in self._required) and bool(
                self._states.get("usb", False)
            )
            should_run = False
            if self._any_one:
                should_run = bool(need_pwd or need_totp or need_usb)
            else:
                ready = True
                for k in self._required:
                    if k == "password" and not need_pwd:
                        ready = False
                        break
                    if k == "totp" and not need_totp:
                        ready = False
                        break
                    if k == "usb" and not need_usb:
                        ready = False
                        break
                should_run = ready
            if should_run:
                self._verify_timer.start()
        except Exception:
            pass

    def __run_verify_async(self):
        try:
            if getattr(self, "_verify_running", False):
                return
            self._verify_running = True
            plain = self.password_edit.text() or ""
            code = self.totp_edit.text() or ""
            do_pwd = "password" in self._required
            do_totp = "totp" in self._required
            self._verify_thread = VerifyWorker(plain, code, do_pwd, do_totp)
            self._verify_thread.resultReady.connect(self.__on_verify_ready)
            self._verify_thread.start()
        except Exception:
            self._verify_running = False

    def __on_preview(self):
        """预览设置"""
        self.previewRequested.emit()
        self.__cancel()

    def __on_verify_ready(self, ok_pwd: bool, ok_totp: bool):
        try:
            if "password" in self._required:
                self._states["password"] = bool(ok_pwd)
            if "totp" in self._required:
                self._states["totp"] = bool(ok_totp)
            if "usb" in self._required:
                self._states["usb"] = bool(is_bound_present())
            if self.progress_ring:
                total = int(len(self._required))
                done = int(sum(1 for k in self._required if self._states.get(k)))
                self.progress_ring.setRange(0, total)
                self.progress_ring.setValue(done)
                self.progress_ring.setFormat(f"{done}/{total}")
        except Exception:
            pass
        finally:
            self._verify_running = False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.__on_ok()
            return
        super().keyPressEvent(event)

    def __cancel(self):
        parent = self.parent()
        try:
            if hasattr(self, "usb_poll_timer"):
                self.usb_poll_timer.stop()
            if hasattr(self, "_usb_thread"):
                try:
                    self._usb_thread.terminate()
                    self._usb_thread.wait(500)
                except Exception:
                    pass
            if hasattr(self, "_verify_thread"):
                try:
                    self._verify_thread.terminate()
                    self._verify_thread.wait(500)
                except Exception:
                    pass
        except Exception:
            pass
        while parent:
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()

    def closeEvent(self, event):
        """窗口关闭时清理线程"""
        self.__cancel()
        super().closeEvent(event)
