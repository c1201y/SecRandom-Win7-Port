import sys
import importlib.util
from loguru import logger
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide2.QtCore import QUrl, Qt
from PySide2.QtGui import QColor

from app.tools.path_utils import get_data_path
from app.tools.settings_access import readme_settings_async


class ThemeLoader:
    @staticmethod
    def load_theme_widget(page_type, default_class):
        """
        从主题中加载页面组件，失败时返回默认组件
        page_type: 'roll_call' 或 'lottery'
        """
        try:
            theme_id = ThemeLoader._get_theme_id_for_page(page_type)
            if not theme_id:
                return default_class

            theme_dir = get_data_path("themes") / theme_id
            if not theme_dir.exists():
                return default_class

            folder_name = ThemeLoader._get_page_folder(page_type)
            if not folder_name:
                return default_class

            target_dir = theme_dir / folder_name
            if not target_dir.exists():
                return default_class

            preferred_type = ""
            if page_type == "roll_call":
                preferred_type = readme_settings_async(
                    "theme_management", "roll_call_theme_type"
                )
            elif page_type == "lottery":
                preferred_type = readme_settings_async(
                    "theme_management", "lottery_theme_type"
                )
            preferred_type = str(preferred_type or "").lower().strip()

            py_file = target_dir / "main.py"
            html_file = target_dir / "main.html"
            if not html_file.exists():
                html_file = target_dir / "index.html"
            if preferred_type == "html":
                if html_file.exists():
                    widget_class = ThemeLoader._load_widget_from_html(html_file)
                    if widget_class:
                        return widget_class
                if py_file.exists():
                    module_name = f"theme_{theme_id}_{page_type}"
                    widget_class = ThemeLoader._load_widget_from_py(
                        py_file, default_class, module_name
                    )
                    if widget_class:
                        return widget_class
            else:
                if preferred_type == "py" and py_file.exists():
                    module_name = f"theme_{theme_id}_{page_type}"
                    widget_class = ThemeLoader._load_widget_from_py(
                        py_file, default_class, module_name
                    )
                    if widget_class:
                        return widget_class
                if py_file.exists():
                    module_name = f"theme_{theme_id}_{page_type}"
                    widget_class = ThemeLoader._load_widget_from_py(
                        py_file, default_class, module_name
                    )
                    if widget_class:
                        return widget_class
                if html_file.exists():
                    widget_class = ThemeLoader._load_widget_from_html(html_file)
                    if widget_class:
                        return widget_class

            return default_class
        except Exception as e:
            logger.exception(f"加载主题页面组件失败: {e}")
            return default_class

    @staticmethod
    def _get_theme_id_for_page(page_type):
        if page_type == "roll_call":
            theme_id = readme_settings_async("theme_management", "roll_call_theme_id")
            if str(theme_id) == "__none__":
                return ""
            if theme_id:
                return theme_id
        if page_type == "lottery":
            theme_id = readme_settings_async("theme_management", "lottery_theme_id")
            if str(theme_id) == "__none__":
                return ""
            if theme_id:
                return theme_id
        return ""

    @staticmethod
    def _get_page_folder(page_type):
        folder_map = {
            "roll_call": "Roll_call_page",
            "lottery": "Lottery_page",
        }
        return folder_map.get(page_type)

    @staticmethod
    def _load_widget_from_py(py_file, default_class, module_name):
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            target_class_name = default_class.__name__
            if hasattr(module, target_class_name):
                return getattr(module, target_class_name)

            if hasattr(module, "Main"):
                return module.Main

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, QWidget)
                    and attr is not QWidget
                ):
                    return attr

            logger.warning(f"未找到可用的主题类: {py_file}")
            return None
        except Exception as e:
            logger.error(f"加载主题 Python 文件失败 {py_file}: {e}")
            return None

    @staticmethod
    def _load_widget_from_html(html_file):
        try:
            from PySide2.QtWebEngineWidgets import QWebEngineView

            class WebViewWrapper(QWidget):
                def __init__(self, parent=None, **kwargs):
                    super().__init__(parent)
                    self.setProperty("theme_html_wrapper", True)
                    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                    self.setStyleSheet("background: transparent;")
                    self.setSizePolicy(
                        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                    )
                    self.layout = QVBoxLayout(self)
                    self.layout.setContentsMargins(0, 0, 0, 0)
                    self.layout.setSpacing(0)
                    self.webview = QWebEngineView()
                    self.webview.setAttribute(
                        Qt.WidgetAttribute.WA_TranslucentBackground, True
                    )
                    self.webview.setStyleSheet("background: transparent;")
                    self.webview.setSizePolicy(
                        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                    )
                    self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
                    self.webview.settings().setAttribute(
                        self.webview.settings().WebAttribute.LocalContentCanAccessRemoteUrls,
                        True,
                    )
                    self.webview.settings().setAttribute(
                        self.webview.settings().WebAttribute.LocalContentCanAccessFileUrls,
                        True,
                    )
                    self.webview.loadFinished.connect(self._apply_fullscreen_css)
                    self.webview.load(QUrl.fromLocalFile(str(html_file.absolute())))
                    self.layout.addWidget(self.webview)

                def _apply_fullscreen_css(self, ok: bool):
                    if not ok:
                        return
                    script = """
                        try {
                            document.documentElement.style.height = '100%';
                            document.documentElement.style.width = '100%';
                            document.documentElement.style.margin = '0';
                            document.documentElement.style.padding = '0';
                            document.body.style.height = '100%';
                            document.body.style.width = '100%';
                            document.body.style.margin = '0';
                            document.body.style.padding = '0';
                            document.body.style.overflow = 'hidden';
                        } catch (e) {}
                    """
                    self.webview.page().runJavaScript(script)

            return WebViewWrapper
        except ImportError:
            try:
                from PySide2.QtWidgets import QTextBrowser

                class HtmlWrapper(QWidget):
                    def __init__(self, parent=None, **kwargs):
                        super().__init__(parent)
                        self.setProperty("theme_html_wrapper", True)
                        self.setAttribute(
                            Qt.WidgetAttribute.WA_TranslucentBackground, True
                        )
                        self.setStyleSheet("background: transparent;")
                        self.setSizePolicy(
                            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                        )
                        self.layout = QVBoxLayout(self)
                        self.layout.setContentsMargins(0, 0, 0, 0)
                        self.layout.setSpacing(0)
                        self.browser = QTextBrowser(self)
                        self.browser.setSizePolicy(
                            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                        )
                        self.browser.setStyleSheet(
                            "background: transparent; border: none;"
                        )
                        self.browser.setOpenExternalLinks(True)
                        self.browser.setSource(
                            QUrl.fromLocalFile(str(html_file.absolute()))
                        )
                        self.layout.addWidget(self.browser)

                return HtmlWrapper
            except Exception as e:
                logger.error(f"缺少 QtWebEngineWidgets，无法加载 HTML 主题: {e}")
                return None
