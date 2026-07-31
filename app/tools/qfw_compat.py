def _patch_simple(module, class_name):
    cls = getattr(module, class_name, None)
    if cls is None:
        return
    orig_init = cls.__init__

    def patched_init(self, *args, **kwargs):
        n = len(args)
        if n >= 3:
            # FluentWidgets-style: (icon, text, parent)
            icon, text, parent = args[0], args[1], args[2]
            # FluentWidgets @overload only accepts 1 positional (text) or (parent)
            orig_init(self, text)
            if parent is not None:
                self.setParent(parent)
            if hasattr(self, "setIcon") and icon is not None:
                from PySide2.QtGui import QIcon
                if isinstance(icon, QIcon):
                    self.setIcon(icon)
        elif n == 2:
            # FluentWidgets: (text, parent) - pass only parent, setText separately
            text = args[0]
            parent = args[1] if n > 1 else None
            orig_init(self, parent)
            if hasattr(self, "setText") and text:
                self.setText(text)
        elif n == 1:
            arg = args[0]
            if isinstance(arg, str):
                orig_init(self)
                if arg:
                    self.setText(arg)
            else:
                orig_init(self, arg)
        else:
            orig_init(self, *args, **kwargs)

    cls.__init__ = patched_init


def _patch_scrollbar(module):
    cls = getattr(module, "ScrollBar", None)
    if cls is None:
        return
    orig = cls._onOpacityAniValueChanged

    def patched(self, _value=None):
        orig(self)

    cls._onOpacityAniValueChanged = patched


def _patch_pivot(module):
    cls = getattr(module, "Pivot", None)
    if cls is None:
        return

    def patched(self, item=None):
        # sender() 在 Nuitka 打包环境下可能返回 None，优先使用信号发射的参数
        if item is None:
            item = self.sender()
        if item is not None:
            self.setCurrentItem(item.property("routeKey"))

    cls._onItemClicked = patched


SIMPLE_CLASSES = [
    "PushButton",
    "PrimaryPushButton",
    "BodyLabel",
    "CaptionLabel",
    "StrongBodyLabel",
    "SubtitleLabel",
    "TitleLabel",
    "LargeTitleLabel",
    "ComboBox",
    "LineEdit",
    "CardWidget",
]


def apply_patches():
    import qfluentwidgets as qfw

    for name in SIMPLE_CLASSES:
        _patch_simple(qfw, name)
    _patch_scrollbar(qfw)
    _patch_pivot(qfw)
