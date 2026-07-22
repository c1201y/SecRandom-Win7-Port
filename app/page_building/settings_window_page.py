# 导入库
from PySide2.QtWidgets import QFrame

# 导入页面模板
from app.page_building.page_template import PageTemplate, PivotPageTemplate

# 导入自定义页面内容组件
# 为了延迟导入，传入字符串路径，实际类将在 PageTemplate.create_content 动态导入
# content path format: 'module.submodule:ClassName' 或 'module.submodule.ClassName'
BASIC_SETTINGS_PATH = "app.view.settings.basic_settings:basic_settings"
FLOATING_WINDOW_MANAGEMENT_PATH = (
    "app.view.settings.floating_window_management:floating_window_management"
)
SAFETY_SETTINGS_PATH = "app.view.settings.safety_settings:safety_settings"
UPDATE_PATH = "app.view.settings.update:update"
ABOUT_PATH = "app.view.settings.about:about"
LINKAGE_SETTINGS_PATH = "app.view.settings.linkage_settings:linkage_settings"
THEME_MANAGEMENT_PATH = (
    "app.view.settings.theme_management.theme_management:ThemeManagement"
)

# 导入默认设置
from app.tools.settings_default import *
from app.Language.obtain_language import *


class basic_settings_page(PageTemplate):
    """创建基础设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=BASIC_SETTINGS_PATH,
            parent=parent,
            is_preview_mode=is_preview,
        )


class list_management_page(PivotPageTemplate):
    """创建名单管理页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        page_config = {
            "list_management": get_content_name_async("list_management", "title"),
            "roll_call_table": get_content_name_async("roll_call_table", "title"),
            "lottery_table": get_content_name_async("lottery_table", "title"),
        }
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.list_management")


class extraction_settings_page(PivotPageTemplate):
    """创建抽取设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        page_config = {
            "roll_call_settings": get_content_name_async("roll_call_settings", "title"),
            "quick_draw_settings": get_content_name_async(
                "quick_draw_settings", "title"
            ),
            "lottery_settings": get_content_name_async("lottery_settings", "title"),
            "face_detector_settings": get_content_name_async(
                "face_detector_settings", "title"
            ),
        }
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.extraction_settings")


class floating_window_management_page(PageTemplate):
    """创建悬浮窗管理页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=FLOATING_WINDOW_MANAGEMENT_PATH,
            parent=parent,
            is_preview_mode=is_preview,
        )


class notification_settings_page(PivotPageTemplate):
    """创建通知服务页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        page_config = {
            "roll_call_notification_settings": get_content_name_async(
                "roll_call_notification_settings", "title"
            ),
            "quick_draw_notification_settings": get_content_name_async(
                "quick_draw_notification_settings", "title"
            ),
            "lottery_notification_settings": get_content_name_async(
                "lottery_notification_settings", "title"
            ),
        }
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.notification_settings")


class safety_settings_page(PageTemplate):
    """创建安全设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=SAFETY_SETTINGS_PATH,
            parent=parent,
            is_preview_mode=is_preview,
        )


class voice_settings_page(PivotPageTemplate):
    """创建语音设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        page_config = {
            "basic_voice_settings": get_content_name_async(
                "basic_voice_settings", "title"
            ),
            "specific_announcements": get_content_name_async(
                "specific_announcements", "title"
            ),
        }
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.voice_settings")


class history_page(PivotPageTemplate):
    """创建历史记录页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        page_config = {
            "history_management": get_content_name_async("history_management", "title"),
            "roll_call_history_table": get_content_name_async(
                "roll_call_history_table", "title"
            ),
            "lottery_history_table": get_content_name_async(
                "lottery_history_table", "title"
            ),
        }
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.history")


class linkage_settings_page(PageTemplate):
    """创建联动设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=LINKAGE_SETTINGS_PATH,
            parent=parent,
            is_preview_mode=is_preview,
        )


class theme_management_page(PageTemplate):
    """创建主题管理页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=THEME_MANAGEMENT_PATH,
            parent=parent,
            is_preview_mode=is_preview,
        )


class more_settings_page(PivotPageTemplate):
    """创建更多设置页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        from app.common.safety.secure_store import read_behind_scenes_settings

        # 读取横幅点击次数
        click_count = 0
        try:
            data = read_behind_scenes_settings()
            click_count = data.get("banner_click_count", 0)
        except Exception:
            pass

        # 只有点击次数 >= 10 时才显示内幕设置页面
        show_behind_scenes = click_count >= 10

        page_config = {
            "fair_draw": get_content_name_async("fair_draw_settings", "title"),
            "shortcut_settings": get_content_name_async("shortcut_settings", "title"),
            "music_settings": get_content_name_async("music_settings", "title"),
            "page_management": get_content_name_async("page_management", "title"),
            "sidebar_tray_management": get_content_name_async(
                "sidebar_tray_management", "title"
            ),
        }
        if show_behind_scenes:
            page_config["behind_scenes_settings"] = get_content_name_async(
                "behind_scenes_settings", "title"
            )
        super().__init__(page_config, parent, is_preview_mode=is_preview)
        self.set_base_path("app.view.settings.more_settings")


class update_page(PageTemplate):
    """创建更新页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=UPDATE_PATH, parent=parent, is_preview_mode=is_preview
        )


class about_page(PageTemplate):
    """创建关于页面"""

    def __init__(self, parent: QFrame = None, is_preview=False):
        super().__init__(
            content_widget_class=ABOUT_PATH, parent=parent, is_preview_mode=is_preview
        )
