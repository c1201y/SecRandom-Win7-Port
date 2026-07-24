# ==================================================
# 导入库
# ==================================================
from datetime import datetime
from typing import Dict, List, Any

from loguru import logger

from app.common.extraction.extract import _get_current_class_info
from app.common.history.file_utils import load_history_data, save_history_data


# ==================================================
# 保存抽奖历史函数
# ==================================================
def save_lottery_history(
    pool_name: str,
    selected_students: List[Dict[str, Any]],
    group_filter: str,
    gender_filter: str,
) -> bool:
    """保存抽奖历史（基于奖池名称）

    Args:
        pool_name: 奖池名称
        selected_students: 学生字典列表（包含 name、id、exist 等）
        group_filter: 抽取时的小组过滤器
        gender_filter: 抽取时的性别过滤器

    Returns:
        bool: 保存是否成功
    """
    try:
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取当前课程信息
        current_class_info = _get_current_class_info()

        history_data = load_history_data("lottery", pool_name)
        lotterys = history_data.get("lotterys", {})
        group_stats = history_data.get("group_stats", {})
        gender_stats = history_data.get("gender_stats", {})
        total_stats = history_data.get("total_stats", 0)

        for student in selected_students or []:
            name = student.get("name", "")
            if not name:
                continue
            entry = lotterys.get(name)
            if not isinstance(entry, dict):
                entry = {
                    "total_count": 0,
                    "rounds_missed": 0,
                    "last_drawn_time": "",
                    "history": [],
                }
            entry["total_count"] = int(entry.get("total_count", 0)) + 1
            entry["last_drawn_time"] = current_time
            hist = entry.get("history", [])
            if not isinstance(hist, list):
                hist = []
            hist.append(
                {
                    "draw_time": current_time,
                    "draw_lottery_numbers": len(selected_students),
                    "draw_group": group_filter,
                    "draw_gender": gender_filter,
                }
            )
            # 如果能获取到课程信息，则添加到历史记录中
            if current_class_info:
                hist[-1]["class_name"] = current_class_info.get("name", "")
            entry["history"] = hist
            lotterys[name] = entry

        # 更新统计
        if group_filter:
            group_stats[group_filter] = int(group_stats.get(group_filter, 0)) + len(
                selected_students or []
            )
        if gender_filter:
            gender_stats[gender_filter] = int(gender_stats.get(gender_filter, 0)) + len(
                selected_students or []
            )
        total_stats = int(total_stats) + len(selected_students or [])

        history_data["lotterys"] = lotterys
        history_data["group_stats"] = group_stats
        history_data["gender_stats"] = gender_stats
        history_data["total_stats"] = total_stats

        return save_history_data("lottery", pool_name, history_data)
    except Exception as e:
        logger.exception(f"保存抽奖历史失败: {e}")
        return False
