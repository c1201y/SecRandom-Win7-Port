def _patch_simple(module, class_name):
    cls = getattr(module, class_name, None)
    if cls is None:
        return
    orig_init = cls.__init__

    def patched_init(self, *args, **kwargs):
        n = len(args)
        if n >= 2:
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
