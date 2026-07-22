# ==================================================
# 导入库
# ==================================================
from app.common.data.list import get_student_list, get_pool_list
from app.common.history.file_utils import load_history_data


# ==================================================
# 历史记录统计函数
# ==================================================
def get_name_history(history_type: str, class_name: str) -> int:
    """获取指定班级的名称历史记录数量

    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        class_name: 班级名称/奖池名称

    Returns:
        int: 名称历史记录数量
    """
    if history_type == "roll_call":
        student_list = get_student_list(class_name)
        return len(student_list) if student_list else 0
    elif history_type == "lottery":
        student_list = get_pool_list(class_name)
        return len(student_list) if student_list else 0
    else:
        return 0


def get_draw_sessions_history(history_type: str, class_name: str) -> int:
    """获取指定班级的抽取会话历史记录数量

    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        class_name: 班级名称

    Returns:
        int: 抽取会话历史记录数量
    """
    history_data = load_history_data(history_type, class_name)
    session_count = 0
    if history_type == "roll_call":
        key = "students"
    elif history_type == "lottery":
        key = "lotterys"
    else:
        return 0
    students_dict = history_data.get(key, {})
    if isinstance(students_dict, dict):
        for student_name, student_info in students_dict.items():
            session_list = student_info.get("history", [])
            if isinstance(session_list, list):
                session_count += len(session_list)
    return session_count


def get_individual_statistics(
    history_type: str, class_name: str, students_name: str
) -> int:
    """获取指定班级的个人统计记录数量

    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        class_name: 班级名称/奖池名称
        students_name: 学生姓名/奖品名称

    Returns:
        int: 个人统计记录数量
    """
    history_data = load_history_data(history_type, class_name)
    if history_type == "roll_call":
        key = "students"
    elif history_type == "lottery":
        key = "lotterys"
    else:
        return 0
    students_dict = history_data.get(key, {})
    if not isinstance(students_dict, dict):
        return 0
    student_info = students_dict.get(students_name)
    if not student_info:
        return 0
    student_history = student_info.get("history", [])
    if not isinstance(student_history, list):
        return 0
    return len(student_history)
