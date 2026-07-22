from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *
from loguru import logger

from app.tools.settings_access import update_settings
from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.usb import (
    get_bound_serials,
    is_serial_connected,
    unbind,
    get_bindings,
    get_serial_volume_label,
    remove_key_file_for_serial,
)


class UnbindUsbWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(
            get_content_name_async("basic_safety_settings", "unbind_usb")
        )
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(
            get_content_name_async("basic_safety_settings", "unbind_usb")
        )
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(
            get_content_description_async("basic_safety_settings", "unbind_usb")
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        list_title = SubtitleLabel(
            get_content_name_async("basic_safety_settings", "usb_bound_devices")
        )
        layout.addWidget(list_title)

        self.bound_list = ListWidget()
        layout.addWidget(self.bound_list)

        btns = QHBoxLayout()
        self.refresh_button = PushButton(
            get_content_name_async("basic_safety_settings", "usb_refresh")
        )
        self.unbind_selected_button = PrimaryPushButton(
            get_content_name_async("basic_safety_settings", "usb_unbind_selected")
        )
        self.unbind_all_button = PushButton(
            get_content_name_async("basic_safety_settings", "usb_unbind_all")
        )
        btns.addWidget(self.refresh_button)
        btns.addWidget(self.unbind_selected_button)
        btns.addWidget(self.unbind_all_button)
        layout.addLayout(btns)

        self.main_layout.addWidget(card)

        footer = QHBoxLayout()
        footer.addStretch(1)
        self.close_button = PushButton(
            get_content_name_async("basic_safety_settings", "cancel_button")
        )
        footer.addWidget(self.close_button)
        self.main_layout.addLayout(footer)
        self.main_layout.addStretch(1)

        self.__refresh()

    def __connect_signals(self):
        self.refresh_button.clicked.connect(self.__refresh)
        self.unbind_selected_button.clicked.connect(self.__unbind_selected)
        self.unbind_all_button.clicked.connect(self.__unbind_all)
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
        self.bound_list.clear()
        try:
            bindings = get_bindings()
            if bindings:
                for b in bindings:
                    s = b.get("serial", "")
                    connected = is_serial_connected(s)
                    name = b.get("name") or get_serial_volume_label(s) or ""
                    suffix = " (Connected)" if connected else " (Disconnected)"
                    item = QListWidgetItem(f"{name} {s}{suffix}")
                    try:
                        item.setData(Qt.UserRole, s)
                    except Exception:
                        pass
                    self.bound_list.addItem(item)
                logger.debug(f"已加载绑定设备数量：{len(bindings)}")
            else:
                serials = get_bound_serials()
                for s in serials:
                    connected = is_serial_connected(s)
                    name = get_serial_volume_label(s) or ""
                    suffix = " (Connected)" if connected else " (Disconnected)"
                    item = QListWidgetItem(f"{name} {s}{suffix}")
                    try:
                        item.setData(Qt.UserRole, s)
                    except Exception:
                        pass
                    self.bound_list.addItem(item)
                logger.debug(f"已加载旧绑定序列数量：{len(serials)}")
        except Exception as e:
            self._notify_error(str(e))

    def __unbind_selected(self):
        item = self.bound_list.currentItem()
        if item is None:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "usb_select_bound_hint")
            )
            return
        text = item.text()
        try:
            serial = item.data(Qt.UserRole)
        except Exception:
            serial = None
        if not serial:
            # 回退解析：取最后一个非状态片段，去掉括号内容
            try:
                import re

                m = re.search(r"\s([A-Z0-9\-\{\}\\?]+)(?:\s\(|$)", text)
                serial = m.group(1) if m else None
            except Exception:
                serial = None
        if not serial:
            self._notify_error(
                get_content_name_async("basic_safety_settings", "usb_select_bound_hint")
            )
            return
        try:
            unbind(serial)
            try:
                remove_key_file_for_serial(serial)
            except Exception:
                pass
            logger.debug("解绑选中设备成功")
            self._notify_success(
                get_content_name_async(
                    "basic_safety_settings", "usb_unbind_selected_success"
                )
            )
            try:
                # 若所有绑定已清空，自动关闭开关
                if not get_bindings() and not get_bound_serials():
                    update_settings("basic_safety_settings", "usb_switch", False)
            except Exception:
                pass
            self.__refresh()
        except Exception as e:
            self._notify_error(str(e))

    def __unbind_all(self):
        try:
            # 删除所有绑定并清理所有匹配的.key
            serials = get_bound_serials()
            unbind(None)
            try:
                for s in serials:
                    remove_key_file_for_serial(s)
            except Exception:
                pass
            logger.debug("解绑全部设备成功")
            self._notify_success(
                get_content_name_async(
                    "basic_safety_settings", "usb_unbind_all_success"
                )
            )
            try:
                update_settings("basic_safety_settings", "usb_switch", False)
            except Exception:
                pass
            self.__refresh()
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
