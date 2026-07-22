# ==================================================
# 导入库
# ==================================================
import json
from typing import Dict, List, Any, Optional, Tuple

from loguru import logger

from app.tools.path_utils import get_data_path, open_file, file_exists
from app.common.data.list import get_gender_list, get_group_list


# ==================================================
# 点名历史记录读取工具
# ==================================================
def get_roll_call_student_list(
    class_name: str,
) -> List[Tuple[str, str, str, str]]:
    """获取班级学生列表

    Args:
        class_name: 班级名称

    Returns:
        List[Tuple[str, str, str, str]]: 学生列表，每个元素为 (id, name, gender, group)
    """
    try:
        student_file = get_data_path("list/roll_call_list", f"{class_name}.json")
        with open_file(student_file, "r", encoding="utf-8") as f:
            class_data = json.load(f)

        cleaned_students = []
        for name, info in class_data.items():
            if isinstance(info, dict) and info.get("exist", True):
                cleaned_students.append(
                    (
                        info.get("id", ""),
                        name,
                        info.get("gender", ""),
                        info.get("group", ""),
                    )
                )
        return cleaned_students
    except Exception as e:
        logger.error(f"获取班级学生列表失败: {e}")
        return []


def get_roll_call_history_data(
    class_name: str,
) -> Dict[str, Any]:
    """获取点名历史记录数据

    Args:
        class_name: 班级名称

    Returns:
        Dict[str, Any]: 历史记录数据
    """
    try:
        history_file = get_data_path("history/roll_call_history", f"{class_name}.json")
        if not file_exists(history_file):
            return {}

        with open_file(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"获取点名历史记录数据失败: {e}")
        return {}


def filter_roll_call_history_by_subject(
    history_data: Dict[str, Any], subject_name: str
) -> Dict[str, Any]:
    """按课程过滤点名历史记录

    Args:
        history_data: 原始历史记录数据
        subject_name: 课程名称

    Returns:
        Dict[str, Any]: 过滤后的历史记录数据
    """
    if not subject_name:
        return history_data

    filtered_history_data = {"students": {}}
    for student_name, student_info in history_data.get("students", {}).items():
        filtered_history = []
        for record in student_info.get("history", []):
            if record.get("class_name", "") == subject_name:
                filtered_history.append(record)
        if filtered_history:
            filtered_history_data["students"][student_name] = {
                **student_info,
                "history": filtered_history,
                "total_count": len(filtered_history),
            }

    # 添加科目统计信息
    subject_stats = history_data.get("subject_stats", {})
    if subject_name in subject_stats:
        subject_data = subject_stats[subject_name]
        if isinstance(subject_data, dict):
            filtered_history_data["group_stats"] = subject_data.get("group_stats", {})
            filtered_history_data["gender_stats"] = subject_data.get("gender_stats", {})
            filtered_history_data["total_rounds"] = subject_data.get("total_rounds", 0)
            filtered_history_data["total_stats"] = subject_data.get("total_stats", 0)

    return filtered_history_data


def get_roll_call_student_total_count(
    history_data: Dict[str, Any],
    student_name: str,
    subject_name: Optional[str] = None,
) -> int:
    """获取学生总次数

    Args:
        history_data: 历史记录数据
        student_name: 学生姓名
        subject_name: 课程名称，如果为None则统计所有记录

    Returns:
        int: 总次数
    """
    if subject_name:
        # 如果选择了特定课程，从 subject_stats 中获取统计信息
        student_info = history_data.get("students", {}).get(student_name, {})
        subject_stats = student_info.get("subject_stats", {})
        if subject_name in subject_stats:
            return subject_stats[subject_name].get("total_count", 0)
        return 0
    else:
        # 统计所有历史记录
        return int(
            history_data.get("students", {}).get(student_name, {}).get("total_count", 0)
        )


def get_roll_call_students_data(
    cleaned_students: List[Tuple[str, str, str, str]],
    history_data: Dict[str, Any],
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """获取学生数据列表

    Args:
        cleaned_students: 清理后的学生列表
        history_data: 历史记录数据
        subject_name: 课程名称，如果为None则统计所有记录

    Returns:
        List[Dict[str, Any]]: 学生数据列表
    """
    max_id_length = (
        max(len(str(student[0])) for student in cleaned_students)
        if cleaned_students
        else 0
    )

    students_data = []
    for student_id, name, gender, group in cleaned_students:
        total_count = get_roll_call_student_total_count(
            history_data, name, subject_name
        )
        students_data.append(
            {
                "id": str(student_id).zfill(max_id_length),
                "name": name,
                "gender": gender,
                "group": group,
                "total_count": total_count,
                "total_count_str": str(total_count),
            }
        )

    max_total_count_length = (
        max(len(str(student.get("total_count", 0))) for student in students_data)
        if students_data
        else 0
    )

    for student in students_data:
        student["total_count_str"] = str(student["total_count"]).zfill(
            max_total_count_length
        )

    return students_data


def get_roll_call_session_data(
    cleaned_students: List[Tuple[str, str, str, str]],
    history_data: Dict[str, Any],
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """获取点名会话数据列表

    Args:
        cleaned_students: 清理后的学生列表
        history_data: 历史记录数据
        subject_name: 课程名称，如果为None则显示所有记录

    Returns:
        List[Dict[str, Any]]: 会话数据列表
    """
    max_id_length = (
        max(len(str(student[0])) for student in cleaned_students)
        if cleaned_students
        else 0
    )

    students_data = []
    for student_id, name, gender, group in cleaned_students:
        time_records = (
            history_data.get("students", {}).get(name, {}).get("history", [{}])
        )
        for record in time_records:
            draw_time = record.get("draw_time", "")
            if draw_time:
                # 如果选择了特定课程，只显示该课程的记录
                if subject_name:
                    if record.get("class_name", "") == subject_name:
                        students_data.append(
                            {
                                "draw_time": draw_time,
                                "id": str(student_id).zfill(max_id_length),
                                "name": name,
                                "gender": gender,
                                "group": group,
                                "class_name": record.get("class_name", ""),
                                "weight": record.get("weight", ""),
                            }
                        )
                else:
                    students_data.append(
                        {
                            "draw_time": draw_time,
                            "id": str(student_id).zfill(max_id_length),
                            "name": name,
                            "gender": gender,
                            "group": group,
                            "class_name": record.get("class_name", ""),
                            "weight": record.get("weight", ""),
                        }
                    )
    return students_data


def get_roll_call_student_stats_data(
    cleaned_students: List[Tuple[str, str, str, str]],
    history_data: Dict[str, Any],
    student_name: str,
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """获取点名学生统计数据列表

    Args:
        cleaned_students: 清理后的学生列表
        history_data: 历史记录数据
        student_name: 学生姓名
        subject_name: 课程名称，如果为None则显示所有记录

    Returns:
        List[Dict[str, Any]]: 统计数据列表
    """
    max_id_length = (
        max(len(str(student[0])) for student in cleaned_students)
        if cleaned_students
        else 0
    )

    students_data = []
    for student_id, name, gender, group in cleaned_students:
        if name == student_name:
            time_records = (
                history_data.get("students", {}).get(name, {}).get("history", [{}])
            )
            for record in time_records:
                draw_time = record.get("draw_time", "")
                if draw_time:
                    # 如果选择了特定课程，只显示该课程的记录
                    if subject_name:
                        if record.get("class_name", "") == subject_name:
                            students_data.append(
                                {
                                    "draw_time": draw_time,
                                    "draw_method": str(record.get("draw_method", "")),
                                    "draw_people_numbers": str(
                                        record.get("draw_people_numbers", 0)
                                    ),
                                    "draw_gender": str(record.get("draw_gender", "")),
                                    "draw_group": str(record.get("draw_group", "")),
                                    "class_name": record.get("class_name", ""),
                                    "weight": record.get("weight", ""),
                                }
                            )
                    else:
                        students_data.append(
                            {
                                "draw_time": draw_time,
                                "draw_method": str(record.get("draw_method", "")),
                                "draw_people_numbers": str(
                                    record.get("draw_people_numbers", 0)
                                ),
                                "draw_gender": str(record.get("draw_gender", "")),
                                "draw_group": str(record.get("draw_group", "")),
                                "class_name": record.get("class_name", ""),
                                "weight": record.get("weight", ""),
                            }
                        )
            break
    return students_data


def check_class_has_gender_or_group(
    class_name: str,
) -> Tuple[bool, bool]:
    """检查班级是否设置了性别和小组

    Args:
        class_name: 班级名称

    Returns:
        Tuple[bool, bool]: (has_gender, has_group)
    """
    gender_list = get_gender_list(class_name)
    group_list = get_group_list(class_name)
    has_gender = bool(gender_list) and gender_list != [""]
    has_group = bool(group_list) and group_list != [""]
    return has_gender, has_group


# ==================================================
# 抽奖历史记录读取工具
# ==================================================


def get_lottery_pool_list(
    pool_name: str,
) -> List[Tuple[str, str, str]]:
    """获取奖池奖品列表

    Args:
        pool_name: 奖池名称

    Returns:
        List[Tuple[str, str, str]]: 奖品列表，每个元素为 (id, name, weight)
    """
    try:
        lottery_file = get_data_path("list/lottery_list", f"{pool_name}.json")
        with open_file(lottery_file, "r", encoding="utf-8") as f:
            pool_data = json.load(f)

        cleaned_lotterys = []
        for name, info in pool_data.items():
            if isinstance(info, dict) and info.get("exist", True):
                cleaned_lotterys.append(
                    (
                        info.get("id", ""),
                        name,
                        info.get("weight", ""),
                    )
                )
        return cleaned_lotterys
    except Exception as e:
        logger.error(f"获取奖池奖品列表失败: {e}")
        return []


def get_lottery_history_data(
    pool_name: str,
) -> Dict[str, Any]:
    """获取抽奖历史记录数据

    Args:
        pool_name: 奖池名称

    Returns:
        Dict[str, Any]: 历史记录数据
    """
    try:
        history_file = get_data_path("history/lottery_history", f"{pool_name}.json")
        if not file_exists(history_file):
            return {}

        with open_file(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"获取抽奖历史记录数据失败: {e}")
        return {}


def get_lottery_prizes_data(
    cleaned_lotterys: List[Tuple[str, str, str]],
    history_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """获取奖品数据列表

    Args:
        cleaned_lotterys: 清理后的奖品列表
        history_data: 历史记录数据

    Returns:
        List[Dict[str, Any]]: 奖品数据列表
    """
    max_id_length = (
        max(len(str(lottery[0])) for lottery in cleaned_lotterys)
        if cleaned_lotterys
        else 0
    )
    max_total_count_length = (
        max(
            len(
                str(
                    history_data.get("lotterys", {}).get(name, {}).get("total_count", 0)
                )
            )
            for _, name, _ in cleaned_lotterys
        )
        if cleaned_lotterys
        else 0
    )

    lotterys_data = []
    for lottery_id, name, weight in cleaned_lotterys:
        total_count = int(
            history_data.get("lotterys", {}).get(name, {}).get("total_count", 0)
        )
        lotterys_data.append(
            {
                "id": str(lottery_id).zfill(max_id_length),
                "name": name,
                "weight": weight,
                "total_count": total_count,
                "total_count_str": str(total_count).zfill(max_total_count_length),
            }
        )
    return lotterys_data


def get_lottery_session_data(
    cleaned_lotterys: List[Tuple[str, str, str]],
    history_data: Dict[str, Any],
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """获取抽奖会话数据列表

    Args:
        cleaned_lotterys: 清理后的奖品列表
        history_data: 历史记录数据
        subject_name: 课程名称，如果为None则显示所有记录

    Returns:
        List[Dict[str, Any]]: 会话数据列表
    """
    max_id_length = (
        max(len(str(lottery[0])) for lottery in cleaned_lotterys)
        if cleaned_lotterys
        else 0
    )

    # 创建奖品名称到权重的映射
    lottery_weight_map = {name: weight for _, name, weight in cleaned_lotterys}

    lotterys_data = []
    for lottery_id, name, weight in cleaned_lotterys:
        time_records = (
            history_data.get("lotterys", {}).get(name, {}).get("history", [{}])
        )
        for record in time_records:
            draw_time = record.get("draw_time", "")
            if draw_time:
                # 如果选择了特定课程，只显示该课程的记录
                if subject_name:
                    if record.get("class_name", "") == subject_name:
                        lotterys_data.append(
                            {
                                "draw_time": draw_time,
                                "id": str(lottery_id).zfill(max_id_length),
                                "name": name,
                                "class_name": record.get("class_name", ""),
                                "weight": lottery_weight_map.get(name, ""),
                            }
                        )
                else:
                    lotterys_data.append(
                        {
                            "draw_time": draw_time,
                            "id": str(lottery_id).zfill(max_id_length),
                            "name": name,
                            "class_name": record.get("class_name", ""),
                            "weight": lottery_weight_map.get(name, ""),
                        }
                    )
    return lotterys_data


def get_lottery_prize_stats_data(
    cleaned_lotterys: List[Tuple[str, str, str]],
    history_data: Dict[str, Any],
    lottery_name: str,
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """获取抽奖奖品统计数据列表

    Args:
        cleaned_lotterys: 清理后的奖品列表
        history_data: 历史记录数据
        lottery_name: 奖品名称
        subject_name: 课程名称，如果为None则显示所有记录

    Returns:
        List[Dict[str, Any]]: 统计数据列表
    """
    max_id_length = (
        max(len(str(lottery[0])) for lottery in cleaned_lotterys)
        if cleaned_lotterys
        else 0
    )

    # 创建奖品名称到权重的映射
    lottery_weight_map = {name: weight for _, name, weight in cleaned_lotterys}

    lotterys_data = []
    for lottery_id, name, weight in cleaned_lotterys:
        if name == lottery_name:
            time_records = (
                history_data.get("lotterys", {}).get(name, {}).get("history", [{}])
            )
            for record in time_records:
                draw_time = record.get("draw_time", "")
                if draw_time:
                    # 如果选择了特定课程，只显示该课程的记录
                    if subject_name:
                        if record.get("class_name", "") == subject_name:
                            lotterys_data.append(
                                {
                                    "draw_time": draw_time,
                                    "draw_lottery_numbers": str(
                                        record.get("draw_lottery_numbers", 0)
                                    ),
                                    "draw_gender": str(record.get("draw_gender", "")),
                                    "draw_group": str(record.get("draw_group", "")),
                                    "class_name": record.get("class_name", ""),
                                    "weight": lottery_weight_map.get(name, ""),
                                }
                            )
                    else:
                        lotterys_data.append(
                            {
                                "draw_time": draw_time,
                                "draw_lottery_numbers": str(
                                    record.get("draw_lottery_numbers", 0)
                                ),
                                "draw_gender": str(record.get("draw_gender", "")),
                                "draw_group": str(record.get("draw_group", "")),
                                "class_name": record.get("class_name", ""),
                                "weight": lottery_weight_map.get(name, ""),
                            }
                        )
            break
    return lotterys_data
