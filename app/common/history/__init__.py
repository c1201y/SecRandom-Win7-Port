# ==================================================
# 历史记录模块
# ==================================================
# 该模块提供历史记录的保存、加载、统计和权重计算功能

# 文件工具
from app.common.history.file_utils import (
    get_history_file_path,
    load_history_data,
    save_history_data,
    get_all_history_names,
)

# 统计函数
from app.common.history.statistics import (
    get_name_history,
    get_draw_sessions_history,
    get_individual_statistics,
)

# 抽奖历史
from app.common.history.lottery_history import save_lottery_history

# 点名历史
from app.common.history.roll_call_history import save_roll_call_history

# 权重工具
from app.common.history.weight_utils import (
    format_weight_for_display,
    calculate_weight,
)

# 辅助函数
from app.common.history.utils import (
    get_all_names,
    format_table_item,
    create_table_item,
)

# 历史记录读取工具
from app.common.history.history_reader import (
    # 点名历史读取
    get_roll_call_student_list,
    get_roll_call_history_data,
    filter_roll_call_history_by_subject,
    get_roll_call_student_total_count,
    get_roll_call_students_data,
    get_roll_call_session_data,
    get_roll_call_student_stats_data,
    check_class_has_gender_or_group,
    # 抽奖历史读取
    get_lottery_pool_list,
    get_lottery_history_data,
    get_lottery_prizes_data,
    get_lottery_session_data,
    get_lottery_prize_stats_data,
)

__all__ = [
    # 文件工具
    "get_history_file_path",
    "load_history_data",
    "save_history_data",
    "get_all_history_names",
    # 统计函数
    "get_name_history",
    "get_draw_sessions_history",
    "get_individual_statistics",
    # 抽奖历史
    "save_lottery_history",
    # 点名历史
    "save_roll_call_history",
    # 权重工具
    "format_weight_for_display",
    "calculate_weight",
    # 辅助函数
    "get_all_names",
    "format_table_item",
    "create_table_item",
    # 历史记录读取工具
    "get_roll_call_student_list",
    "get_roll_call_history_data",
    "filter_roll_call_history_by_subject",
    "get_roll_call_student_total_count",
    "get_roll_call_students_data",
    "get_roll_call_session_data",
    "get_roll_call_student_stats_data",
    "check_class_has_gender_or_group",
    "get_lottery_pool_list",
    "get_lottery_history_data",
    "get_lottery_prizes_data",
    "get_lottery_session_data",
    "get_lottery_prize_stats_data",
]
