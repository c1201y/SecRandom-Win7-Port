# ==================================================
# 内幕工具类
# ==================================================
import time
from loguru import logger

from app.common.safety.secure_store import read_behind_scenes_settings


class BehindScenesUtils:
    """内幕工具类，提供内幕设置相关功能"""

    _settings_cache = None
    _cache_timestamp = 0
    _cache_ttl = 5.0

    @staticmethod
    def get_behind_scenes_settings(use_cache=True):
        """获取内幕设置数据

        Args:
            use_cache: 是否使用缓存（默认为True）

        Returns:
            dict: 内幕设置数据字典
        """
        current_time = time.time()

        if use_cache and BehindScenesUtils._settings_cache is not None:
            if (
                current_time - BehindScenesUtils._cache_timestamp
                < BehindScenesUtils._cache_ttl
            ):
                return BehindScenesUtils._settings_cache

        try:
            settings = read_behind_scenes_settings()
            BehindScenesUtils._settings_cache = settings
            BehindScenesUtils._cache_timestamp = current_time
            return settings
        except Exception as e:
            logger.error(f"读取内幕设置失败: {e}")
            return {}

    @staticmethod
    def clear_cache():
        """清除缓存"""
        BehindScenesUtils._settings_cache = None
        BehindScenesUtils._cache_timestamp = 0

    @staticmethod
    def get_probability_settings(name, mode, pool_name=None):
        """获取指定人员的概率设置

        Args:
            name: 人员名称
            mode: 模式（0=点名, 1=抽奖）
            pool_name: 奖池名称（仅在抽奖模式下使用）

        Returns:
            dict: 包含 enabled 和 probability 的字典
        """
        try:
            settings = BehindScenesUtils.get_behind_scenes_settings()
            if (
                settings
                and isinstance(settings, dict)
                and not settings.get("enabled_global", True)
            ):
                return {"enabled": False, "probability": 1.0}
            if name in settings:
                if mode == 0:
                    # 点名模式
                    return settings[name].get(
                        "roll_call", {"enabled": False, "probability": 1.0}
                    )
                else:
                    # 抽奖模式
                    lottery_settings = settings[name].get("lottery", {})
                    if pool_name and pool_name in lottery_settings:
                        # 按奖池获取设置
                        return lottery_settings[pool_name]
                    else:
                        # 默认设置
                        return {"enabled": False, "probability": 1.0}
            return {"enabled": False, "probability": 1.0}
        except Exception as e:
            logger.error(f"获取概率设置失败: {e}")
            return {"enabled": False, "probability": 1.0}

    @staticmethod
    def apply_probability_weights(
        students_dict_list, mode, class_name, pool_name=None, prize_list=None
    ):
        """应用内幕设置到学生列表

        Args:
            students_dict_list: 学生字典列表
            mode: 模式（0=点名, 1=抽奖）
            class_name: 班级名称（用于日志）
            pool_name: 奖池名称（仅在抽奖模式下使用）
            prize_list: 奖品列表（用于提高指定该奖品的学生的权重）

        Returns:
            tuple: (过滤后的学生列表, 权重列表)
        """
        try:
            settings = BehindScenesUtils.get_behind_scenes_settings()
            if (
                settings
                and isinstance(settings, dict)
                and not settings.get("enabled_global", True)
            ):
                return students_dict_list, [1.0] * len(students_dict_list)

            # 构建抽中奖品集合（用于快速查找）
            drawn_prizes = set(prize_list) if prize_list else set()

            # 如果有奖品-学生关联，记录日志
            if prize_list and pool_name:
                prize_to_students = {}
                for prize_name in prize_list:
                    for student_name, student_settings in settings.items():
                        lottery_settings = student_settings.get("lottery", {})
                        if pool_name in lottery_settings:
                            pool_setting = lottery_settings[pool_name]
                            assigned_prize = pool_setting.get("prize", "")
                            if assigned_prize == prize_name:
                                if prize_name not in prize_to_students:
                                    prize_to_students[prize_name] = []
                                prize_to_students[prize_name].append(student_name)

            filtered_students = []
            weights = []

            for student in students_dict_list:
                name = student.get("name", "")

                if name in settings:
                    if mode == 0:
                        # 点名模式
                        prob_settings = settings[name].get("roll_call", {})
                        enabled = prob_settings.get("enabled", False)
                        probability = prob_settings.get("probability", 1.0)
                    else:
                        # 抽奖模式
                        lottery_settings = settings[name].get("lottery", {})
                        if pool_name in lottery_settings:
                            prob_settings = lottery_settings[pool_name]
                            enabled = prob_settings.get("enabled", False)
                            probability = prob_settings.get("probability", 1.0)

                            # 检查该学生指定的奖品是否在抽中的奖品列表中
                            assigned_prize = prob_settings.get("prize", "")
                            if assigned_prize and assigned_prize in drawn_prizes:
                                # 指定的奖品被抽中，提高该学生的权重
                                if probability < 1000:
                                    # 如果不是必中，则提高权重
                                    probability = probability * 10
                            else:
                                # 指定的奖品未被抽中，使用正常权重
                                probability = 1.0
                        else:
                            # 未设置该奖池的权重，使用默认值
                            enabled = False
                            probability = 1.0

                    if enabled:
                        if probability == 0:
                            # 禁用：排除该学生
                            continue
                        elif probability >= 1000:
                            # 必中：设置极高权重
                            filtered_students.append(student)
                            weights.append(1000.0)
                        else:
                            # 直接使用用户输入的权重值
                            filtered_students.append(student)
                            weights.append(probability)
                    else:
                        # 未启用：正常权重
                        filtered_students.append(student)
                        weights.append(1.0)
                else:
                    # 未设置：正常权重
                    filtered_students.append(student)
                    weights.append(1.0)

            return filtered_students, weights
        except Exception as e:
            logger.error(f"应用内幕设置失败: {e}")
            return students_dict_list, [1.0] * len(students_dict_list)

    @staticmethod
    def apply_probability_weights_to_items(items, mode, pool_name):
        """应用内幕设置到奖品列表

        Args:
            items: 奖品字典列表
            mode: 模式（0=点名, 1=抽奖）
            pool_name: 奖池名称（用于日志）

        Returns:
            tuple: (过滤后的奖品列表, 权重列表)
        """
        try:
            settings = BehindScenesUtils.get_behind_scenes_settings()
            if (
                settings
                and isinstance(settings, dict)
                and not settings.get("enabled_global", True)
            ):
                return items, [1.0] * len(items)

            filtered_items = []
            weights = []

            for item in items:
                name = item.get("name", "")
                if name in settings:
                    if mode == 0:
                        # 点名模式（奖品不使用点名模式）
                        filtered_items.append(item)
                        weights.append(1.0)
                    else:
                        # 抽奖模式
                        lottery_settings = settings[name].get("lottery", {})
                        if pool_name and pool_name in lottery_settings:
                            prob_settings = lottery_settings[pool_name]
                            enabled = prob_settings.get("enabled", False)
                            probability = prob_settings.get("probability", 1.0)
                        else:
                            # 未设置该奖池的权重，使用默认值
                            enabled = False
                            probability = 1.0

                        if enabled:
                            if probability == 0:
                                # 禁用：排除该奖品
                                continue
                            elif probability >= 1000:
                                # 必中：设置极高权重
                                filtered_items.append(item)
                                weights.append(1000.0)
                            else:
                                # 直接使用用户输入的权重值
                                filtered_items.append(item)
                                weights.append(probability)
                        else:
                            # 未启用：正常权重
                            filtered_items.append(item)
                            weights.append(1.0)
                else:
                    # 未设置：正常权重
                    filtered_items.append(item)
                    weights.append(1.0)

            return filtered_items, weights
        except Exception as e:
            logger.error(f"应用内幕设置失败: {e}")
            return items, [1.0] * len(items)

    @staticmethod
    def ensure_guaranteed_selection(
        students_with_weight, weights, class_name, pool_name=None
    ):
        """确保必中人员被选中

        Args:
            students_with_weight: 学生列表
            weights: 权重列表
            class_name: 班级名称（用于日志）
            pool_name: 奖池名称（仅在抽奖模式下使用）

        Returns:
            list: 选中的学生列表（如果存在必中人员）
        """
        try:
            guaranteed_students = []
            for i, (student, weight) in enumerate(
                zip(students_with_weight, weights)
            ):
                if weight == 1000.0:
                    guaranteed_students.append(student)

            if guaranteed_students:
                names = [s.get("name", "") for s in guaranteed_students]
                return guaranteed_students

            return None
        except Exception as e:
            logger.error(f"确保必中人员失败: {e}")
            return None
