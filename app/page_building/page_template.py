# ==================================================
# 导入库
# ==================================================
import importlib
import time

from loguru import logger

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtNetwork import *
import loguru
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *


class PageTemplate(QFrame):
    # 暂时禁用实例缓存以解决初始化问题
    # _instances = {}
    def __new__(cls, content_widget_class=None, parent: QFrame = None, **kwargs):
        # 直接创建新实例，不使用缓存
        return super(PageTemplate, cls).__new__(cls)

    def __init__(
        self,
        content_widget_class=None,
        parent: QFrame = None,
        is_preview_mode=False,
        **kwargs,
    ):
        super().__init__(parent=parent)

        self.ui_created = False
        self.content_created = False
        self.content_widget_class = content_widget_class
        self._is_preview_mode = is_preview_mode
        self._content_kwargs = kwargs  # 存储传递给内容组件的额外参数

        self.__connectSignalToSlot()
        self.create_ui_components()

    @property
    def is_preview_mode(self):
        """获取是否为预览模式"""
        return self._is_preview_mode

    @is_preview_mode.setter
    def is_preview_mode(self, value):
        """设置是否为预览模式，并在值改变时触发锁定逻辑

        Args:
            value: 是否为预览模式
        """
        self._is_preview_mode = value
        # 如果内容组件已经创建完成，立即执行锁定逻辑
        if (
            self.content_created
            and hasattr(self, "contentWidget")
            and self.contentWidget
        ):
            if value:
                self._lock_all_widgets(self.contentWidget)
            else:
                # 如果不是预览模式，可以选择解锁所有组件
                # 但通常情况下，预览模式是一次性的，所以这里可以不处理
                pass

    def __connectSignalToSlot(self):
        qconfig.themeChanged.connect(setTheme)

    def create_ui_components(self):
        """后台创建UI组件，避免堵塞进程"""
        if self.ui_created:
            return

        # 内存优化：延迟创建滚动区域，只在需要时创建
        self._scroll_area_lazy = None
        self._inner_frame_lazy = None
        self._inner_layout_lazy = None
        self._main_layout_lazy = None
        self.ui_created = True

        if self.content_widget_class:
            self.create_content()

    def _ensure_scroll_area(self):
        """确保滚动区域已创建 - 延迟创建以减少内存使用"""
        if self._scroll_area_lazy is None:
            self._scroll_area_lazy = SingleDirectionScrollArea(self)
            self._scroll_area_lazy.setWidgetResizable(True)
            self._scroll_area_lazy.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollArea QWidget {
                    border: none;
                    background-color: transparent;
                }
            """)
            QScroller.grabGesture(
                self._scroll_area_lazy.viewport(),
                QScroller.ScrollerGestureType.LeftMouseButtonGesture,
            )

            self._inner_frame_lazy = QWidget(self._scroll_area_lazy)
            self._inner_layout_lazy = QVBoxLayout(self._inner_frame_lazy)
            self._inner_layout_lazy.setAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop
            )

            self._scroll_area_lazy.setWidget(self._inner_frame_lazy)

            self._main_layout_lazy = QVBoxLayout(self)
            self._main_layout_lazy.addWidget(self._scroll_area_lazy)

    def create_content(self):
        """后台创建内容组件，避免堵塞进程 - 使用延迟创建的布局"""
        if not self.ui_created or not self.content_widget_class:
            return

        # 确保滚动区域已创建
        self._ensure_scroll_area()

        # 支持传入三种类型的 content_widget_class:
        # 1) 直接的类 / 可调用对象 -> content_widget_class(self)
        # 2) 字符串形式的导入路径，如 'app.view.settings.home:home' 或 'app.view.settings.home.home'
        #    -> 动态导入模块并获取类
        start = time.perf_counter()
        try:
            content_cls = None
            content_name = None
            if isinstance(self.content_widget_class, str):
                path = self.content_widget_class
                content_name = path
                if ":" in path:
                    module_name, attr = path.split(":", 1)
                else:
                    module_name, attr = path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                content_cls = getattr(module, attr)
            else:
                content_cls = self.content_widget_class
                content_name = getattr(content_cls, "__name__", str(content_cls))

            # 如果内容组件尚未创建，创建并添加到布局
            if not self.content_created:
                # 实例化并添加到延迟创建的布局
                # 传递额外参数给内容组件构造函数
                self.contentWidget = content_cls(self, **self._content_kwargs)
                self._inner_layout_lazy.addWidget(self.contentWidget)
                self.content_created = True

                # 如果是预览模式，立即锁定所有组件
                if self.is_preview_mode:
                    self._lock_all_widgets(self.contentWidget)
            else:
                # 如果内容组件已经创建，检查是否需要更新锁定状态
                if hasattr(self, "contentWidget") and self.contentWidget:
                    if self.is_preview_mode:
                        self._lock_all_widgets(self.contentWidget)
                    else:
                        # 如果不是预览模式，可以选择解锁所有组件
                        # 但通常情况下，预览模式是一次性的，所以这里可以不处理
                        pass

            elapsed = time.perf_counter() - start
            loguru.logger.debug(f"创建内容组件 {content_name} 耗时: {elapsed:.3f}s")
        except Exception as e:
            elapsed = time.perf_counter() - start
            from loguru import logger

            logger.exception(f"创建内容组件失败 ({elapsed:.3f}s): {e}")

    def create_empty_content(self, message="该页面正在开发中，敬请期待！"):
        """创建空页面内容"""
        if self.content_created:
            return

        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(20)

        if message:
            custom_label = BodyLabel(message)
            custom_label.setAlignment(Qt.AlignCenter)
            custom_font = load_custom_font()
            if custom_font:
                custom_label.setFont(QFont(custom_font, 12))
            center_layout.addWidget(custom_label)

        empty_layout.addWidget(center_container)
        empty_layout.addStretch()

        self.contentWidget = empty_widget
        self.inner_layout_personal.addWidget(self.contentWidget)
        self.content_created = True

    def _lock_all_widgets(self, widget):
        """递归锁定所有子组件，包括嵌套的组件和GroupHeaderCardWidget内部的控件

        Args:
            widget: 要锁定的根组件
        """
        if widget is None:
            return

        # 首先锁定当前组件
        if hasattr(widget, "setEnabled"):
            widget.setEnabled(False)

        # 特殊处理GroupHeaderCardWidget，确保锁定所有addItem或addGroup添加的控件
        try:
            if hasattr(widget, "widgets"):
                # 如果GroupHeaderCardWidget有widgets属性，锁定所有widgets
                for w in widget.widgets:
                    if isinstance(w, QWidget):
                        self._lock_all_widgets(w)
            elif hasattr(widget, "items"):
                # 如果有items属性，锁定所有items
                for item in widget.items:
                    if hasattr(item, "widget") and isinstance(item.widget, QWidget):
                        self._lock_all_widgets(item.widget)
                    elif isinstance(item, QWidget):
                        self._lock_all_widgets(item)
        except Exception as e:
            logger.debug(f"处理特殊组件时出错: {e}")

        # 然后递归锁定所有直接子组件
        for child in widget.children():
            if isinstance(child, QWidget):
                self._lock_all_widgets(child)

        # 最后，检查是否有contentWidget或其他可能包含控件的属性
        if hasattr(widget, "contentWidget") and isinstance(
            widget.contentWidget, QWidget
        ):
            self._lock_all_widgets(widget.contentWidget)
        if hasattr(widget, "centralWidget") and isinstance(
            widget.centralWidget, QWidget
        ):
            self._lock_all_widgets(widget.centralWidget)

    def clear_instance_cache(cls):
        """清除实例缓存，用于强制重新创建页面"""
        cls._instances.clear()

    @classmethod
    def remove_instance(cls, content_widget_class=None, parent=None):
        """移除特定实例"""
        if content_widget_class is None:
            content_class_name = "None"
        else:
            if hasattr(content_widget_class, "__name__"):
                content_class_name = content_widget_class.__name__
            else:
                content_class_name = str(type(content_widget_class).__name__)

        parent_id = id(parent) if parent else "None"
        instance_key = f"{cls.__name__}_{content_class_name}_{parent_id}"

        if instance_key in cls._instances:
            del cls._instances[instance_key]


class PivotPageTemplate(QFrame):
    """Pivot 导航页面模板类，支持动态加载不同的页面组件

    内存优化：
    - 只保留当前页面在内存中
    - 切换页面时卸载之前的页面
    - 支持按需重新加载
    """

    def __init__(self, page_config: dict, parent: QFrame = None, is_preview_mode=False):
        """
        初始化 Pivot 页面模板

        Args:
            page_config: 页面配置字典，格式为 {"page_name": "display_name", ...}
            parent: 父窗口
            is_preview_mode: 是否为预览模式
        """
        super().__init__(parent=parent)

        self.page_config = page_config  # 页面配置字典
        self.ui_created = False
        self.pages = {}  # 存储页面组件 (scroll areas)
        self.page_infos = {}  # 存储页面附加信息: display, layout, loaded
        self.current_page = None  # 当前页面
        self.base_path = "app.view.settings.list_management"  # 默认基础路径
        self._page_load_order = []  # 页面加载顺序，用于LRU卸载
        self.MAX_CACHED_PAGES = MAX_CACHED_PAGES  # 最大同时保留在内存中的页面数量
        self._is_preview_mode = is_preview_mode

        self.__connectSignalToSlot()

        QTimer.singleShot(0, self.create_ui_components)

    @property
    def is_preview_mode(self):
        """获取是否为预览模式"""
        return self._is_preview_mode

    @is_preview_mode.setter
    def is_preview_mode(self, value):
        """设置是否为预览模式，并在值改变时触发锁定逻辑

        Args:
            value: 是否为预览模式
        """
        self._is_preview_mode = value
        # 如果已经有加载的页面，立即执行锁定逻辑
        if hasattr(self, "page_infos"):
            for page_name, info in self.page_infos.items():
                if info.get("loaded") and info.get("widget"):
                    widget = info.get("widget")
                    if widget:
                        self._lock_all_widgets(widget)

    def __connectSignalToSlot(self):
        """连接信号与槽"""
        qconfig.themeChanged.connect(setTheme)

    def create_ui_components(self):
        """创建UI组件"""
        if self.ui_created:
            return

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建 Pivot 控件
        self.pivot = SegmentedWidget(self)

        # 创建堆叠窗口控件
        self.stacked_widget = QStackedWidget(self)

        # 添加到主布局
        self.main_layout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.stacked_widget)

        # 连接信号
        self.stacked_widget.currentChanged.connect(self.on_current_index_changed)

        self.ui_created = True

        # 添加页面
        self.add_pages()

    def add_pages(self):
        """根据配置添加所有页面"""
        for page_name, display_name in self.page_config.items():
            self.add_page(page_name, display_name)

        # 如果有页面，设置第一个页面为当前页面并仅加载第一个页面的内容
        if self.page_infos:
            first_page_name = next(iter(self.page_infos))
            # 延迟一点点创建第一个页面的内容，避免阻塞
            QTimer.singleShot(
                0,
                lambda n=first_page_name: self._load_page_content(
                    n,
                    self.page_infos[n]["display"],
                    self.page_infos[n]["scroll"],
                    self.page_infos[n]["layout"],
                ),
            )
            self.switch_to_page(first_page_name)

    def add_page(self, page_name: str, display_name: str):
        """
        添加单个页面

        Args:
            page_name: 页面名称，用于导入模块
            display_name: 在 Pivot 中显示的名称
        """
        if not self.ui_created:
            # 如果UI尚未创建，延迟添加
            QTimer.singleShot(
                APP_INIT_DELAY, lambda: self.add_page(page_name, display_name)
            )
            return

        # 创建滑动区域
        scroll_area = SingleDirectionScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        QScroller.grabGesture(
            scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )

        # 创建内部框架
        inner_frame = QWidget(scroll_area)
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop
        )

        scroll_area.setWidget(inner_frame)
        scroll_area.setObjectName(page_name)

        # 添加到堆叠窗口
        self.stacked_widget.addWidget(scroll_area)

        # 添加到 Pivot
        self.pivot.addItem(
            routeKey=page_name,
            text=display_name,
            onClick=lambda: self.switch_to_page(page_name),
        )

        # 存储滑动区域引用
        self.pages[page_name] = scroll_area
        self.page_infos[page_name] = {
            "display": display_name,
            "scroll": scroll_area,
            "layout": inner_layout,
            "loaded": False,
        }

    def _load_page_content(
        self,
        page_name: str,
        display_name: str,
        scroll_area: QScrollArea,
        inner_layout: QVBoxLayout,
    ):
        """
        后台加载页面内容，避免堵塞进程

        Args:
            page_name: 页面名称
            display_name: 在 Pivot 中显示的名称
            scroll_area: 滑动区域
            inner_layout: 内部布局
        """
        try:
            # 动态导入页面组件
            start = time.perf_counter()
            module = importlib.import_module(f"{self.base_path}.{page_name}")
            content_widget_class = getattr(module, page_name)

            # 创建页面组件
            widget = content_widget_class(self)
            widget.setObjectName(page_name)

            # 如果是预览模式，锁定所有组件
            if self.is_preview_mode:
                self._lock_all_widgets(widget)

            # 清除加载提示（使用安全的 takeAt 循环以避免 Qt C++ 对象提前删除问题）
            try:
                while inner_layout.count() > 0:
                    item = inner_layout.takeAt(0)
                    if not item:
                        break
                    w = item.widget()
                    if w is not None:
                        w.deleteLater()
            except RuntimeError:
                # 如果内部对象被底层 Qt 提前销毁，忽略并继续
                pass

            # 添加实际内容到内部布局
            inner_layout.addWidget(widget)

            # 标记为已加载并保存组件引用
            if page_name in self.page_infos:
                self.page_infos[page_name]["loaded"] = True
                self.page_infos[page_name]["widget"] = widget

            elapsed = time.perf_counter() - start
            logger.debug(f"加载页面组件 {page_name} 耗时: {elapsed:.3f}s")

            # 如果当前页面就是正在加载的页面，确保滑动区域是当前可见的
            if self.current_page == page_name:
                self.stacked_widget.setCurrentWidget(scroll_area)

        except (ImportError, AttributeError) as e:
            logger.exception(f"无法导入页面组件 {page_name}: {e}")

            # 清除加载提示（安全地移除所有子项）
            try:
                while inner_layout.count() > 0:
                    item = inner_layout.takeAt(0)
                    if not item:
                        break
                    w = item.widget()
                    if w is not None:
                        w.deleteLater()
            except RuntimeError:
                pass

            # 创建错误页面
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            error_title = BodyLabel("页面加载失败")
            error_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            custom_font = load_custom_font()
            if custom_font:
                error_title.setFont(QFont(custom_font, 16))

            error_content = BodyLabel(f"无法加载页面 {page_name}: {str(e)}")
            error_content.setAlignment(Qt.AlignmentFlag.AlignCenter)

            error_layout.addWidget(error_title)
            error_layout.addWidget(error_content)
            error_layout.addStretch()

            # 添加错误页面到内部布局
            inner_layout.addWidget(error_widget)

            # 标记为已加载（虽然是错误页面，但不再重复尝试）
            if page_name in self.page_infos:
                self.page_infos[page_name]["loaded"] = True

            # 如果当前页面就是正在加载的页面，确保滑动区域是当前可见的
            if self.current_page == page_name:
                self.stacked_widget.setCurrentWidget(scroll_area)

    def switch_to_page(self, page_name: str):
        """切换到指定页面，并卸载不活动的页面以释放内存"""
        if page_name in self.pages:
            # 先卸载超出缓存限制的页面
            self._unload_excess_pages(page_name)

            # 按需加载：如果尚未加载该页面的实际内容，则先加载
            info = self.page_infos.get(page_name)
            if info and not info.get("loaded"):
                # 调用加载函数（同步执行），传入存储的 inner_layout
                self._load_page_content(
                    page_name, info["display"], info["scroll"], info["layout"]
                )

            # 更新加载顺序（LRU）
            if page_name in self._page_load_order:
                self._page_load_order.remove(page_name)
            self._page_load_order.append(page_name)

            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            self.pivot.setCurrentItem(page_name)
            self.current_page = page_name

    def _unload_excess_pages(self, exclude_page: str = None):
        """卸载超出缓存限制的页面以释放内存

        Args:
            exclude_page: 不卸载的页面名称（通常是即将切换到的页面）
        """
        # 获取已加载的页面列表
        loaded_pages = [
            name
            for name, info in self.page_infos.items()
            if info.get("loaded") and name != exclude_page
        ]

        # 如果已加载页面数量超过限制，卸载最早加载的页面
        while len(loaded_pages) >= self.MAX_CACHED_PAGES:
            # 找到最早加载的页面（使用加载顺序列表）
            oldest_page = None
            for page_name in self._page_load_order:
                if page_name in loaded_pages and page_name != exclude_page:
                    oldest_page = page_name
                    break

            if oldest_page is None and loaded_pages:
                # 如果没有在顺序列表中找到，使用第一个
                oldest_page = loaded_pages[0]

            if oldest_page:
                self._unload_page(oldest_page)
                loaded_pages.remove(oldest_page)
                if oldest_page in self._page_load_order:
                    self._page_load_order.remove(oldest_page)
            else:
                break

    def _unload_page(self, page_name: str):
        """卸载指定页面以释放内存

        Args:
            page_name: 要卸载的页面名称
        """
        info = self.page_infos.get(page_name)
        if not info or not info.get("loaded"):
            return

        try:
            # 获取并销毁页面组件
            widget = info.get("widget")
            inner_layout = info.get("layout")

            if widget and inner_layout:
                widget.deleteLater()

                # 清除引用
                info["widget"] = None
                info["loaded"] = False

                logger.debug(f"已卸载页面组件 {page_name} 以释放内存")
        except RuntimeError as e:
            # widget可能已经被销毁
            logger.warning(f"卸载页面 {page_name} 时出现警告: {e}")
            info["widget"] = None
            info["loaded"] = False
        except Exception as e:
            logger.exception(f"卸载页面 {page_name} 失败: {e}")

    def load_all_pages(self, interval_ms: int = 50, max_per_tick: int = 5):
        """
        分批异步加载该 PivotPageTemplate 下所有未加载的页面项。

        内存优化：此方法已禁用批量预加载。
        页面现在完全按需加载，切换时才创建，离开时自动卸载。

        Args:
            interval_ms: 每个批次内相邻项的间隔毫秒数（已禁用）。
            max_per_tick: 每个定时器回调中加载的最大项数（已禁用）。
        """
        # 内存优化：禁用批量预加载，所有页面按需加载
        # 这可以显著减少内存占用
        pass

    def on_current_index_changed(self, index: int):
        """堆叠窗口索引改变时的处理"""
        widget = self.stacked_widget.widget(index)
        if widget:
            self.pivot.setCurrentItem(widget.objectName())
            self.current_page = widget.objectName()

    def get_current_page(self) -> str:
        """获取当前页面名称"""
        return self.current_page

    def _lock_all_widgets(self, widget):
        """递归锁定所有子组件，包括嵌套的组件和GroupHeaderCardWidget内部的控件

        Args:
            widget: 要锁定的根组件
        """
        if widget is None:
            return

        # 首先锁定当前组件
        if hasattr(widget, "setEnabled"):
            widget.setEnabled(False)

        # 特殊处理GroupHeaderCardWidget，确保锁定所有addItem或addGroup添加的控件
        try:
            if hasattr(widget, "widgets"):
                # 如果GroupHeaderCardWidget有widgets属性，锁定所有widgets
                for w in widget.widgets:
                    if isinstance(w, QWidget):
                        self._lock_all_widgets(w)
            elif hasattr(widget, "items"):
                # 如果有items属性，锁定所有items
                for item in widget.items:
                    if hasattr(item, "widget") and isinstance(item.widget, QWidget):
                        self._lock_all_widgets(item.widget)
                    elif isinstance(item, QWidget):
                        self._lock_all_widgets(item)
        except Exception as e:
            logger.debug(f"处理特殊组件时出错: {e}")

        # 然后递归锁定所有直接子组件
        for child in widget.children():
            if isinstance(child, QWidget):
                self._lock_all_widgets(child)

        # 最后，检查是否有contentWidget或其他可能包含控件的属性
        if hasattr(widget, "contentWidget") and isinstance(
            widget.contentWidget, QWidget
        ):
            self._lock_all_widgets(widget.contentWidget)
        if hasattr(widget, "centralWidget") and isinstance(
            widget.centralWidget, QWidget
        ):
            self._lock_all_widgets(widget.centralWidget)

    def get_page(self, page_name: str):
        """根据页面名称获取页面组件"""
        return self.pages.get(page_name, None)

    def set_base_path(self, base_path: str):
        """设置页面模块的基础路径"""
        self.base_path = base_path
