# ==================================================
# 导入库
# ==================================================

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from qfluentwidgets import *
from loguru import logger

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.page_building.security_window import (
    create_set_password_window,
    create_set_totp_window,
    create_bind_usb_window,
    create_unbind_usb_window,
)
from app.common.safety.verify_ops import require_and_run
from app.common.safety.usb import has_binding, is_bound_present
from app.common.safety.secure_store import read_secrets, write_secrets
from app.common.safety.password import is_configured as password_is_configured
from app.common.safety.totp import is_configured as totp_is_configured


# ==================================================
# 安全设置
# ==================================================
class safety_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加验证方式设置组件
        self.verification_method_widget = basic_safety_verification_method(self)
        self.vBoxLayout.addWidget(self.verification_method_widget)

        # 添加验证流程设置组件
        self.verification_process_widget = basic_safety_verification_process(self)
        self.vBoxLayout.addWidget(self.verification_process_widget)

        # 添加安全操作设置组件
        self.security_operations_widget = basic_safety_security_operations(self)
        self.vBoxLayout.addWidget(self.security_operations_widget)

        # 初始化时根据安全总开关状态更新所有组件的启用状态
        self._update_all_security_components_enabled_state()

        # 连接安全总开关状态变化信号
        get_settings_signals().settingChanged.connect(self._on_global_setting_changed)

    def _update_all_security_components_enabled_state(self):
        """更新所有安全相关组件的启用状态"""
        # 获取安全总开关状态
        safety_enabled = readme_settings_async("basic_safety_settings", "safety_switch")

        # 更新验证方式组件
        self.verification_method_widget._update_components_enabled_state_based_on_global(
            safety_enabled
        )

        # 更新验证流程组件
        self.verification_process_widget._update_enabled_state(safety_enabled)

        # 更新安全操作组件
        self.security_operations_widget._update_enabled_state(safety_enabled)

    def _on_global_setting_changed(self, first_level_key, second_level_key, value):
        """全局设置变化时的处理"""
        if (
            first_level_key == "basic_safety_settings"
            and second_level_key == "safety_switch"
        ):
            # 安全总开关状态变化时，更新所有安全相关组件的启用状态
            self._update_all_security_components_enabled_state()


class basic_safety_verification_method(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self.setTitle(
            get_content_name_async("basic_safety_settings", "verification_method")
        )
        self.setBorderRadius(8)

        # 是否开启安全功能开关
        self.safety_switch = SwitchButton()
        self.safety_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "safety_switch", "disable"
            )
        )
        self.safety_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "safety_switch", "enable"
            )
        )
        self.safety_switch.setChecked(
            readme_settings_async("basic_safety_settings", "safety_switch")
        )
        try:
            sec = read_secrets()
            bs = sec.get("basic_safety_settings") or {}
            if "safety_switch" in bs:
                self.safety_switch.setChecked(bool(bs.get("safety_switch")))
        except Exception:
            pass
        if self.safety_switch.isChecked() and not password_is_configured():
            self.safety_switch.setChecked(False)
            update_settings("basic_safety_settings", "safety_switch", False)
        self.safety_switch.checkedChanged.connect(self.__on_safety_switch_changed)

        # 设置/修改密码按钮
        self.set_password_button = PushButton(
            get_content_name_async("basic_safety_settings", "set_password")
        )
        self.set_password_button.clicked.connect(lambda: self.set_password())

        # 是否启用TOTP开关
        self.totp_switch = SwitchButton()
        self.totp_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "totp_switch", "disable"
            )
        )
        self.totp_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "totp_switch", "enable"
            )
        )
        self.totp_switch.setChecked(
            readme_settings_async("basic_safety_settings", "totp_switch")
        )
        try:
            sec = read_secrets()
            bs = sec.get("basic_safety_settings") or {}
            if "totp_switch" in bs:
                self.totp_switch.setChecked(bool(bs.get("totp_switch")))
        except Exception:
            pass
        if self.totp_switch.isChecked() and not totp_is_configured():
            self.totp_switch.setChecked(False)
            update_settings("basic_safety_settings", "totp_switch", False)
        self.totp_switch.checkedChanged.connect(self.__on_totp_switch_changed)

        # 设置TOTP按钮
        self.set_totp_button = PushButton(
            get_content_name_async("basic_safety_settings", "set_totp")
        )
        self.set_totp_button.clicked.connect(lambda: self.set_totp())

        # 是否启用U盘验证开关
        self.usb_switch = SwitchButton()
        self.usb_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "usb_switch", "disable"
            )
        )
        self.usb_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "usb_switch", "enable"
            )
        )
        self.usb_switch.setChecked(
            readme_settings_async("basic_safety_settings", "usb_switch")
        )
        try:
            sec = read_secrets()
            bs = sec.get("basic_safety_settings") or {}
            if "usb_switch" in bs:
                self.usb_switch.setChecked(bool(bs.get("usb_switch")))
        except Exception:
            pass
        if self.usb_switch.isChecked() and not has_binding():
            self.usb_switch.setChecked(False)
            update_settings("basic_safety_settings", "usb_switch", False)
        self.usb_switch.checkedChanged.connect(self.__on_usb_switch_changed)

        # 绑定U盘按钮
        self.bind_usb_button = PushButton(
            get_content_name_async("basic_safety_settings", "bind_usb")
        )
        self.bind_usb_button.clicked.connect(lambda: self.bind_usb())

        # 解绑U盘按钮
        self.unbind_usb_button = PushButton(
            get_content_name_async("basic_safety_settings", "unbind_usb")
        )
        self.unbind_usb_button.clicked.connect(lambda: self.unbind_usb())

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_shield_keyhole_20_filled"),
            get_content_name_async("basic_safety_settings", "safety_switch"),
            get_content_description_async("basic_safety_settings", "safety_switch"),
            self.safety_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_laptop_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "set_password"),
            get_content_description_async("basic_safety_settings", "set_password"),
            self.set_password_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_puzzle_piece_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "totp_switch"),
            get_content_description_async("basic_safety_settings", "totp_switch"),
            self.totp_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_laptop_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "set_totp"),
            get_content_description_async("basic_safety_settings", "set_totp"),
            self.set_totp_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_puzzle_piece_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "usb_switch"),
            get_content_description_async("basic_safety_settings", "usb_switch"),
            self.usb_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_usb_stick_20_filled"),
            get_content_name_async("basic_safety_settings", "bind_usb"),
            get_content_description_async("basic_safety_settings", "bind_usb"),
            self.bind_usb_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_usb_plug_20_filled"),
            get_content_name_async("basic_safety_settings", "unbind_usb"),
            get_content_description_async("basic_safety_settings", "unbind_usb"),
            self.unbind_usb_button,
        )

        if not password_is_configured():
            self.totp_switch.setEnabled(False)
            self.set_totp_button.setEnabled(False)
            self.usb_switch.setEnabled(False)
            self.bind_usb_button.setEnabled(False)
            self.unbind_usb_button.setEnabled(False)

        # 初始化时根据总开关状态更新组件启用状态
        self._update_components_enabled_state()

        get_settings_signals().settingChanged.connect(self.__on_setting_changed)

    def _notify_error(self, text: str, duration: int = 3000):
        try:
            InfoBar.error(
                title=get_content_name_async("basic_safety_settings", "error_title"),
                content=text,
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
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=self,
            )
        except Exception:
            pass

    def _set_switch(self, switch: SwitchButton, key: str, desired: bool):
        try:
            switch.blockSignals(True)
            switch.setChecked(desired)
            switch.blockSignals(False)
        except Exception:
            pass
        update_settings("basic_safety_settings", key, desired)

    def _persist_basic_safety(self, name: str, value: bool):
        try:
            sec = read_secrets()
            bs = sec.get("basic_safety_settings") or {}
            bs[name] = bool(value)
            sec["basic_safety_settings"] = bs
            write_secrets(sec)
        except Exception:
            pass

    def set_password(self):
        create_set_password_window()

    def set_totp(self):
        if not password_is_configured():
            self._notify_error(
                get_content_name_async(
                    "basic_safety_settings", "error_set_password_first"
                )
            )
            return
        require_and_run("set_totp", self, create_set_totp_window)

    def bind_usb(self):
        if not password_is_configured():
            self._notify_error(
                get_content_name_async(
                    "basic_safety_settings", "error_set_password_first"
                )
            )
            return
        require_and_run("bind_usb", self, create_bind_usb_window)

    def unbind_usb(self):
        if not password_is_configured():
            self._notify_error(
                get_content_name_async(
                    "basic_safety_settings", "error_set_password_first"
                )
            )
            return
        require_and_run("unbind_usb", self, create_unbind_usb_window)

    def __on_safety_switch_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if self.safety_switch.isChecked() and not password_is_configured():
                self.safety_switch.setChecked(False)
                update_settings("basic_safety_settings", "safety_switch", False)
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_set_password_first"
                    )
                )
                # 更新其他组件的启用状态
                self._update_components_enabled_state()
                return
            desired = bool(self.safety_switch.isChecked())
            prev = bool(readme_settings_async("basic_safety_settings", "safety_switch"))

            # 恢复之前的状态，等待验证通过后再执行实际变更
            self._set_switch(self.safety_switch, "safety_switch", prev)

            def apply():
                self._set_switch(self.safety_switch, "safety_switch", desired)
                try:
                    self._persist_basic_safety("safety_switch", desired)
                except Exception:
                    pass
                # 更新其他组件的启用状态
                self._update_components_enabled_state()
                logger.debug(f"安全总开关状态：{bool(desired)}")

            require_and_run("toggle_safety", self, apply)
        finally:
            self._busy = False

    def __on_totp_switch_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            desired = bool(self.totp_switch.isChecked())
            if desired and not totp_is_configured():
                self._set_switch(self.totp_switch, "totp_switch", False)
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_set_totp_first"
                    )
                )
                return

            prev = bool(readme_settings_async("basic_safety_settings", "totp_switch"))

            # 恢复之前的状态，等待验证通过后再执行实际变更
            self._set_switch(self.totp_switch, "totp_switch", prev)

            def apply():
                self._set_switch(self.totp_switch, "totp_switch", desired)
                self._persist_basic_safety("totp_switch", desired)
                if desired:
                    self._notify_success(
                        get_content_name_async("basic_safety_settings", "totp_switch")
                        + "：已开启TOTP验证",
                        duration=2000,
                    )
                else:
                    InfoBar.info(
                        title=get_content_name_async(
                            "basic_safety_settings", "totp_switch"
                        ),
                        content="已关闭TOTP验证",
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self,
                    )
                logger.debug(f"TOTP开关状态：{bool(desired)}")

            require_and_run("toggle_totp", self, apply)
        finally:
            self._busy = False

    def __on_usb_switch_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            desired = bool(self.usb_switch.isChecked())
            try:
                need_present = desired and (not has_binding() or not is_bound_present())
            except Exception:
                need_present = desired and (not has_binding())
            if need_present:
                self._set_switch(self.usb_switch, "usb_switch", False)
                self._notify_error(
                    get_content_name_async(
                        "basic_safety_settings", "error_bind_usb_first"
                    )
                )
                return

            prev = bool(readme_settings_async("basic_safety_settings", "usb_switch"))

            # 恢复之前的状态，等待验证通过后再执行实际变更
            self._set_switch(self.usb_switch, "usb_switch", prev)

            def apply():
                self._set_switch(self.usb_switch, "usb_switch", desired)
                self._persist_basic_safety("usb_switch", desired)
                if desired:
                    self._notify_success(
                        get_content_name_async("basic_safety_settings", "usb_switch")
                        + "：已开启U盘验证",
                        duration=2000,
                    )
                else:
                    InfoBar.info(
                        title=get_content_name_async(
                            "basic_safety_settings", "usb_switch"
                        ),
                        content="已关闭U盘验证",
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self,
                    )
                logger.debug(f"U盘验证开关状态：{bool(desired)}")

            require_and_run("toggle_usb", self, apply)
        finally:
            self._busy = False

    def _update_components_enabled_state(self):
        """根据安全总开关状态更新其他组件的启用状态（内部方法）"""
        safety_enabled = self.safety_switch.isChecked()
        password_configured = password_is_configured()

        # 总开关关闭时，禁用除总开关外的所有安全相关组件
        if not safety_enabled:
            self.totp_switch.setEnabled(False)
            self.set_totp_button.setEnabled(False)
            self.usb_switch.setEnabled(False)
            self.bind_usb_button.setEnabled(False)
            self.unbind_usb_button.setEnabled(False)
        else:
            # 总开关开启时，根据密码配置状态决定其他组件是否启用
            self.totp_switch.setEnabled(password_configured)
            self.set_totp_button.setEnabled(True)  # 设置密码按钮始终可用
            self.usb_switch.setEnabled(password_configured)
            self.bind_usb_button.setEnabled(password_configured)
            self.unbind_usb_button.setEnabled(password_configured)

    def _update_components_enabled_state_based_on_global(self, global_safety_enabled):
        """根据全局安全总开关状态更新组件的启用状态"""
        password_configured = password_is_configured()

        # 如果全局安全总开关关闭，禁用除总开关外的所有安全相关组件
        if not global_safety_enabled:
            self.totp_switch.setEnabled(False)
            self.set_totp_button.setEnabled(False)  # 即使是设置密码按钮也禁用
            self.usb_switch.setEnabled(False)
            self.bind_usb_button.setEnabled(False)
            self.unbind_usb_button.setEnabled(False)
        else:
            # 全局安全总开关开启时，根据密码配置状态决定其他组件是否启用
            self.totp_switch.setEnabled(password_configured)
            self.set_totp_button.setEnabled(
                True
            )  # 设置密码按钮始终可用（当全局安全开启时）
            self.usb_switch.setEnabled(password_configured)
            self.bind_usb_button.setEnabled(password_configured)
            self.unbind_usb_button.setEnabled(password_configured)

    def __on_setting_changed(self, first_level_key, second_level_key, value):
        if first_level_key != "basic_safety_settings":
            return

        if self._busy:
            return

        # 只在状态不同时才更新，避免不必要的信号触发
        if (
            second_level_key == "safety_switch"
            and self.safety_switch.isChecked() != bool(value)
        ):
            self.safety_switch.blockSignals(True)
            self.safety_switch.setChecked(bool(value))
            self.safety_switch.blockSignals(False)
            # 安全总开关状态改变时，更新其他组件的启用状态
            self._update_components_enabled_state()
        elif second_level_key == "totp_switch" and self.totp_switch.isChecked() != bool(
            value
        ):
            self.totp_switch.blockSignals(True)
            self.totp_switch.setChecked(bool(value))
            self.totp_switch.blockSignals(False)
        elif second_level_key == "usb_switch" and self.usb_switch.isChecked() != bool(
            value
        ):
            self.usb_switch.blockSignals(True)
            self.usb_switch.setChecked(bool(value))
            self.usb_switch.blockSignals(False)

        enabled = password_is_configured()
        self.totp_switch.setEnabled(enabled and self.safety_switch.isChecked())
        self.set_totp_button.setEnabled(self.safety_switch.isChecked())
        self.usb_switch.setEnabled(enabled and self.safety_switch.isChecked())
        self.bind_usb_button.setEnabled(enabled and self.safety_switch.isChecked())
        self.unbind_usb_button.setEnabled(enabled and self.safety_switch.isChecked())


class basic_safety_verification_process(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("basic_safety_settings", "verification_process")
        )
        self.setBorderRadius(8)

        # 选择验证流程下拉框
        self.verification_process_combo = ComboBox()
        self.verification_process_combo.addItems(
            get_content_combo_name_async(
                "basic_safety_settings", "verification_process"
            )
        )
        self.verification_process_combo.setCurrentIndex(
            readme_settings_async("basic_safety_settings", "verification_process")
        )
        self.verification_process_combo.currentIndexChanged.connect(
            self.__on_verification_process_changed
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_calendar_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "verification_process"),
            get_content_description_async(
                "basic_safety_settings", "verification_process"
            ),
            self.verification_process_combo,
        )

    def __on_verification_process_changed(self):
        desired = int(self.verification_process_combo.currentIndex())
        _pv = readme_settings_async("basic_safety_settings", "verification_process")
        prev = int(_pv) if isinstance(_pv, int) else 0
        self.verification_process_combo.blockSignals(True)
        self.verification_process_combo.setCurrentIndex(prev)
        self.verification_process_combo.blockSignals(False)

        def apply():
            update_settings(
                "basic_safety_settings",
                "verification_process",
                desired,
            )
            # 验证通过后刷新下拉框显示
            self.verification_process_combo.blockSignals(True)
            self.verification_process_combo.setCurrentIndex(desired)
            self.verification_process_combo.blockSignals(False)

        require_and_run("change_verification_process", self, apply)

    def _update_enabled_state(self, enabled):
        """根据安全总开关状态更新组件的启用状态"""
        self.verification_process_combo.setEnabled(enabled)


class basic_safety_security_operations(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self.setTitle(
            get_content_name_async("basic_safety_settings", "security_operations")
        )
        self.setBorderRadius(8)

        # 显隐浮窗需验证密码开关
        self.show_hide_floating_window_switch = SwitchButton()
        self.show_hide_floating_window_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch", "disable"
            )
        )
        self.show_hide_floating_window_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch", "enable"
            )
        )
        self.show_hide_floating_window_switch.setChecked(
            readme_settings_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            )
        )
        self.show_hide_floating_window_switch.checkedChanged.connect(
            self.__on_ops_show_hide_changed
        )

        # 重启软件需验证密码开关
        self.restart_switch = SwitchButton()
        self.restart_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "restart_switch", "disable"
            )
        )
        self.restart_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "restart_switch", "enable"
            )
        )
        self.restart_switch.setChecked(
            readme_settings_async("basic_safety_settings", "restart_switch")
        )
        self.restart_switch.checkedChanged.connect(self.__on_ops_restart_changed)

        # 退出软件需验证密码开关
        self.exit_switch = SwitchButton()
        self.exit_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "exit_switch", "disable"
            )
        )
        self.exit_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "exit_switch", "enable"
            )
        )
        self.exit_switch.setChecked(
            readme_settings_async("basic_safety_settings", "exit_switch")
        )
        self.exit_switch.checkedChanged.connect(self.__on_ops_exit_changed)

        self.open_settings_switch = SwitchButton()
        self.open_settings_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "open_settings_switch", "disable"
            )
        )
        self.open_settings_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "open_settings_switch", "enable"
            )
        )
        self.open_settings_switch.setChecked(
            bool(readme_settings_async("basic_safety_settings", "open_settings_switch"))
        )
        self.open_settings_switch.checkedChanged.connect(
            self.__on_ops_open_settings_changed
        )

        # 预览设置开关
        self.preview_settings_switch = SwitchButton()
        self.preview_settings_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "preview_settings_switch", "disable"
            )
        )
        self.preview_settings_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "preview_settings_switch", "enable"
            )
        )
        self.preview_settings_switch.setChecked(
            bool(
                readme_settings_async(
                    "basic_safety_settings", "preview_settings_switch"
                )
            )
        )
        self.preview_settings_switch.checkedChanged.connect(
            self.__on_ops_preview_settings_changed
        )

        get_settings_signals().settingChanged.connect(self.__on_ops_setting_changed)

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_eye_20_filled"),
            get_content_name_async("basic_safety_settings", "preview_settings_switch"),
            get_content_description_async(
                "basic_safety_settings", "preview_settings_switch"
            ),
            self.preview_settings_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_window_ad_20_filled"),
            get_content_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            ),
            get_content_description_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            ),
            self.show_hide_floating_window_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async("basic_safety_settings", "restart_switch"),
            get_content_description_async("basic_safety_settings", "restart_switch"),
            self.restart_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_exit_20_filled"),
            get_content_name_async("basic_safety_settings", "exit_switch"),
            get_content_description_async("basic_safety_settings", "exit_switch"),
            self.exit_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_settings_20_filled"),
            get_content_name_async("basic_safety_settings", "open_settings_switch"),
            get_content_description_async(
                "basic_safety_settings", "open_settings_switch"
            ),
            self.open_settings_switch,
        )

        self._ensure_ops_disabled_if_no_password()

    def __on_ops_setting_changed(self, first_level_key, second_level_key, value):
        if first_level_key != "basic_safety_settings":
            return
        self._ensure_ops_disabled_if_no_password()

        # 只在状态不同时才更新，避免不必要的信号触发
        if (
            second_level_key == "show_hide_floating_window_switch"
            and self.show_hide_floating_window_switch.isChecked() != bool(value)
        ):
            self.show_hide_floating_window_switch.blockSignals(True)
            self.show_hide_floating_window_switch.setChecked(bool(value))
            self.show_hide_floating_window_switch.blockSignals(False)
        elif (
            second_level_key == "restart_switch"
            and self.restart_switch.isChecked() != bool(value)
        ):
            self.restart_switch.blockSignals(True)
            self.restart_switch.setChecked(bool(value))
            self.restart_switch.blockSignals(False)
        elif second_level_key == "exit_switch" and self.exit_switch.isChecked() != bool(
            value
        ):
            self.exit_switch.blockSignals(True)
            self.exit_switch.setChecked(bool(value))
            self.exit_switch.blockSignals(False)
        elif (
            second_level_key == "open_settings_switch"
            and self.open_settings_switch.isChecked() != bool(value)
        ):
            self.open_settings_switch.blockSignals(True)
            self.open_settings_switch.setChecked(bool(value))
            self.open_settings_switch.blockSignals(False)
        elif (
            second_level_key == "preview_settings_switch"
            and self.preview_settings_switch.isChecked() != bool(value)
        ):
            self.preview_settings_switch.blockSignals(True)
            self.preview_settings_switch.setChecked(bool(value))
            self.preview_settings_switch.blockSignals(False)

    def _ensure_ops_disabled_if_no_password(self):
        enabled = password_is_configured()
        self.show_hide_floating_window_switch.setEnabled(enabled)
        self.restart_switch.setEnabled(enabled)
        self.exit_switch.setEnabled(enabled)
        self.open_settings_switch.setEnabled(enabled)
        self.preview_settings_switch.setEnabled(enabled)
        if not enabled:
            for key, sw in [
                (
                    "show_hide_floating_window_switch",
                    self.show_hide_floating_window_switch,
                ),
                ("restart_switch", self.restart_switch),
                ("exit_switch", self.exit_switch),
                ("open_settings_switch", self.open_settings_switch),
                ("preview_settings_switch", self.preview_settings_switch),
            ]:
                try:
                    # 检查开关当前状态，如果已经是False，就不需要再次更新
                    if sw.isChecked():
                        sw.blockSignals(True)
                        sw.setChecked(False)
                        sw.blockSignals(False)
                        update_settings("basic_safety_settings", key, False)
                except Exception:
                    pass

    def __on_ops_show_hide_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if not password_is_configured():
                try:
                    self.show_hide_floating_window_switch.blockSignals(True)
                    self.show_hide_floating_window_switch.setChecked(False)
                    self.show_hide_floating_window_switch.blockSignals(False)
                    update_settings(
                        "basic_safety_settings",
                        "show_hide_floating_window_switch",
                        False,
                    )
                except Exception:
                    pass
                return
            desired = bool(self.show_hide_floating_window_switch.isChecked())
            prev = bool(
                readme_settings_async(
                    "basic_safety_settings", "show_hide_floating_window_switch"
                )
            )
            self.show_hide_floating_window_switch.blockSignals(True)
            self.show_hide_floating_window_switch.setChecked(prev)
            self.show_hide_floating_window_switch.blockSignals(False)

            def apply():
                update_settings(
                    "basic_safety_settings",
                    "show_hide_floating_window_switch",
                    desired,
                )

            require_and_run("toggle_show_hide_floating_window_switch", self, apply)
        finally:
            self._busy = False

    def __on_ops_restart_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if not password_is_configured():
                try:
                    self.restart_switch.blockSignals(True)
                    self.restart_switch.setChecked(False)
                    self.restart_switch.blockSignals(False)
                    update_settings("basic_safety_settings", "restart_switch", False)
                except Exception:
                    pass
                return
            desired = bool(self.restart_switch.isChecked())
            prev = bool(
                readme_settings_async("basic_safety_settings", "restart_switch")
            )
            self.restart_switch.blockSignals(True)
            self.restart_switch.setChecked(prev)
            self.restart_switch.blockSignals(False)

            def apply():
                update_settings(
                    "basic_safety_settings",
                    "restart_switch",
                    desired,
                )

            require_and_run("toggle_restart_switch", self, apply)
        finally:
            self._busy = False

    def __on_ops_exit_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if not password_is_configured():
                try:
                    self.exit_switch.blockSignals(True)
                    self.exit_switch.setChecked(False)
                    self.exit_switch.blockSignals(False)
                    update_settings("basic_safety_settings", "exit_switch", False)
                except Exception:
                    pass
                return
            desired = bool(self.exit_switch.isChecked())
            prev = bool(readme_settings_async("basic_safety_settings", "exit_switch"))
            self.exit_switch.blockSignals(True)
            self.exit_switch.setChecked(prev)
            self.exit_switch.blockSignals(False)

            def apply():
                update_settings(
                    "basic_safety_settings",
                    "exit_switch",
                    desired,
                )

            require_and_run("toggle_exit_switch", self, apply)
        finally:
            self._busy = False

    def __on_ops_open_settings_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if not password_is_configured():
                try:
                    self.open_settings_switch.blockSignals(True)
                    self.open_settings_switch.setChecked(False)
                    self.open_settings_switch.blockSignals(False)
                    update_settings(
                        "basic_safety_settings", "open_settings_switch", False
                    )
                except Exception:
                    pass
                return
            desired = bool(self.open_settings_switch.isChecked())
            prev = bool(
                readme_settings_async("basic_safety_settings", "open_settings_switch")
            )
            self.open_settings_switch.blockSignals(True)
            self.open_settings_switch.setChecked(prev)
            self.open_settings_switch.blockSignals(False)

            def apply():
                update_settings(
                    "basic_safety_settings",
                    "open_settings_switch",
                    desired,
                )

            require_and_run("toggle_open_settings_switch", self, apply)
        finally:
            self._busy = False

    def __on_ops_preview_settings_changed(self):
        if self._busy:
            return
        self._busy = True
        try:
            if not password_is_configured():
                try:
                    self.preview_settings_switch.blockSignals(True)
                    self.preview_settings_switch.setChecked(False)
                    self.preview_settings_switch.blockSignals(False)
                    update_settings(
                        "basic_safety_settings", "preview_settings_switch", False
                    )
                except Exception:
                    pass
                return

            # 保存当前状态以备回滚
            prev_state = bool(
                readme_settings_async(
                    "basic_safety_settings", "preview_settings_switch"
                )
            )
            desired = bool(self.preview_settings_switch.isChecked())

            # 立即更新UI，如果验证失败将回滚
            try:
                self.preview_settings_switch.blockSignals(True)
                self.preview_settings_switch.setChecked(desired)
                self.preview_settings_switch.blockSignals(False)
            except Exception:
                pass

            def apply():
                update_settings(
                    "basic_safety_settings",
                    "preview_settings_switch",
                    desired,
                )

            require_and_run("toggle_preview_settings_switch", self, apply)
        finally:
            self._busy = False

    def _update_enabled_state(self, global_safety_enabled):
        """根据全局安全总开关状态更新组件的启用状态"""
        # 如果全局安全总开关关闭，禁用除总开关外的所有安全相关组件
        if not global_safety_enabled:
            self.show_hide_floating_window_switch.setEnabled(False)
            self.restart_switch.setEnabled(False)
            self.exit_switch.setEnabled(False)
            self.open_settings_switch.setEnabled(False)
            self.preview_settings_switch.setEnabled(False)
        else:
            # 全局安全总开关开启时，根据密码配置状态决定其他组件是否启用
            password_configured = password_is_configured()
            self.show_hide_floating_window_switch.setEnabled(password_configured)
            self.restart_switch.setEnabled(password_configured)
            self.exit_switch.setEnabled(password_configured)
            self.open_settings_switch.setEnabled(password_configured)
            self.preview_settings_switch.setEnabled(password_configured)
