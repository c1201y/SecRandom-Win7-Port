from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *


class shortcut_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        self.shortcut_enable_widget = shortcut_enable(self)
        self.vBoxLayout.addWidget(self.shortcut_enable_widget)

        self.shortcut_table_widget = shortcut_table(self)
        self.vBoxLayout.addWidget(self.shortcut_table_widget)


class shortcut_enable(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("shortcut_settings", "title"))
        self.setBorderRadius(8)

        self.enable_shortcut_switch = SwitchButton()
        self.enable_shortcut_switch.setOffText(
            get_content_switchbutton_name_async(
                "shortcut_settings", "enable_shortcut", "disable"
            )
        )
        self.enable_shortcut_switch.setOnText(
            get_content_switchbutton_name_async(
                "shortcut_settings", "enable_shortcut", "enable"
            )
        )
        enable_shortcut = readme_settings_async("shortcut_settings", "enable_shortcut")
        self.enable_shortcut_switch.setChecked(enable_shortcut)
        self.enable_shortcut_switch.checkedChanged.connect(
            lambda: update_settings(
                "shortcut_settings",
                "enable_shortcut",
                self.enable_shortcut_switch.isChecked(),
            )
        )

        self.addGroup(
            get_theme_icon("ic_fluent_keyboard_20_filled"),
            get_content_name_async("shortcut_settings", "enable_shortcut"),
            get_content_description_async("shortcut_settings", "enable_shortcut"),
            self.enable_shortcut_switch,
        )


class shortcut_table(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("shortcut_settings", "title"))
        self.setBorderRadius(8)

        self.create_table()
        self.init_table_data()

    def create_table(self):
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()

        headers = [
            get_content_name_async("shortcut_settings", "function"),
            get_content_name_async("shortcut_settings", "shortcut"),
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )
            self.table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

        self.layout().addWidget(self.table)

    def init_table_data(self):
        self.shortcut_configs = [
            {
                "name": get_content_name_async(
                    "shortcut_settings", "open_roll_call_page"
                ),
                "config_key": "open_roll_call_page",
            },
            {
                "name": get_content_name_async("shortcut_settings", "use_quick_draw"),
                "config_key": "use_quick_draw",
            },
            {
                "name": get_content_name_async(
                    "shortcut_settings", "open_lottery_page"
                ),
                "config_key": "open_lottery_page",
            },
            {
                "name": get_content_name_async(
                    "shortcut_settings", "increase_roll_call_count"
                ),
                "config_key": "increase_roll_call_count",
            },
            {
                "name": get_content_name_async(
                    "shortcut_settings", "decrease_roll_call_count"
                ),
                "config_key": "decrease_roll_call_count",
            },
            {
                "name": get_content_name_async(
                    "shortcut_settings", "increase_lottery_count"
                ),
                "config_key": "increase_lottery_count",
            },
            {
                "name": get_content_name_async(
                    "shortcut_settings", "decrease_lottery_count"
                ),
                "config_key": "decrease_lottery_count",
            },
            {
                "name": get_content_name_async("shortcut_settings", "start_roll_call"),
                "config_key": "start_roll_call",
            },
            {
                "name": get_content_name_async("shortcut_settings", "start_lottery"),
                "config_key": "start_lottery",
            },
        ]

        self.table.setRowCount(len(self.shortcut_configs))

        for row, config in enumerate(self.shortcut_configs):
            function_item = QTableWidgetItem(config["name"])
            function_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, function_item)

            shortcut_key = LineEdit()
            shortcut_key.setPlaceholderText(
                get_content_name_async("shortcut_settings", "press_shortcut")
            )
            shortcut_key.setFixedHeight(30)
            shortcut_key.setReadOnly(True)
            current_shortcut = readme_settings_async(
                "shortcut_settings", config["config_key"]
            )
            if current_shortcut:
                shortcut_key.setText(current_shortcut)

            shortcut_key.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            shortcut_key.installEventFilter(self)
            shortcut_key.setProperty("config_key", config["config_key"])
            self.table.setCellWidget(row, 1, shortcut_key)

    def update_shortcut(self, config_key, sequence):
        if sequence.isEmpty():
            update_settings("shortcut_settings", config_key, "")
        else:
            update_settings("shortcut_settings", config_key, sequence.toString())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if isinstance(obj, LineEdit) and obj.property("config_key"):
                config_key = obj.property("config_key")

                if event.key() == Qt.Key.Key_Escape:
                    obj.clearFocus()
                    return True

                if event.key() == Qt.Key.Key_Backspace:
                    update_settings("shortcut_settings", config_key, "")
                    obj.setText("")
                    return True

                modifiers = []
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    modifiers.append("Ctrl")
                if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                    modifiers.append("Alt")
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    modifiers.append("Shift")

                key = event.key()
                if key >= Qt.Key.Key_A and key <= Qt.Key.Key_Z:
                    key_char = chr(key).lower()
                elif key >= Qt.Key.Key_0 and key <= Qt.Key.Key_9:
                    key_char = chr(key)
                elif key == Qt.Key.Key_Space:
                    key_char = "Space"
                elif key == Qt.Key.Key_Tab:
                    key_char = "Tab"
                elif key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
                    key_char = "Return"
                elif key == Qt.Key.Key_Backspace:
                    key_char = "Backspace"
                elif key == Qt.Key.Key_Delete:
                    key_char = "Delete"
                elif key == Qt.Key.Key_Home:
                    key_char = "Home"
                elif key == Qt.Key.Key_End:
                    key_char = "End"
                elif key == Qt.Key.Key_Left:
                    key_char = "Left"
                elif key == Qt.Key.Key_Up:
                    key_char = "Up"
                elif key == Qt.Key.Key_Right:
                    key_char = "Right"
                elif key == Qt.Key.Key_Down:
                    key_char = "Down"
                elif key == Qt.Key.Key_PageUp:
                    key_char = "PageUp"
                elif key == Qt.Key.Key_PageDown:
                    key_char = "PageDown"
                elif key == Qt.Key.Key_F1:
                    key_char = "F1"
                elif key == Qt.Key.Key_F2:
                    key_char = "F2"
                elif key == Qt.Key.Key_F3:
                    key_char = "F3"
                elif key == Qt.Key.Key_F4:
                    key_char = "F4"
                elif key == Qt.Key.Key_F5:
                    key_char = "F5"
                elif key == Qt.Key.Key_F6:
                    key_char = "F6"
                elif key == Qt.Key.Key_F7:
                    key_char = "F7"
                elif key == Qt.Key.Key_F8:
                    key_char = "F8"
                elif key == Qt.Key.Key_F9:
                    key_char = "F9"
                elif key == Qt.Key.Key_F10:
                    key_char = "F10"
                elif key == Qt.Key.Key_F11:
                    key_char = "F11"
                elif key == Qt.Key.Key_F12:
                    key_char = "F12"
                else:
                    return False

                if modifiers:
                    shortcut_str = "+".join(modifiers) + "+" + key_char
                else:
                    shortcut_str = key_char

                update_settings("shortcut_settings", config_key, shortcut_str)
                obj.setText(shortcut_str)
                obj.clearFocus()
                return True

        return super().eventFilter(obj, event)
