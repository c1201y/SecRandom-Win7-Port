from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from datetime import datetime
from app.tools.variable import NEXT_VERSION, CODENAME, SYSTEM, ARCH
from app.Language.obtain_language import get_content_name_async


class DevHintWidget(QWidget):
    """开发中提示组件 - 显示在窗口内部左下角"""

    def __init__(self, parent=None, position_mode="bottom_left"):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.position_mode = position_mode
        self.setup_ui()
        self.setup_position()

    def setup_ui(self):
        """初始化UI"""
        # 获取应用程序字体
        app_font = QApplication.font()

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(2)

        hint_text = get_content_name_async("dev_hint", "hint_text")
        version_text = f"SecRandom {NEXT_VERSION} Dev | {CODENAME} ({SYSTEM}-{ARCH})"
        self.hint_text = hint_text
        self.version_text = version_text

        self.hint_label = QLabel(self._build_hint_text())
        hint_font = QFont(app_font)
        self.hint_label.setFont(hint_font)
        self.hint_label.setTextFormat(Qt.TextFormat.RichText)
        self.hint_label.setWordWrap(False)

        self.main_layout.addWidget(self.hint_label)

        # 设置最小宽度和固定大小
        self.setMinimumWidth(400)
        self.adjustSize()
        self.setFixedSize(self.size())

    def setup_position(self):
        if self.parent():
            parent_rect = self.parent().rect()
            if self.position_mode == "titlebar_center":
                x = max(0, int((parent_rect.width() - self.width()) / 2))
                y = max(0, int((parent_rect.height() - self.height()) / 2))
            else:
                x = 5
                y = parent_rect.height() - self.height() - 5
            self.move(x, y)

    def update_position(self):
        """更新位置 - 当父窗口大小改变时调用"""
        self.setup_position()

    def update_date(self):
        date_text = datetime.now().strftime("%Y-%m-%d")
        self.version_text = (
            f"SecRandom {NEXT_VERSION} Dev | {CODENAME} ({SYSTEM}-{ARCH}) | {date_text}"
        )
        self.hint_label.setText(self._build_hint_text())

    def _build_hint_text(self):
        return (
            f"<span style='color:#FF6B6B; font-weight:600;'>{self.hint_text}</span> "
            f"<span style='color:#888888; font-size:8pt;'>{self.version_text}</span>"
        )
