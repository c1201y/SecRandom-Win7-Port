# ==================================================
# 导入库
# ==================================================

from PySide2.QtWidgets import QApplication, QSystemTrayIcon
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtCore import QTimer, QEvent, QPoint, Signal
from qfluentwidgets import Action, SystemTrayMenu
from loguru import logger

from app.tools.variable import (
    MENU_AUTO_CLOSE_TIMEOUT,
    TRAY_TOOLTIP_TEXT,
    TRAY_ICON_FILENAME,
    TRAY_MENU_POSITION_ADJUSTMENT,
)
from app.common.safety.verify_ops import require_and_run
from app.tools.path_utils import get_data_path
from app.Language.obtain_language import readme_settings_async, get_content_name_async
from app.common.IPC_URL.url_command_handler import URLCommandHandler


# ==================================================
# 托盘图标管理器类
# ==================================================
class Tray(QSystemTrayIcon):
    """系统托盘图标管理器

    负责管理托盘图标和菜单，提供右键菜单功能。
    继承自QSystemTrayIcon以简化实现。
    """

    showSettingsRequested = Signal(str)  # 请求显示设置页面
    showSettingsRequestedAbout = Signal()
    showFloatWindowRequested = Signal()
    showTrayActionRequested = Signal(str)  # 请求执行托盘操作

    def __init__(self, parent=None):
        """初始化系统托盘图标

        Args:
            parent: 父窗口对象，通常为主窗口
        """
        super().__init__(parent)
        self._initialize_instance_variables(parent)
        self._setup_tray_icon()
        self._setup_url_command_handler()
        self._setup_menu_timer()
        self._connect_signals()

    def _initialize_instance_variables(self, parent):
        """初始化实例变量

        Args:
            parent: 父窗口对象
        """
        self.main_window = parent

    def _setup_tray_icon(self):
        """设置托盘图标和工具提示"""
        self.setIcon(QIcon(str(get_data_path("assets/icon", TRAY_ICON_FILENAME))))
        self.setToolTip(TRAY_TOOLTIP_TEXT)
        self.activated.connect(self._on_tray_activated)

    def _setup_url_command_handler(self):
        """设置URL命令处理器"""
        self.url_command_handler = URLCommandHandler(self)
        self.url_command_handler.showTrayActionRequested.connect(
            self._handle_tray_action_requested
        )

    def _setup_menu_timer(self):
        """设置菜单自动关闭定时器"""
        self.menu_timer = QTimer(self)
        self.menu_timer.setSingleShot(True)
        self.menu_timer.timeout.connect(self._on_menu_timeout)

    def _connect_signals(self):
        """连接信号"""
        self.showTrayActionRequested.connect(self._handle_tray_action_requested)

    def _on_tray_activated(self, reason):
        """处理托盘图标点击事件

        当用户点击托盘图标时，显示菜单。

        Args:
            reason: 激活原因
        """
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.Context,
        ):
            self._create_fresh_menu()
            adjusted_pos = self._calculate_menu_position()
            self.tray_menu.popup(adjusted_pos)
            self.menu_timer.start(MENU_AUTO_CLOSE_TIMEOUT)

    def _calculate_menu_position(self):
        """计算菜单显示位置

        Returns:
            QPoint: 调整后的菜单位置
        """
        pos = QCursor.pos()
        screen = QApplication.primaryScreen().availableGeometry()
        menu_size = self.tray_menu.sizeHint()

        adjusted_x = self._calculate_menu_x_position(pos, screen, menu_size)
        adjusted_y = self._calculate_menu_y_position(pos, screen, menu_size)

        return QPoint(adjusted_x, adjusted_y - TRAY_MENU_POSITION_ADJUSTMENT)

    def _calculate_menu_x_position(self, pos, screen, menu_size):
        """计算菜单X轴位置

        Args:
            pos: 鼠标位置
            screen: 屏幕几何信息
            menu_size: 菜单大小

        Returns:
            int: 调整后的X坐标
        """
        if pos.x() + menu_size.width() > screen.right():
            adjusted_x = pos.x() - menu_size.width()
        else:
            adjusted_x = pos.x()
        return max(screen.left(), min(adjusted_x, screen.right() - menu_size.width()))

    def _calculate_menu_y_position(self, pos, screen, menu_size):
        """计算菜单Y轴位置

        Args:
            pos: 鼠标位置
            screen: 屏幕几何信息
            menu_size: 菜单大小

        Returns:
            int: 调整后的Y坐标
        """
        if pos.y() + menu_size.height() > screen.bottom():
            adjusted_y = pos.y() - menu_size.height()
        else:
            adjusted_y = pos.y()
        return max(screen.top(), min(adjusted_y, screen.bottom() - menu_size.height()))

    def _create_fresh_menu(self):
        """创建全新的托盘菜单"""
        self._delete_existing_menu()
        self.tray_menu = SystemTrayMenu(parent=self.main_window)
        self._add_about_action()
        self._add_separator()
        menu_items = self._collect_menu_items()
        self._add_menu_items(menu_items)
        self.tray_menu.installEventFilter(self)

    def _delete_existing_menu(self):
        """删除已存在的菜单"""
        if hasattr(self, "tray_menu"):
            self.tray_menu.deleteLater()

    def _add_about_action(self):
        """添加关于SecRandom菜单项"""
        self.about_action = Action(
            "SecRandom", triggered=lambda: self.showSettingsRequestedAbout.emit()
        )
        self.tray_menu.addAction(self.about_action)

    def _add_separator(self):
        """添加分隔线"""
        self.tray_menu.addSeparator()

    def _collect_menu_items(self):
        """收集需要显示的菜单项

        Returns:
            list: 菜单项列表
        """
        menu_items = []

        show_hide_main_window = readme_settings_async(
            "tray_management", "show_hide_main_window"
        )
        if show_hide_main_window is not False:
            menu_items.append(self._create_toggle_main_window_action())

        open_settings = readme_settings_async("tray_management", "open_settings")
        if open_settings is not False:
            menu_items.append(self._create_open_settings_action())

        show_hide_float_window = readme_settings_async(
            "tray_management", "show_hide_float_window"
        )
        if show_hide_float_window is not False:
            menu_items.append(self._create_toggle_float_window_action())

        if show_hide_main_window or open_settings or show_hide_float_window:
            menu_items.append("separator")

        restart = readme_settings_async("tray_management", "restart")
        if restart is not False:
            menu_items.append(self._create_restart_action())

        exit_setting = readme_settings_async("tray_management", "exit")
        if exit_setting is not False:
            menu_items.append(self._create_exit_action())

        return menu_items

    def _create_toggle_main_window_action(self):
        """创建切换主窗口显示状态的菜单项

        Returns:
            Action: 切换主窗口的Action
        """
        return Action(
            get_content_name_async("tray_management", "show_hide_main_window"),
            triggered=self.main_window.toggle_window,
        )

    def _create_open_settings_action(self):
        """创建打开设置页面的菜单项

        Returns:
            Action: 打开设置的Action
        """
        return Action(
            get_content_name_async("tray_management", "open_settings"),
            triggered=lambda: self.showSettingsRequested.emit("basicSettingsInterface"),
        )

    def _create_toggle_float_window_action(self):
        """创建切换浮窗显示状态的菜单项

        Returns:
            Action: 切换浮窗的Action
        """
        return Action(
            get_content_name_async("tray_management", "show_hide_float_window"),
            triggered=lambda: require_and_run(
                "show_hide_floating_window",
                self.main_window,
                self.main_window._toggle_float_window,
            ),
        )

    def _create_restart_action(self):
        """创建重启应用的菜单项

        Returns:
            Action: 重启应用的Action
        """
        return Action(
            get_content_name_async("tray_management", "restart"),
            triggered=lambda: require_and_run(
                "restart", self.main_window, self.main_window.restart_app
            ),
        )

    def _create_exit_action(self):
        """创建退出应用的菜单项

        Returns:
            Action: 退出应用的Action
        """
        return Action(
            get_content_name_async("tray_management", "exit"),
            triggered=lambda: require_and_run(
                "exit", self.main_window, self.main_window.close_window_secrandom
            ),
        )

    def _add_menu_items(self, menu_items):
        """添加菜单项到托盘菜单

        Args:
            menu_items: 菜单项列表
        """
        for item in menu_items:
            if item == "separator":
                self.tray_menu.addSeparator()
            else:
                self.tray_menu.addAction(item)

    def _on_menu_timeout(self):
        """菜单超时自动关闭

        当用户在指定时间内没有操作菜单时，自动关闭菜单。
        """
        if self.tray_menu.isVisible():
            self.tray_menu.close()

    def eventFilter(self, obj, event):
        """事件过滤器

        监听菜单相关事件，当用户点击菜单外部时自动关闭菜单。

        Args:
            obj: 事件对象
            event: 事件类型

        Returns:
            bool: 是否拦截事件
        """
        if obj == self.tray_menu:
            self._handle_menu_events(event)

        if self._should_close_menu_on_outside_click(event):
            self.tray_menu.close()
            self.menu_timer.stop()
            return True

        return super().eventFilter(obj, event)

    def _handle_menu_events(self, event):
        """处理菜单事件

        Args:
            event: 事件对象
        """
        if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.Hide):
            self.menu_timer.stop()

    def _should_close_menu_on_outside_click(self, event):
        """判断是否应该在外部点击时关闭菜单

        Args:
            event: 事件对象

        Returns:
            bool: 是否应该关闭菜单
        """
        return (
            event.type() == QEvent.Type.MouseButtonPress
            and self.tray_menu.isVisible()
            and not self._is_click_inside_menu(event)
        )

    def _is_click_inside_menu(self, event):
        """判断点击是否在菜单内部

        Args:
            event: 事件对象

        Returns:
            bool: 点击是否在菜单内部
        """
        click_pos = event.globalPos()
        menu_rect = self.tray_menu.geometry()
        return menu_rect.contains(click_pos)

    def show_tray_icon(self):
        """显示托盘图标"""
        if not self.isVisible():
            self.show()

    def _handle_tray_action_requested(self, action: str):
        """处理托盘操作请求

        Args:
            action: 托盘操作类型
                - 'toggle_main_window': 切换主窗口显示状态
                - 'settings': 打开设置页面
                - 'float': 切换浮窗显示状态
                - 'restart': 重启应用程序
                - 'exit': 退出应用程序
        """
        logger.debug(f"托盘收到操作请求: {action}")

        action_handlers = {
            "toggle_main_window": self._handle_toggle_main_window,
            "settings": self._handle_open_settings,
            "float": self._handle_toggle_float_window,
            "restart": self._handle_restart_app,
            "exit": self._handle_exit_app,
        }

        handler = action_handlers.get(action)
        if handler:
            handler()
        else:
            logger.warning(f"未知的托盘操作: {action}")

    def _handle_toggle_main_window(self):
        """处理切换主窗口显示状态"""
        self.main_window.toggle_window()

    def _handle_open_settings(self):
        """处理打开设置页面"""
        self.showSettingsRequested.emit("basicSettingsInterface")

    def _handle_toggle_float_window(self):
        """处理切换浮窗显示状态"""
        self.showFloatWindowRequested.emit()

    def _handle_restart_app(self):
        """处理重启应用程序"""
        require_and_run("restart", self.main_window, self.main_window.restart_app)

    def _handle_exit_app(self):
        """处理退出应用程序"""
        require_and_run(
            "exit", self.main_window, self.main_window.close_window_secrandom
        )
