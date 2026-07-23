from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *
from loguru import logger

from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.usb import (
    list_removable_drives,
    list_usb_drive_letters_wmi,
    get_volume_serial,
    get_volume_label,
    bind_with_options,
    remove_key_file,
)


class BindUsbWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.saved = False
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("basic_safety_settings", "bind_usb"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("basic_safety_settings", "bind_usb")
        )
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_description_async("basic_safety_settings", "bind_usb")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        self.drive_combo = ComboBox()
        self.refresh_button = PushButton(
            get_content_name_async("basic_safety_settings", "usb_refresh")
        )
        self.require_key_checkbox = CheckBox(
            get_content_name_async("basic_safety_settings", "usb_require_key_file")
        )
        self.bind_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "usb_bind")
        )

        layout.addWidget(self.drive_combo)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.require_key_checkbox)
        layout.addWidget(self.bind_button)

        self.main_layout.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.close_button = PushButton(
            get_content_name_async("basic_safety_settings", "cancel_button")
        )
        btns.addWidget(self.close_button)
        self.main_layout.addLayout(btns)
        self.main_layout.addStretch(1)

        QTimer.singleShot(0, self.__refresh)

    def __connect_signals(self):
        self.refresh_button.clicked.connect(self.__refresh)
        self.bind_button.clicked.connect(self.__bind)
        self.close_button.clicked.connect(self.__cancel)

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

    def __refresh(self):
        self.drive_combo.clear()
        try:
            import platform

            # 优先使用WMI获取USB设备的逻辑盘符（可覆盖固定盘类型的外置硬盘）
            letters = list_usb_drive_letters_wmi()
            if not letters:
                # 回退到驱动类型为可移动盘的枚举
                letters = list_removable_drives()
            logger.debug(f"刷新可绑定设备，数量：{len(letters)}, 设备列表：{letters}")
            for device in letters:
                if platform.system() == "Windows":
                    # Windows 平台：device 是盘符（如 "E"）
                    name = get_volume_label(device)
                    text = f"{name} ({device}:)" if name else f"({device}:)"
                    self.drive_combo.addItem(text, device)
                    logger.debug(f"添加设备到下拉框：显示文本={text}, 数据={device}")
                else:
                    # Linux 平台：device 是挂载点路径（如 "/media/user/USB Drive"）
                    name = get_volume_label(device)
                    # 在Linux上，name 可能就是挂载点的目录名，所以直接使用 device 作为显示文本
                    text = device
                    self.drive_combo.addItem(text, device)
                    logger.debug(f"添加设备到下拉框：显示文本={text}, 数据={device}")
            if not letters:
                self.drive_combo.setCurrentIndex(-1)
                # 使占位文本可见
                try:
                    self.drive_combo.setEditable(True)
                    self.drive_combo.lineEdit().setReadOnly(True)
                    self.drive_combo.lineEdit().setPlaceholderText(
                        get_content_name_async(
                            "basic_safety_settings", "usb_no_removable"
                        )
                    )
                    self.bind_button.setEnabled(False)
                except Exception:
                    self.bind_button.setEnabled(False)
            else:
                try:
                    self.drive_combo.setEditable(False)
                    self.drive_combo.setCurrentIndex(0)
                except Exception:
                    pass
                self.bind_button.setEnabled(True)
        except Exception as e:
            self._notify_error(str(e))

    def __bind(self):
        idx = self.drive_combo.currentIndex()
        logger.debug(f"当前选中索引：{idx}")
        if idx < 0:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "usb_no_removable")
            )
            return
        text = self.drive_combo.currentText()
        device = self.drive_combo.currentData()
        logger.debug(
            f"当前选中项：显示文本={text}, 数据={device}, 数据类型={type(device)}"
        )

        # 如果 currentData() 返回 None，尝试通过索引获取数据
        if device is None:
            logger.warning("currentData() 返回 None，尝试通过索引获取数据")
            # 从文本中提取盘符
            import re

            match = re.search(r"\(([A-Z]):\)", text)
            if match:
                device = match.group(1)
                logger.debug(f"从文本中提取到盘符：{device}")

        try:
            # 允许来自USB设备的逻辑盘（包括部分显示为固定盘的外置硬盘）
            serial = get_volume_serial(device)
            logger.debug(f"尝试绑定设备：{device}, 序列号：{serial}")
            if not serial or serial == "00000000":
                logger.warning(f"设备序列号无效：{device}, serial={serial}")
                raise RuntimeError(
                    get_content_name_async("basic_safety_settings", "usb_no_removable")
                )
            require_key = bool(self.require_key_checkbox.isChecked())
            key_value = None
            if require_key:
                try:
                    from app.common.safety.usb import write_key_file

                    try:
                        remove_key_file(device)
                    except Exception:
                        pass
                    key_value = os.urandom(16).hex()
                    ok = write_key_file(device, key_value)
                    if not ok:
                        raise RuntimeError(
                            get_content_name_async(
                                "basic_safety_settings", "usb_no_removable"
                            )
                        )
                except Exception as e:
                    raise RuntimeError(str(e)) from e
            display_name = get_volume_label(device)
            bind_with_options(
                serial,
                require_key_file=require_key,
                key_value=key_value,
                name=display_name,
            )
            logger.debug(f"绑定设备成功：{device}")
            self._notify_success(
                f"{get_content_name_async('basic_safety_settings', 'usb_bind_success')}: {text}"
            )
        except Exception as e:
            logger.error(f"绑定设备失败：{device}, 错误：{e}")
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
