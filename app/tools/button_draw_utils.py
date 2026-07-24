"""按钮绘制工具函数"""

from PySide2.QtGui import QPainter, QColor
from qfluentwidgets.common.color import autoFallbackThemeColor
from qfluentwidgets.common.config import isDarkTheme

from app.tools.variable import (
    BUTTON_BACKGROUND_ALPHA_DARK,
    BUTTON_BACKGROUND_ALPHA_LIGHT,
    BUTTON_ENTER_ALPHA_DARK,
    BUTTON_ENTER_ALPHA_LIGHT,
    BUTTON_PRESSED_ALPHA_DARK,
    BUTTON_PRESSED_ALPHA_LIGHT,
    BUTTON_INDICATOR_HEIGHT_NORMAL,
    BUTTON_INDICATOR_HEIGHT_PRESSED,
    BUTTON_INDICATOR_WIDTH,
    BUTTON_INDICATOR_RADIUS,
    BUTTON_RECT_RADIUS,
    BUTTON_INDICATOR_Y_OFFSET_PRESSED,
)


def centered_draw_background(button, painter: QPainter, button_size: int):
    """绘制按钮背景，使选中指示条（小蓝条）垂直居中

    Args:
        button: 按钮对象
        painter: 绘制器
        button_size: 按钮大小
    """
    if button.isSelected:
        _draw_selected_background(button, painter)
        _draw_indicator(button, painter, button_size)
    elif button.isPressed or button.isEnter:
        _draw_hover_background(button, painter)


def _draw_selected_background(button, painter: QPainter):
    """绘制选中状态的背景

    Args:
        button: 按钮对象
        painter: 绘制器
    """
    alpha = (
        BUTTON_BACKGROUND_ALPHA_DARK if isDarkTheme() else BUTTON_BACKGROUND_ALPHA_LIGHT
    )
    painter.setBrush(QColor(255, 255, 255, alpha))
    painter.drawRoundedRect(button.rect(), BUTTON_RECT_RADIUS, BUTTON_RECT_RADIUS)


def _draw_indicator(button, painter: QPainter, button_size: int):
    """绘制选中指示条（小蓝条），垂直居中

    Args:
        button: 按钮对象
        painter: 绘制器
        button_size: 按钮大小
    """
    painter.setBrush(
        autoFallbackThemeColor(button.lightSelectedColor, button.darkSelectedColor)
    )
    indicator_height = (
        BUTTON_INDICATOR_HEIGHT_PRESSED
        if button.isPressed
        else BUTTON_INDICATOR_HEIGHT_NORMAL
    )
    indicator_y = (button_size - indicator_height) // 2
    if button.isPressed:
        indicator_y += BUTTON_INDICATOR_Y_OFFSET_PRESSED
    painter.drawRoundedRect(
        0,
        indicator_y,
        BUTTON_INDICATOR_WIDTH,
        indicator_height,
        BUTTON_INDICATOR_RADIUS,
        BUTTON_INDICATOR_RADIUS,
    )


def _draw_hover_background(button, painter: QPainter):
    """绘制鼠标悬停或按下状态的背景

    Args:
        button: 按钮对象
        painter: 绘制器
    """
    c = 255 if isDarkTheme() else 0
    alpha = (
        (BUTTON_PRESSED_ALPHA_DARK if button.isPressed else BUTTON_ENTER_ALPHA_DARK)
        if isDarkTheme()
        else (
            BUTTON_PRESSED_ALPHA_LIGHT if button.isPressed else BUTTON_ENTER_ALPHA_LIGHT
        )
    )
    painter.setBrush(QColor(c, c, c, alpha))
    painter.drawRoundedRect(button.rect(), BUTTON_RECT_RADIUS, BUTTON_RECT_RADIUS)
