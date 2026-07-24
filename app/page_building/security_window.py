from app.page_building.page_template import PageTemplate
from app.page_building.window_template import SimpleWindowTemplate
from app.view.another_window.security.set_password import SetPasswordWindow
from app.view.another_window.security.set_totp import SetTotpWindow
from app.view.another_window.usb.bind_usb import BindUsbWindow
from app.view.another_window.usb.unbind_usb import UnbindUsbWindow
from app.view.another_window.security.verify_password import VerifyPasswordWindow
from app.Language.obtain_language import *

_security_window_instances = {}


class set_password_window_template(PageTemplate):
    def __init__(self, parent=None):
        super().__init__(content_widget_class=SetPasswordWindow, parent=parent)


def create_set_password_window():
    title = get_content_name_async("basic_safety_settings", "set_password")
    if "set_password" in _security_window_instances:
        w = _security_window_instances["set_password"]
        try:
            w.raise_()
            w.activateWindow()
            w.switch_to_page("set_password")
            return w
        except Exception:
            _security_window_instances.pop("set_password", None)
    window = SimpleWindowTemplate(title, width=600, height=530)
    window.add_page_from_template("set_password", set_password_window_template)
    window.switch_to_page("set_password")
    _security_window_instances["set_password"] = window
    window.windowClosed.connect(
        lambda: _security_window_instances.pop("set_password", None)
    )
    window.show()
    return window


class set_totp_window_template(PageTemplate):
    def __init__(self, parent=None):
        super().__init__(content_widget_class=SetTotpWindow, parent=parent)


def create_set_totp_window():
    title = get_content_name_async("basic_safety_settings", "set_totp")
    if "set_totp" in _security_window_instances:
        w = _security_window_instances["set_totp"]
        try:
            w.raise_()
            w.activateWindow()
            w.switch_to_page("set_totp")
            return w
        except Exception:
            _security_window_instances.pop("set_totp", None)
    window = SimpleWindowTemplate(title, width=600, height=500)
    window.add_page_from_template("set_totp", set_totp_window_template)
    window.switch_to_page("set_totp")
    _security_window_instances["set_totp"] = window
    window.windowClosed.connect(
        lambda: _security_window_instances.pop("set_totp", None)
    )
    window.show()
    return window


class bind_usb_window_template(PageTemplate):
    def __init__(self, parent=None):
        super().__init__(content_widget_class=BindUsbWindow, parent=parent)


def create_bind_usb_window():
    title = get_content_name_async("basic_safety_settings", "bind_usb")
    if "bind_usb" in _security_window_instances:
        w = _security_window_instances["bind_usb"]
        try:
            w.raise_()
            w.activateWindow()
            w.switch_to_page("bind_usb")
            return w
        except Exception:
            _security_window_instances.pop("bind_usb", None)
    window = SimpleWindowTemplate(title, width=600, height=380)
    window.add_page_from_template("bind_usb", bind_usb_window_template)
    window.switch_to_page("bind_usb")
    _security_window_instances["bind_usb"] = window
    window.windowClosed.connect(
        lambda: _security_window_instances.pop("bind_usb", None)
    )
    window.show()
    return window


class unbind_usb_window_template(PageTemplate):
    def __init__(self, parent=None):
        super().__init__(content_widget_class=UnbindUsbWindow, parent=parent)


def create_unbind_usb_window():
    title = get_content_name_async("basic_safety_settings", "unbind_usb")
    if "unbind_usb" in _security_window_instances:
        w = _security_window_instances["unbind_usb"]
        try:
            w.raise_()
            w.activateWindow()
            w.switch_to_page("unbind_usb")
            return w
        except Exception:
            _security_window_instances.pop("unbind_usb", None)
    window = SimpleWindowTemplate(title, width=600, height=560)
    window.add_page_from_template("unbind_usb", unbind_usb_window_template)
    window.switch_to_page("unbind_usb")
    _security_window_instances["unbind_usb"] = window
    window.windowClosed.connect(
        lambda: _security_window_instances.pop("unbind_usb", None)
    )
    window.show()
    return window


class verify_password_window_template(PageTemplate):
    def __init__(self, parent=None, operation_type=None):
        def factory(parent):
            return VerifyPasswordWindow(parent=parent, operation_type=operation_type)

        factory.__name__ = "VerifyPasswordWindow"
        super().__init__(
            content_widget_class=factory,
            parent=parent,
        )


def create_verify_password_window(
    on_verified=None, on_preview=None, operation_type=None
):
    title = get_content_name_async("basic_safety_settings", "safety_switch")
    if "verify_password" in _security_window_instances:
        w = _security_window_instances["verify_password"]
        try:
            w.raise_()
            w.activateWindow()
            w.switch_to_page("verify_password")
            return w
        except Exception:
            _security_window_instances.pop("verify_password", None)
    window = SimpleWindowTemplate(title, width=480, height=240)
    page = window.add_page_from_template(
        "verify_password",
        verify_password_window_template,
        operation_type=operation_type,
    )
    window.switch_to_page("verify_password")
    content = getattr(page, "contentWidget", None)
    if on_verified:
        try:
            if content is not None and hasattr(content, "verified"):
                content.verified.connect(on_verified)
            elif hasattr(page, "verified"):
                page.verified.connect(on_verified)
        except Exception:
            pass
    if on_preview:
        try:
            if content is not None and hasattr(content, "previewRequested"):
                content.previewRequested.connect(on_preview)
            elif hasattr(page, "previewRequested"):
                page.previewRequested.connect(on_preview)
        except Exception:
            pass
    _security_window_instances["verify_password"] = window
    window.windowClosed.connect(
        lambda: _security_window_instances.pop("verify_password", None)
    )
    window.show()
    return window
