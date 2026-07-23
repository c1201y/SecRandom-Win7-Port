from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *
from loguru import logger

from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.totp import is_configured, generate_secret, set_totp


class SetTotpWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.saved = False
        self.secret = ""
        self.uri = ""
        self._verified = False
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("basic_safety_settings", "set_totp"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("basic_safety_settings", "set_totp")
        )
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_description_async("basic_safety_settings", "set_totp")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        self.secret_label = BodyLabel("")
        self.qr_label = ImageLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(96, 96)
        self.generate_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "generate_totp_secret")
        )

        self.code_edit = LineEdit()
        self.code_edit.setPlaceholderText(
            get_content_name_async("basic_safety_settings", "totp_input_placeholder")
        )
        self.verify_button = PushButton(
            get_content_name_async("basic_safety_settings", "verify_totp_code")
        )

        layout.addWidget(self.secret_label)
        layout.addWidget(self.qr_label)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.code_edit)
        layout.addWidget(self.verify_button)

        self.main_layout.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.save_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "save_button")
        )
        self.cancel_button = PushButton(
            get_content_name_async("basic_safety_settings", "cancel_button")
        )
        btns.addWidget(self.save_button)
        btns.addWidget(self.cancel_button)
        self.main_layout.addLayout(btns)
        self.main_layout.addStretch(1)

        if is_configured():
            self.secret_label.setText(
                get_content_name_async("basic_safety_settings", "totp_generated_saved")
            )
        else:
            self.secret_label.setText("")

    def __connect_signals(self):
        self.generate_button.clicked.connect(self.__generate)
        self.verify_button.clicked.connect(self.__verify)
        self.save_button.clicked.connect(self.__save)
        self.cancel_button.clicked.connect(self.__cancel)

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

    def __generate(self):
        try:
            sec = generate_secret()
            issuer = "SecRandom"
            account = "user"
            import pyotp

            uri = pyotp.TOTP(sec).provisioning_uri(name=account, issuer_name=issuer)
            self.secret = sec
            self.uri = uri
            self.secret_label.setText(
                f"{get_content_name_async('basic_safety_settings', 'totp_secret_prefix')}: {sec}"
            )
            try:
                import qrcode

                img = qrcode.make(uri)
                from io import BytesIO

                buf = BytesIO()
                img.save(buf, format="PNG")
                qt_img = QImage.fromData(buf.getvalue(), "PNG")
                pix = QPixmap.fromImage(qt_img)
                scaled = pix.scaled(
                    self.qr_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.qr_label.setPixmap(scaled)
            except Exception:
                self.qr_label.setText(
                    get_content_name_async(
                        "basic_safety_settings", "totp_qr_unavailable"
                    )
                )
            logger.debug("已生成TOTP密钥与二维码")
            self._notify_success(
                get_content_name_async("basic_safety_settings", "totp_secret_generated")
            )
        except Exception as e:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "totp_generated_error")
                + f": {str(e)}"
            )

    def __verify(self):
        code = self.code_edit.text() or ""
        if not code:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "totp_code_invalid")
            )
            return
        try:
            import pyotp

            ok = pyotp.TOTP(self.secret).verify(code, valid_window=1)
        except Exception:
            ok = False
        logger.debug(f"TOTP输入验证结果：{ok}")
        if ok:
            self._notify_success(
                get_content_name_async("basic_safety_settings", "totp_code_valid")
            )
            self._verified = True
        else:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "totp_code_invalid")
            )

    def __save(self):
        if not self._verified:
            self._notify_error(
                get_content_name_async(
                    "basic_safety_settings", "totp_verify_before_save"
                )
            )
            return
        try:
            set_totp(self.secret)
            self.saved = True
            logger.debug("已保存TOTP配置（验证通过）")
            self._notify_success(
                get_content_name_async("basic_safety_settings", "totp_save_success"),
                duration=2000,
            )
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
        event.accept()
