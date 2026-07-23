# ==================================================
# 导入库
# ==================================================
import random
import colorsys
import weakref
from loguru import logger

from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QMenu,
    QSizePolicy,
)
from PySide2.QtGui import QMouseEvent
from PySide2.QtCore import Qt, QPoint, QTimer, QEvent
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    AvatarWidget,
    ElevatedCardWidget,
    qconfig,
)

from app.tools.variable import (
    STUDENT_ID_FORMAT,
    NAME_SPACING,
    SUPPORTED_IMAGE_EXTENSIONS,
    AVATAR_LABEL_SPACING,
    DEFAULT_MIN_SATURATION,
    DEFAULT_MAX_SATURATION,
    DEFAULT_MIN_VALUE,
    DEFAULT_MAX_VALUE,
    LIGHT_VALUE_MULTIPLIER,
    LIGHT_MAX_VALUE_MULTIPLIER,
    DARK_VALUE_MULTIPLIER,
    DARK_MAX_VALUE_MULTIPLIER,
    LIGHT_THEME_MAX_VALUE,
    LIGHT_THEME_ADJUSTED_MAX_VALUE,
    DARK_THEME_MIN_VALUE,
    DARK_THEME_MAX_VALUE,
    RGB_COLOR_FORMAT,
)
from app.tools.path_utils import file_exists, get_data_path
from app.tools.personalised import is_dark_theme
from app.tools.settings_access import readme_settings_async
from app.common.data.list import get_group_members

from random import SystemRandom

system_random = SystemRandom()

# 移除了循环导入，将导入移到函数内部使用


# ==================================================
# 触屏结果显示组件
# ==================================================
class TouchResultWidget(QWidget):
    """支持触屏操作的结果显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 触屏相关变量
        self.is_pressing = False
        self.press_pos = QPoint()
        self.long_press_timer = QTimer(self)
        self.long_press_timer.setSingleShot(True)
        self.long_press_delay = 500  # 长按延迟时间(毫秒)
        self.long_press_timer.timeout.connect(self.handle_long_press)
        self.context_menu_requested = False

        # 滑动相关变量
        self.is_sliding = False
        self.last_pos = QPoint()

        # 内存优化：使用弱引用避免循环引用
        self._cached_mouse_events = []
        self._max_cached_events = 10

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressing = True
            self.press_pos = event.pos()
            self.last_pos = event.pos()
            self.long_press_timer.start(self.long_press_delay)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.is_pressing:
            # 计算移动距离
            delta = event.pos() - self.press_pos
            if abs(delta.x()) > 5 or abs(delta.y()) > 5:
                # 移动距离超过阈值，取消长按
                self.long_press_timer.stop()
                self.is_sliding = True

                # 实现滑动效果
                parent = self.parent()
                while parent:
                    if hasattr(parent, "verticalScrollBar") or hasattr(
                        parent, "horizontalScrollBar"
                    ):
                        # 找到滚动区域，实现滑动
                        if hasattr(parent, "verticalScrollBar"):
                            vbar = parent.verticalScrollBar()
                            vbar.setValue(vbar.value() - delta.y())
                        if hasattr(parent, "horizontalScrollBar"):
                            hbar = parent.horizontalScrollBar()
                            hbar.setValue(hbar.value() - delta.x())
                        self.last_pos = event.pos()
                        break
                    parent = parent.parent()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressing = False
            self.is_sliding = False
            self.long_press_timer.stop()

            # 内存优化：清理缓存的事件对象
            if len(self._cached_mouse_events) > self._max_cached_events // 2:
                self._cached_mouse_events.clear()
        super().mouseReleaseEvent(event)

    def handle_long_press(self):
        """处理长按事件"""
        if self.is_pressing and not self.is_sliding:
            # 模拟右键点击，显示上下文菜单
            self.context_menu_requested = True
            # 创建并显示上下文菜单
            menu = QMenu(self)
            # 可以添加自定义菜单项
            menu.exec(self.mapToGlobal(self.press_pos))
            self.context_menu_requested = False

    def touchEvent(self, event):
        """处理触屏事件"""
        touch_points = event.touchPoints()
        if not touch_points:
            return

        touch_point = touch_points[0]
        touch_pos = touch_point.pos().toPoint()

        # 内存优化：复用鼠标事件对象
        if touch_point.state() == Qt.TouchPointState.Pressed:
            # 触屏按下
            mouse_event = self._get_cached_mouse_event(
                QEvent.Type.MouseButtonPress, touch_pos, Qt.MouseButton.LeftButton
            )
            self.mousePressEvent(mouse_event)
        elif touch_point.state() == Qt.TouchPointState.Moved:
            # 触屏移动
            mouse_event = self._get_cached_mouse_event(
                QEvent.Type.MouseMove, touch_pos, Qt.MouseButton.LeftButton
            )
            self.mouseMoveEvent(mouse_event)
        elif touch_point.state() == Qt.TouchPointState.Released:
            # 触屏释放
            mouse_event = self._get_cached_mouse_event(
                QEvent.Type.MouseButtonRelease, touch_pos, Qt.MouseButton.LeftButton
            )
            self.mouseReleaseEvent(mouse_event)

    def _get_cached_mouse_event(self, event_type, pos, button):
        """获取缓存的鼠标事件对象，减少内存分配"""
        # 清理过期的事件缓存
        self._cached_mouse_events = [
            event for event in self._cached_mouse_events if event is not None
        ]

        if len(self._cached_mouse_events) < self._max_cached_events:
            event = QMouseEvent(
                event_type,
                pos,
                button,
                button
                if event_type != QEvent.Type.MouseButtonRelease
                else Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )
            self._cached_mouse_events.append(event)
            return event
        else:
            # 如果缓存已满，创建新事件并替换最旧的
            return QMouseEvent(
                event_type,
                pos,
                button,
                button
                if event_type != QEvent.Type.MouseButtonRelease
                else Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )


# ==================================================
# 结果显示工具类
# ==================================================
class ResultDisplayUtils:
    """结果显示工具类，提供通用的结果显示功能"""

    _color_cache = {}
    _max_cache_size = 100  # 限制颜色缓存大小
    _weak_widget_refs = weakref.WeakSet()  # 使用弱引用跟踪widget

    @staticmethod
    def _clear_color_cache():
        """清除颜色缓存"""
        ResultDisplayUtils._color_cache.clear()

    @staticmethod
    def _init_theme_listener():
        """初始化主题变化监听器"""
        if not hasattr(ResultDisplayUtils, "_theme_listener_initialized"):
            qconfig.themeChanged.connect(ResultDisplayUtils._clear_color_cache)
            ResultDisplayUtils._theme_listener_initialized = True

    @staticmethod
    def _create_avatar_widget(image_path, name, font_size):
        """
        创建头像组件

        参数:
            image_path: 图片路径
            name: 学生姓名
            font_size: 字体大小

        返回:
            AvatarWidget: 创建的头像组件
        """
        if image_path is not None:
            avatar = AvatarWidget(image_path)
        else:
            avatar = AvatarWidget()
            avatar.setText(name)

        return avatar

    @staticmethod
    def _format_student_text(
        class_name,
        display_format,
        student_id_str,
        name,
        draw_count,
        is_group_mode=False,
        show_random=0,
    ):
        """
        格式化学生显示文本

        参数:
            display_format: 显示格式 (0:学号+姓名, 1:仅姓名, 2:仅学号)
            student_id_str: 学号字符串
            name: 学生姓名或小组名称
            draw_count: 抽取人数
            is_group_mode: 是否为小组模式
            show_random: 随机组员显示格式 (0:不显示, 1:组名[换行]姓名, 2:组名[短横杠]姓名)

        返回:
            str: 格式化后的文本
        """
        # 小组模式下，根据show_random设置显示格式
        if is_group_mode:
            # 获取小组成员列表
            group_members = get_group_members(class_name, name)

            if show_random == 1:  # 组名[换行]随机选择的成员
                if group_members:
                    # 随机选择一个成员
                    selected_member = system_random.choice(group_members)
                    selected_name = selected_member["name"]
                    return f"{name}\n{selected_name}"
                else:
                    return name
            elif show_random == 2:  # 组名[短横杠]随机选择的成员
                if group_members:
                    # 随机选择一个成员
                    selected_member = system_random.choice(group_members)
                    selected_name = selected_member["name"]
                    return f"{name} - {selected_name}"
                else:
                    return name
            else:  # 不显示特殊格式 - 只显示组名
                return f"{name}"

        if display_format == 1:  # 仅显示姓名
            return f"{name}"
        elif display_format == 2:  # 仅显示学号
            if not student_id_str:
                return f"{name}"
            return f"{student_id_str}"
        else:  # 显示学号+姓名
            if draw_count == 1:
                return f"{student_id_str}\n{name}"
            else:
                return f"{student_id_str} {name}"

    @staticmethod
    def _create_student_label_with_avatar(
        image_path, name, font_size, draw_count, text, image_position=0
    ):
        """
        创建带头像的学生标签

        参数:
            image_path: 图片路径
            name: 学生姓名
            font_size: 字体大小
            draw_count: 抽取人数
            text: 显示文本

        返回:
            QWidget: 包含头像和文本的容器组件
        """
        # 内存优化：使用更轻量的布局策略
        container = QWidget()
        container.setAttribute(Qt.WA_DeleteOnClose)  # 自动清理

        try:
            image_position = int(image_position)
        except Exception:
            image_position = 0

        use_vertical_layout = image_position in (1, 3)
        layout = (
            QVBoxLayout(container) if use_vertical_layout else QHBoxLayout(container)
        )
        layout.setSpacing(AVATAR_LABEL_SPACING)
        layout.setContentsMargins(0, 0, 0, 0)

        avatar = ResultDisplayUtils._create_avatar_widget(image_path, name, font_size)
        avatar.setRadius(font_size * 2 if draw_count == 1 else int(font_size * 1.5))

        text_label = BodyLabel(text)

        if image_position == 3:
            layout.addWidget(text_label, 0, Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignHCenter)
        elif image_position == 2:
            layout.addWidget(text_label, 0, Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignVCenter)
        elif image_position == 1:
            layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(text_label, 0, Qt.AlignmentFlag.AlignHCenter)
        else:
            layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(text_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # 内存优化：跟踪创建的widget以便清理
        ResultDisplayUtils._weak_widget_refs.add(container)

        return container

    @staticmethod
    def _get_style_color(animation_color, fixed_color):
        """获取样式颜色"""
        if animation_color == 1:
            return ResultDisplayUtils._generate_vibrant_color()
        elif animation_color == 2:
            return fixed_color
        else:
            try:
                from app.tools.personalised import is_dark_theme
                from qfluentwidgets import qconfig

                return "#ffffff" if is_dark_theme(qconfig) else "#000000"
            except Exception:
                return "#000000"

    @staticmethod
    def _apply_label_style(
        label,
        font_size,
        animation_color,
        settings_group="roll_call_settings",
        custom_font_family="",
        style_sheet=None,
    ):
        """
        应用标签样式

        参数:
            label: 标签组件
            font_size: 字体大小
            animation_color: 动画颜色模式
            settings_group: 设置组名称，默认为roll_call_settings
            custom_font_family: 自定义字体族
        """
        if style_sheet is None:
            fixed_color = readme_settings_async(settings_group, "animation_fixed_color")
            color_str = ResultDisplayUtils._get_style_color(
                animation_color, fixed_color
            )
            style_sheet = ResultDisplayUtils._build_text_style_sheet(
                font_size,
                color_str,
                settings_group,
                custom_font_family=custom_font_family,
            )

        def apply_to_widget(widget):
            if isinstance(widget, BodyLabel):
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                widget.setStyleSheet(style_sheet)
                return
            if isinstance(widget, QWidget) and widget.layout() is not None:
                layout = widget.layout()
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    child = item.widget()
                    if child is not None:
                        apply_to_widget(child)

        if isinstance(label, QWidget):
            apply_to_widget(label)

    @staticmethod
    def _build_text_style_sheet(
        font_size,
        color_str,
        settings_group="roll_call_settings",
        *,
        custom_font_family="",
    ):
        use_global_font = readme_settings_async(settings_group, "use_global_font")
        custom_font = None
        if use_global_font == 1:
            custom_font = readme_settings_async(settings_group, "custom_font")
        if custom_font_family:
            custom_font = custom_font_family

        style_sheet = f"font-size: {font_size}pt; color: {color_str} !important;"
        if custom_font and use_global_font == 1:
            style_sheet = f"font-family: '{custom_font}'; {style_sheet}"
        return style_sheet

    @staticmethod
    def _find_student_image(image_dir, image_name):
        """查找学生图片"""
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            path = get_data_path("images", f"{image_dir}/{image_name}{ext}")
            if file_exists(path):
                return str(path)
        return None

    @staticmethod
    def create_student_label(
        class_name,
        selected_students,
        selected_students_dict=None,
        draw_count=1,
        font_size=50,
        animation_color=0,
        display_format=0,
        display_style=None,
        show_student_image=False,
        image_position=None,
        group_index=0,
        show_random=0,
        settings_group="roll_call_settings",
        custom_font_family="",
        show_tags=False,
    ):
        """
        创建学生显示标签

        参数:
            selected_students: 选中的学生列表 [(num, selected, exist), ...]
            draw_count: 抽取人数
            font_size: 字体大小
            animation_color: 动画颜色模式 (0:默认, 1:随机颜色, 2:固定颜色)
            display_format: 显示格式 (0:学号+姓名, 1:仅姓名, 2:仅学号)
            show_student_image: 是否显示学生头像
            group_index: 小组索引 (0:全班, 1:随机小组, >1:指定小组)
            show_random: 随机组员显示格式 (0:不显示, 1:组名[换行]姓名, 2:组名[短横杠]姓名)
            settings_group: 设置组名称，默认为roll_call_settings
            custom_font_family: 自定义字体族

        返回:
            list: 创建的标签列表
        """
        # 检查 selected_students 是否为 None，避免后续的 len() 调用和迭代操作失败
        if selected_students is None:
            logger.warning(
                "create_student_label: selected_students 为 None，可能是未设置默认班级或抽取名单"
            )
            return []

        student_labels = [None] * len(selected_students)

        # 确定图片目录
        image_dir = (
            "prize_images" if settings_group == "lottery_settings" else "student_images"
        )
        if display_style is None:
            try:
                display_style = readme_settings_async(settings_group, "display_style")
            except Exception:
                display_style = 0

        image_position_key = (
            "lottery_image_position"
            if settings_group == "lottery_settings"
            else "student_image_position"
        )
        if image_position is None:
            try:
                image_position = readme_settings_async(
                    settings_group, image_position_key
                )
            except Exception:
                image_position = 0

        try:
            image_position = int(image_position)
        except Exception:
            image_position = 0

        fixed_color = readme_settings_async(settings_group, "animation_fixed_color")

        for i, (num, selected, exist) in enumerate(selected_students):
            current_image_path = None
            if show_student_image:
                image_name = str(selected)
                if settings_group == "lottery_settings":
                    image_name = (
                        image_name.splitlines()[0] if image_name else image_name
                    )
                current_image_path = ResultDisplayUtils._find_student_image(
                    image_dir, image_name
                )

            # 处理学号格式化
            student_id_str = (
                STUDENT_ID_FORMAT.format(num=num) if num is not None else ""
            )

            # 处理不同模式下的名称显示
            name = (
                f"{str(selected)[0]}{NAME_SPACING}{str(selected)[1]}"
                if len(str(selected)) == 2 and group_index == 0
                else str(selected)
            )

            text = ResultDisplayUtils._format_student_text(
                class_name,
                display_format,
                student_id_str,
                name,
                draw_count,
                is_group_mode=(group_index == 1),
                show_random=show_random,
            )
            # 使用支持触屏的容器包装所有内容，确保整个区域都能响应触屏操作
            touch_container = TouchResultWidget()
            touch_container.setAttribute(Qt.WA_DeleteOnClose)  # 自动清理

            # 内存优化：使用更轻量的布局策略
            inner_layout = QVBoxLayout() if draw_count == 1 else QHBoxLayout()
            inner_layout.setContentsMargins(0, 0, 0, 0)
            inner_layout.setSpacing(0)
            touch_container.setLayout(inner_layout)

            # 在小组模式下，只在没有成员显示时才显示头像
            if show_student_image:
                label = ResultDisplayUtils._create_student_label_with_avatar(
                    current_image_path,
                    name,
                    font_size,
                    draw_count,
                    text,
                    image_position,
                )
            else:
                label = BodyLabel(text)
                label.setAttribute(Qt.WA_DeleteOnClose)  # 自动清理

            color_str = ResultDisplayUtils._get_style_color(
                animation_color, fixed_color
            )
            main_style_sheet = ResultDisplayUtils._build_text_style_sheet(
                font_size,
                color_str,
                settings_group,
                custom_font_family=custom_font_family,
            )

            tag_text = ""
            if show_tags and selected_students_dict and i < len(selected_students_dict):
                current_item = selected_students_dict[i]
                if isinstance(current_item, dict):
                    tags = current_item.get("tags") or []
                    if isinstance(tags, str):
                        tags = [tags]
                    if isinstance(tags, (list, tuple)):
                        normalized = []
                        for t in tags:
                            t = str(t or "").strip()
                            if t:
                                normalized.append(t)
                        if normalized:
                            tag_text = " · ".join(normalized)

            if tag_text:
                try:
                    tag_font_size = max(1, int(int(font_size) / 2.5))
                except Exception:
                    tag_font_size = 1
                tag_label = CaptionLabel(tag_text)
                tag_label.setAttribute(Qt.WA_DeleteOnClose)
                tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                tag_label.setStyleSheet(
                    ResultDisplayUtils._build_text_style_sheet(
                        tag_font_size,
                        color_str,
                        settings_group,
                        custom_font_family=custom_font_family,
                    )
                )

                wrapper = QWidget()
                wrapper.setAttribute(Qt.WA_DeleteOnClose)
                wrapper_layout = QVBoxLayout(wrapper)
                wrapper_layout.setContentsMargins(0, 0, 0, 0)
                wrapper_layout.setSpacing(2)
                wrapper_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
                wrapper_layout.addWidget(tag_label, 0, Qt.AlignmentFlag.AlignCenter)
                label = wrapper

            card_widget = None
            if display_style == 1:
                card_widget = ElevatedCardWidget()
                card_widget.setAttribute(Qt.WA_DeleteOnClose)
                card_layout = QVBoxLayout(card_widget)
                card_layout.setContentsMargins(12, 12, 12, 12)
                card_layout.setSpacing(4)
                card_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
                label = card_widget

            ResultDisplayUtils._apply_label_style(
                label,
                font_size,
                animation_color,
                settings_group,
                custom_font_family,
                style_sheet=main_style_sheet,
            )

            if card_widget is not None:
                card_widget.setSizePolicy(
                    QSizePolicy.Policy.MinimumExpanding,
                    QSizePolicy.Policy.MinimumExpanding,
                )
                layout = card_widget.layout()
                if layout is not None:
                    layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
                    layout.activate()
                    card_widget.setMinimumSize(layout.sizeHint())

            # 将标签添加到触屏容器中
            inner_layout.addWidget(label)
            student_labels[i] = touch_container

        return student_labels

    @staticmethod
    def _generate_vibrant_color(
        min_saturation=DEFAULT_MIN_SATURATION,
        max_saturation=DEFAULT_MAX_SATURATION,
        min_value=DEFAULT_MIN_VALUE,
        max_value=DEFAULT_MAX_VALUE,
        use_cache=True,
    ):
        """生成鲜艳直观的颜色

        根据当前主题自动调整颜色明亮程度：
        - 浅色主题：降低亮度范围，避免颜色过于明亮导致看不清
        - 深色主题：使用正常亮度范围，确保颜色在深色背景上清晰可见

        参数:
            min_saturation: 最小饱和度 (默认DEFAULT_MIN_SATURATION)
            max_saturation: 最大饱和度 (默认DEFAULT_MAX_SATURATION)
            min_value: 最小亮度值 (默认DEFAULT_MIN_VALUE)
            max_value: 最大亮度值 (默认DEFAULT_MAX_VALUE)
            use_cache: 是否使用颜色缓存 (默认True)

        返回:
            str: RGB格式的颜色字符串，如"rgb(255,100,50)"
        """
        ResultDisplayUtils._init_theme_listener()

        # 内存优化：限制缓存大小，防止无限增长
        if (
            use_cache
            and len(ResultDisplayUtils._color_cache)
            >= ResultDisplayUtils._max_cache_size
        ):
            # 清除最旧的50%缓存项
            keys_to_remove = list(ResultDisplayUtils._color_cache.keys())[
                : ResultDisplayUtils._max_cache_size // 2
            ]
            for key in keys_to_remove:
                ResultDisplayUtils._color_cache.pop(key, None)

        if is_dark_theme(qconfig):  # 深色主题
            adjusted_min_value = min(
                min_value * DARK_VALUE_MULTIPLIER, DARK_THEME_MIN_VALUE
            )
            adjusted_max_value = max(
                max_value * DARK_MAX_VALUE_MULTIPLIER, DARK_THEME_MAX_VALUE
            )
        else:  # 浅色主题
            adjusted_min_value = min(
                min_value * LIGHT_VALUE_MULTIPLIER, LIGHT_THEME_MAX_VALUE
            )
            adjusted_max_value = min(
                max_value * LIGHT_MAX_VALUE_MULTIPLIER, LIGHT_THEME_ADJUSTED_MAX_VALUE
            )

        h = random.random()
        s = random.uniform(min_saturation, max_saturation)
        v = random.uniform(adjusted_min_value, adjusted_max_value)
        r, g, b = (int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))
        color_str = RGB_COLOR_FORMAT.format(r=r, g=g, b=b)

        # 内存优化：只在启用缓存时存储颜色
        if use_cache:
            ResultDisplayUtils._color_cache[color_str] = True

        return color_str

    @staticmethod
    def display_results_in_grid(result_grid, student_labels, alignment=None):
        """
        在网格布局中显示结果

        参数:
            result_grid: QGridLayout 网格布局
            student_labels: 学生标签列表
            alignment: 对齐方式 (默认为居中)
        """
        if alignment is None:
            alignment = Qt.AlignmentFlag.AlignCenter
        result_grid.setAlignment(alignment)
        parent_widget = None
        if hasattr(result_grid, "parentWidget"):
            try:
                parent_widget = result_grid.parentWidget()
            except Exception:
                parent_widget = None
        if parent_widget is None and hasattr(result_grid, "parent"):
            try:
                obj = result_grid.parent()
                while obj is not None and not isinstance(obj, QWidget):
                    obj = obj.parent()
                if isinstance(obj, QWidget):
                    parent_widget = obj
            except Exception:
                parent_widget = None

        ResultDisplayUtils.clear_grid(result_grid)

        if not student_labels:
            if parent_widget:
                try:
                    layout = parent_widget.layout()
                    if layout is not None:
                        layout.invalidate()
                        layout.activate()
                except Exception:
                    pass
                parent_widget.updateGeometry()
            return

        widgets = list(student_labels)
        for w in widgets:
            result_grid.addWidget(w)

        if hasattr(result_grid, "removeAllWidgets"):
            try:
                result_grid.removeAllWidgets()
                for w in widgets:
                    result_grid.addWidget(w)
            except Exception:
                pass

        if parent_widget:
            try:
                layout = parent_widget.layout()
                if layout is not None:
                    layout.invalidate()
                    layout.activate()
            except Exception:
                pass
            parent_widget.updateGeometry()

    @staticmethod
    def collect_grid_widgets(result_grid):
        widgets = []
        if not hasattr(result_grid, "count") or not hasattr(result_grid, "itemAt"):
            return widgets
        for i in range(result_grid.count()):
            item = result_grid.itemAt(i)
            if not item or not hasattr(item, "widget"):
                continue
            widget = item.widget()
            if widget:
                widgets.append(widget)
        return widgets

    @staticmethod
    def dispose_widgets(widgets):
        if not widgets:
            return
        for widget in widgets:
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

    @staticmethod
    def update_grid_labels(result_grid, new_labels, cached_labels):
        """
        更新网格布局中的标签内容（优化动画性能）

        参数:
            result_grid: QGridLayout 网格布局
            new_labels: 新的学生标签列表
            cached_labels: 缓存的旧标签列表

        返回:
            bool: 始终返回False，强制重新创建组件以确保头像正确显示
        """
        # 简化逻辑：始终返回False，强制重新创建所有组件
        # 这样可以避免头像缓存导致的显示问题
        return False

    @staticmethod
    def clear_grid(result_grid, log_debug=False):
        """
        清空网格布局中的所有小部件

        参数:
            result_grid: QGridLayout 网格布局
            log_debug: 是否输出调试日志（默认为False）
        """
        if not hasattr(result_grid, "count") or not hasattr(result_grid, "takeAt"):
            if hasattr(result_grid, "removeAllWidgets"):
                try:
                    result_grid.removeAllWidgets()
                except Exception:
                    pass
            ResultDisplayUtils._color_cache.clear()
            return

        count = result_grid.count()
        if count == 0:
            ResultDisplayUtils._color_cache.clear()
            return

        removed_count = 0
        while result_grid.count():
            item = result_grid.takeAt(0)
            if not item:
                break
            widget = None
            if isinstance(item, QWidget):
                widget = item
            elif hasattr(item, "widget"):
                try:
                    widget = item.widget()
                except Exception:
                    widget = None
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
                removed_count += 1
                continue
            child_layout = None
            if hasattr(item, "layout"):
                try:
                    child_layout = item.layout()
                except Exception:
                    child_layout = None
            if child_layout:
                ResultDisplayUtils.clear_grid(child_layout)
                try:
                    child_layout.deleteLater()
                except Exception:
                    pass

        if log_debug and removed_count > 0:
            logger.debug(f"本次销毁了{removed_count}个组件")

        ResultDisplayUtils._color_cache.clear()

    @staticmethod
    def show_notification_if_enabled(
        class_name,
        selected_students,
        draw_count=1,
        settings=None,
        settings_group=None,
        is_animating=False,
    ):
        """
        如果启用了通知服务，则显示抽取结果通知

        参数:
            class_name: 班级名称
            selected_students: 选中的学生列表
            draw_count: 抽取人数
            settings: 通知设置参数
            settings_group: 设置组名称
            is_animating: 是否在动画过程中，如果是则不启动自动关闭定时器
        """
        # 检查是否启用了通知服务（这个检查应该由调用方完成）
        from app.common.notification.notification_service import (
            show_roll_call_notification,
        )

        show_roll_call_notification(
            class_name,
            selected_students,
            draw_count,
            settings,
            settings_group,
            is_animating,
        )

    @staticmethod
    def cleanup_memory():
        """
        清理内存占用，释放不再使用的资源
        建议在大量操作后调用此方法来释放内存
        """
        # 清理颜色缓存
        ResultDisplayUtils._color_cache.clear()

        # 清理弱引用集合
        ResultDisplayUtils._weak_widget_refs.clear()

        # 可选：强制垃圾回收
        # import gc
        # gc.collect()

        logger.debug("ResultDisplayUtils内存清理完成")
