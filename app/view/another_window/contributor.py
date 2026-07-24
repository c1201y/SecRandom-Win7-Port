# ==================================================
# 导入库
# ==================================================

from loguru import logger
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.view.components.center_flow_layout import CenterFlowLayout
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.variable import *


# ==================================================
# 贡献者页面类
# ==================================================
class contributor_page(QWidget):
    """贡献者信息页面 - 显示项目贡献者信息，采用响应式网格布局"""

    def __init__(self, parent=None):
        """初始化贡献者页面"""
        super().__init__(parent)
        self.setObjectName("contributor_page")
        self._closing = False

        # 初始化UI组件
        self._init_ui()

        # 初始化数据
        self._init_data()

        # 延迟添加贡献者卡片
        self._init_timer = QTimer(self)
        self._init_timer.setSingleShot(True)
        self._init_timer.timeout.connect(self.create_contributor_cards)
        self._init_timer.start(APP_INIT_DELAY)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_update_layout)

    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 滚动区域
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.main_layout.addWidget(self.scroll_area)

        # 流式布局容器
        self.flow_container = QWidget()
        self.scroll_area.setWidget(self.flow_container)
        self.flow_layout = CenterFlowLayout(self.flow_container)
        self.flow_layout.setHorizontalSpacing(CONTRIBUTOR_CARD_SPACING)
        self.flow_layout.setVerticalSpacing(CONTRIBUTOR_CARD_SPACING)
        self.flow_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.flow_layout.setContentsMargins(10, 10, 10, 10)
        self.flow_container.setLayout(self.flow_layout)

        # 初始化卡片列表
        self.cards = []

    def _init_data(self):
        """初始化贡献者数据"""
        # 贡献者数据
        contributors = [
            {
                "name": "lzy98276",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_1"
                ),
                "github": "https://github.com/lzy98276",
                "avatar": str(get_data_path("assets/contribution", "contributor1.png")),
            },
            {
                "name": "chenjintang-shrimp",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_2"
                ),
                "github": "https://github.com/chenjintang-shrimp",
                "avatar": str(get_data_path("assets/contribution", "contributor2.png")),
            },
            {
                "name": "yuanbenxin",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_3"
                ),
                "github": "https://github.com/yuanbenxin",
                "avatar": str(get_data_path("assets/contribution", "contributor3.png")),
            },
            {
                "name": "LeafS",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_4"
                ),
                "github": "https://github.com/LeafS825",
                "avatar": str(get_data_path("assets/contribution", "contributor4.png")),
            },
            {
                "name": "QiKeZhiCao",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_5"
                ),
                "github": "https://github.com/QiKeZhiCao",
                "avatar": str(get_data_path("assets/contribution", "contributor5.png")),
            },
            {
                "name": "Fox-block-offcial",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_6"
                ),
                "github": "https://github.com/Fox-block-offcial",
                "avatar": str(get_data_path("assets/contribution", "contributor6.png")),
            },
            {
                "name": "Jursin",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_7"
                ),
                "github": "https://github.com/jursin",
                "avatar": str(get_data_path("assets/contribution", "contributor7.png")),
            },
            {
                "name": "lrs2187",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_10"
                ),
                "github": "https://github.com/lrsgzs",
                "avatar": str(
                    get_data_path("assets/contribution", "contributor10.png")
                ),
            },
            {
                "name": "WSXYT",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_11"
                ),
                "github": "https://github.com/WSXYT",
                "avatar": str(
                    get_data_path("assets/contribution", "contributor11.png")
                ),
            },
            {
                "name": "LHGS-github",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_8"
                ),
                "github": "https://github.com/LHGS-github",
                "avatar": str(get_data_path("assets/contribution", "contributor8.png")),
            },
            {
                "name": "real01bit",
                "role": get_any_position_value_async(
                    "about", "contributor", "contributor_role_9"
                ),
                "github": "https://github.com/real01bit",
                "avatar": str(get_data_path("assets/contribution", "contributor9.png")),
            },
        ]

        # 标准化职责文本长度
        self._standardize_role_text(contributors)
        self.contributors = contributors

    def _standardize_role_text(self, contributors):
        """标准化职责文本长度，使所有职责文本行数一致"""
        # 计算所有职责文本的行数
        fm = QFontMetrics(self.font())
        max_lines = 0
        role_lines = []

        # 找出最长的职责文本有多少行
        for contributor in contributors:
            role_text = contributor["role"] or ""  # 确保role_text不为None
            contributor["role"] = role_text

            # 计算文本在MAX_ROLE_WIDTH宽度下的行数
            text_rect = fm.boundingRect(
                QRect(0, 0, CONTRIBUTOR_MAX_ROLE_WIDTH, 0),
                Qt.TextFlag.TextWordWrap,
                role_text,
            )
            line_count = text_rect.height() // fm.lineSpacing()
            role_lines.append(line_count)
            max_lines = max(max_lines, line_count)

        # 为每个职责文本添加换行符，确保行数相同
        for i, contributor in enumerate(contributors):
            current_lines = role_lines[i]
            if current_lines < max_lines:
                contributor["role"] += "\n" * (max_lines - current_lines)

    def create_contributor_cards(self):
        """创建贡献者卡片"""
        if self._closing:
            return
        if not hasattr(self, "flow_layout") or self.flow_layout is None:
            return

        # 添加贡献者卡片
        for contributor in self.contributors:
            card = self.addContributorCard(contributor)
            if card is not None:  # 只添加有效的卡片
                self.cards.append(card)

        # 延迟更新布局
        self.update_layout()

    def update_layout(self):
        """更新布局 - 根据窗口大小动态调整卡片排列"""
        if self.flow_layout is None:
            return
        if hasattr(self, "scroll_area") and self.scroll_area is not None:
            try:
                self.flow_container.setMinimumWidth(self.scroll_area.viewport().width())
            except Exception:
                pass
        self.flow_layout.invalidate()

    def addContributorCard(self, contributor):
        """添加单个贡献者卡片"""
        if not hasattr(self, "flow_layout") or self.flow_layout is None:
            return None

        try:
            card = ElevatedCardWidget()
            card.setObjectName("contributorCard")
            card.setMinimumWidth(CONTRIBUTOR_CARD_MIN_WIDTH)
            card.setMaximumWidth(CONTRIBUTOR_CARD_MIN_WIDTH * 1.5)
            cardLayout = QVBoxLayout(card)
            cardLayout.setContentsMargins(
                CONTRIBUTOR_CARD_MARGIN,
                CONTRIBUTOR_CARD_MARGIN,
                CONTRIBUTOR_CARD_MARGIN,
                CONTRIBUTOR_CARD_MARGIN,
            )
            cardLayout.setSpacing(10)

            # 头像
            avatar = AvatarWidget(contributor["avatar"])
            avatar.setRadius(CONTRIBUTOR_AVATAR_RADIUS)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cardLayout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)

            # 昵称作为GitHub链接
            name = HyperlinkButton(contributor["github"], contributor["name"], None)
            name.setStyleSheet(
                "text-decoration: underline; color: #0066cc; background: transparent; border: none; padding: 0;"
            )
            cardLayout.addWidget(name, 0, Qt.AlignmentFlag.AlignCenter)

            # 职责
            role_text = contributor["role"] or ""
            role = BodyLabel(role_text)
            role.setAlignment(Qt.AlignmentFlag.AlignCenter)
            role.setWordWrap(True)
            role.setMaximumWidth(CONTRIBUTOR_MAX_ROLE_WIDTH)
            cardLayout.addWidget(role, 0, Qt.AlignmentFlag.AlignCenter)

            self.flow_layout.addWidget(card)
            return card
        except RuntimeError as e:
            logger.exception(f"创建贡献者卡片时出错: {e}")
            return None

    def resizeEvent(self, event):
        """窗口大小变化事件"""
        # 使用QTimer延迟布局更新，避免递归调用
        if self._resize_timer.isActive():
            self._resize_timer.stop()
        self._resize_timer.start(50)
        super().resizeEvent(event)

    def _delayed_update_layout(self):
        """延迟更新布局"""
        if self._closing:
            return
        try:
            if hasattr(self, "flow_layout") and self.flow_layout is not None:
                if self.isVisible():
                    self.update_layout()
        except RuntimeError as e:
            logger.exception(f"延迟布局更新错误: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self._closing = True
        try:
            if self._init_timer.isActive():
                self._init_timer.stop()
        except Exception:
            pass
        try:
            if self._resize_timer.isActive():
                self._resize_timer.stop()
        except Exception:
            pass

        super().closeEvent(event)
