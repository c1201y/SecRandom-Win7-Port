# ==================================================
# 导入库
# ==================================================
from typing import Union

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem

from app.common.data.list import get_student_list, get_pool_list


# ==================================================
# 辅助函数
# ==================================================
def get_all_names(history_type: str, list_name: str) -> list:
    """获取历史记录中所有名称

    Args:
        history_type: 历史记录类型
        list_name: 列表名称

    Returns:
        list: 所有名称列表
    """
    try:
        if history_type == "roll_call":
            list_name_data = get_student_list(list_name)
            return [
                item["name"]
                for item in list_name_data
                if "name" in item and item["name"]
            ]
        else:
            list_name_data = get_pool_list(list_name)
            return [
                item["name"]
                for item in list_name_data
                if "name" in item and item["name"]
            ]
    except Exception as e:
        from loguru import logger

        logger.exception(f"获取历史记录中所有名称失败: {e}")
        return []


def format_table_item(
    value: Union[str, int, float], is_percentage: bool = False
) -> str:
    """格式化表格项显示值

    Args:
        value: 要格式化的值
        is_percentage: 是否为百分比值

    Returns:
        str: 格式化后的字符串
    """
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value:.2%}"
        else:
            return f"{value:.2f}"
    return str(value)


def create_table_item(
    value: Union[str, int, float],
    is_centered: bool = True,
    is_percentage: bool = False,
) -> "QTableWidgetItem":
    """创建表格项

    Args:
        value: 要显示的值
        is_centered: 是否居中
        is_percentage: 是否为百分比值

    Returns:
        QTableWidgetItem: 表格项对象
    """
    display_value = format_table_item(value, is_percentage)
    item = QTableWidgetItem(display_value)

    if is_centered:
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item
