from __future__ import annotations
import yaml
from datetime import time
from typing import Dict, List
from loguru import logger


class CSESParser:
    """CSES格式课程表解析器"""

    def __init__(self):
        self.schedule_data = None

    def load_from_file(self, file_path: str) -> bool:
        """从文件加载CSES数据

        Args:
            file_path: CSES文件路径

        Returns:
            bool: 加载成功返回True，否则返回False
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.schedule_data = yaml.safe_load(f)
            return self._validate_schedule()
        except Exception as e:
            logger.error(f"加载CSES文件失败: {e}")
            return False

    def load_from_content(self, content: str) -> bool:
        """从字符串内容加载CSES数据

        Args:
            content: YAML格式的CSES内容

        Returns:
            bool: 加载成功返回True，否则返回False
        """
        try:
            self.schedule_data = yaml.safe_load(content)
            return self._validate_schedule()
        except Exception as e:
            logger.exception(f"解析CSES内容失败: {e}")
            return False

    def get_class_times_by_day(self, day_of_week: int) -> Dict[str, str]:
        """获取指定星期几的上课时间段

        Args:
            day_of_week: 星期几（1=星期一，7=星期日）

        Returns:
            Dict[str, str]: 上课时间段字典，格式为 {"name": "HH:MM:SS-HH:MM:SS"}
        """
        if not self.schedule_data:
            return {}

        class_times = {}
        schedule = self.schedule_data.get("schedule", {})
        timeslots = schedule.get("timeslots", [])

        valid_timeslots = [
            slot
            for slot in timeslots
            if isinstance(slot, dict)
            and slot.get("start_time")
            and slot.get("end_time")
            and slot.get("day_of_week") == day_of_week
        ]

        sorted_timeslots = self._sort_timeslots_by_time(valid_timeslots)

        for i, timeslot in enumerate(sorted_timeslots):
            start_time = self._format_time_for_secrandom(timeslot.get("start_time", ""))
            end_time = self._format_time_for_secrandom(timeslot.get("end_time", ""))
            class_name = timeslot.get("name", f"课程_{i + 1}")
            class_times[class_name] = f"{start_time}-{end_time}"

        logger.info(f"成功获取星期{day_of_week}的{len(class_times)}个上课时间段")
        return class_times

    def get_class_times_by_day_with_week(
        self, day_of_week: int, week_type: str = "all"
    ) -> Dict[str, str]:
        """获取指定星期几和周数的上课时间段

        Args:
            day_of_week: 星期几（1=星期一，7=星期日）
            week_type: 周数类型（"all"=所有周，"odd"=单数周，"even"=双数周）

        Returns:
            Dict[str, str]: 上课时间段字典，格式为 {"name": "HH:MM:SS-HH:MM:SS"}
        """
        if not self.schedule_data:
            return {}

        class_times = {}
        schedules = self.schedule_data.get("schedules", [])

        valid_schedules = []
        for sched in schedules:
            if isinstance(sched, dict) and sched.get("enable_day") == day_of_week:
                sched_weeks = sched.get("weeks", "all")
                if (
                    week_type == "all"
                    or sched_weeks == "all"
                    or sched_weeks == week_type
                ):
                    valid_schedules.append(sched)

        all_classes = []
        for sched in valid_schedules:
            classes = sched.get("classes", [])
            if isinstance(classes, list):
                all_classes.extend(classes)

        subject_teacher_map = self._build_subject_teacher_map()

        timeslots = []
        for cls in all_classes:
            if isinstance(cls, dict):
                teacher = cls.get("teacher", "")
                if not teacher:
                    teacher = subject_teacher_map.get(cls.get("subject", ""), "")

                timeslot = {
                    "name": cls.get("subject", ""),
                    "start_time": cls.get("start_time"),
                    "end_time": cls.get("end_time"),
                    "teacher": teacher,
                    "location": cls.get("room", ""),
                    "day_of_week": day_of_week,
                }
                timeslots.append(timeslot)

        sorted_timeslots = self._sort_timeslots_by_time(timeslots)

        for i, timeslot in enumerate(sorted_timeslots):
            start_time = self._format_time_for_secrandom(timeslot.get("start_time", ""))
            end_time = self._format_time_for_secrandom(timeslot.get("end_time", ""))
            class_name = timeslot.get("name", f"课程_{i + 1}")
            class_times[class_name] = f"{start_time}-{end_time}"

        logger.info(
            f"成功获取星期{day_of_week}（{week_type}周）的{len(class_times)}个上课时间段"
        )
        return class_times

    def get_non_class_times(self) -> Dict[str, str]:
        """获取非上课时间段配置

        将CSES格式的时间段转换为SecRandom使用的非上课时间段格式

        Returns:
            Dict[str, str]: 非上课时间段字典，格式为 {"name": "HH:MM:SS-HH:MM:SS"}
        """
        if not self.schedule_data:
            return {}

        non_class_times = {}
        schedule = self.schedule_data.get("schedule", {})
        timeslots = schedule.get("timeslots", [])

        valid_timeslots = [
            slot
            for slot in timeslots
            if isinstance(slot, dict)
            and slot.get("start_time")
            and slot.get("end_time")
        ]

        timeslots_by_day = {}
        for slot in valid_timeslots:
            day = slot.get("day_of_week", 0)
            if day not in timeslots_by_day:
                timeslots_by_day[day] = []
            timeslots_by_day[day].append(slot)

        for day, day_timeslots in timeslots_by_day.items():
            sorted_timeslots = self._sort_timeslots_by_time(day_timeslots)

            class_periods = []
            for timeslot in sorted_timeslots:
                start_time = self._format_time_for_secrandom(
                    timeslot.get("start_time", "")
                )
                end_time = self._format_time_for_secrandom(timeslot.get("end_time", ""))
                class_periods.append((start_time, end_time))

            if class_periods:
                first_start = class_periods[0][0]
                if first_start != "00:00:00":
                    non_class_times[f"day_{day}_before_first_class"] = (
                        f"00:00:00-{first_start}"
                    )

                for i in range(len(class_periods) - 1):
                    current_end = class_periods[i][1]
                    next_start = class_periods[i + 1][0]
                    if current_end != next_start:
                        period_name = f"day_{day}_break_{i + 1}"
                        non_class_times[period_name] = f"{current_end}-{next_start}"

                last_end = class_periods[-1][1]
                if last_end != "23:59:59":
                    non_class_times[f"day_{day}_after_last_class"] = (
                        f"{last_end}-23:59:59"
                    )

        logger.info(f"成功解析CSES课程表，生成{len(non_class_times)}个非上课时间段")
        return non_class_times

    def get_class_info(self) -> List[Dict]:
        """获取课程信息列表

        Returns:
            List[Dict]: 课程信息列表
        """
        if not self.schedule_data:
            return []

        schedule = self.schedule_data.get("schedule", {})
        timeslots = schedule.get("timeslots", [])

        class_info = []
        for timeslot in timeslots:
            if isinstance(timeslot, dict):
                info = {
                    "name": timeslot.get("name", ""),
                    "start_time": self._format_time_for_secrandom(
                        timeslot.get("start_time", "")
                    ),
                    "end_time": self._format_time_for_secrandom(
                        timeslot.get("end_time", "")
                    ),
                    "teacher": timeslot.get("teacher", ""),
                    "location": timeslot.get("location", ""),
                    "day_of_week": timeslot.get("day_of_week", ""),
                }
                class_info.append(info)

        return class_info

    def get_summary(self) -> str:
        """获取课程表摘要信息

        Returns:
            str: 摘要信息
        """
        if not self.schedule_data:
            return "未加载课程表"

        schedule = self.schedule_data.get("schedule", {})
        timeslots = schedule.get("timeslots", [])

        if not timeslots:
            return "课程表为空"

        start_times = [
            str(slot.get("start_time", ""))
            for slot in timeslots
            if isinstance(slot, dict) and slot.get("start_time")
        ]
        end_times = [
            str(slot.get("end_time", ""))
            for slot in timeslots
            if isinstance(slot, dict) and slot.get("end_time")
        ]

        if not start_times or not end_times:
            return f"课程表包含{len(timeslots)}个时间段"

        summary = f"课程表包含{len(timeslots)}个时间段，"
        summary += f"最早开始时间：{min(start_times)}，"
        summary += f"最晚结束时间：{max(end_times)}"

        return summary

    def _validate_schedule(self) -> bool:
        """验证课程表数据的有效性

        Returns:
            bool: 数据有效返回True，否则返回False
        """
        if not self.schedule_data:
            logger.error("课程表数据为空")
            return False

        schedule = self.schedule_data.get("schedule")
        if schedule and isinstance(schedule, dict):
            timeslots = schedule.get("timeslots")
            if timeslots is None:
                logger.warning("缺少'timeslots'字段，将使用空课程表数据")
                return True
            if not isinstance(timeslots, list):
                logger.error("'timeslots'字段必须是列表类型")
                return False
            for i, timeslot in enumerate(timeslots):
                if not self._validate_timeslot(timeslot, i):
                    return False
            return True

        schedules = self.schedule_data.get("schedules")
        if schedules and isinstance(schedules, list):
            subject_teacher_map = self._build_subject_teacher_map()

            timeslots = []
            for day_schedule in schedules:
                if isinstance(day_schedule, dict) and day_schedule.get("classes"):
                    for cls in day_schedule["classes"]:
                        if isinstance(cls, dict):
                            teacher = cls.get("teacher", "")
                            if not teacher:
                                teacher = subject_teacher_map.get(
                                    cls.get("subject", ""), ""
                                )

                            timeslot = {
                                "name": cls.get("subject", ""),
                                "start_time": cls.get("start_time"),
                                "end_time": cls.get("end_time"),
                                "teacher": teacher,
                                "location": cls.get("room", ""),
                                "day_of_week": day_schedule.get("enable_day"),
                            }
                            timeslots.append(timeslot)

            self.schedule_data["schedule"] = {"timeslots": timeslots}
            return True

        logger.warning("缺少有效的课程表结构，将使用空课程表数据")
        self.schedule_data["schedule"] = {"timeslots": []}
        return True

    def _validate_timeslot(self, timeslot: dict, index: int) -> bool:
        """验证单个时间段的配置

        Args:
            timeslot: 时间段配置字典
            index: 时间段索引

        Returns:
            bool: 有效返回True，否则返回False
        """
        required_fields = ["name", "start_time", "end_time"]
        for field in required_fields:
            if field not in timeslot:
                logger.error(f"时间段{index}缺少'{field}'字段")
                return False

        try:
            start_time = self._parse_time(timeslot["start_time"])
            end_time = self._parse_time(timeslot["end_time"])

            if start_time >= end_time:
                logger.error(f"时间段{index}的开始时间必须早于结束时间")
                return False

        except ValueError as e:
            logger.error(f"时间段{index}时间格式错误: {e}")
            return False

        return True

    def _parse_time(self, time_str: str) -> time:
        """解析时间字符串

        Args:
            time_str: 时间字符串 (HH:MM 或 HH:MM:SS)

        Returns:
            time: 时间对象

        Raises:
            ValueError: 时间格式错误
        """
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    return time(int(parts[0]), int(parts[1]))
                elif len(parts) == 3:
                    return time(int(parts[0]), int(parts[1]), int(parts[2]))
            raise ValueError(f"无效的时间格式: {time_str}")
        except (ValueError, IndexError):
            logger.error(f"无法解析时间: {time_str}")
            raise ValueError(f"无法解析时间: {time_str}") from None

    def _parse_time_string_to_seconds(self, time_val: str | int) -> int:
        """将时间字符串或整数转换为总秒数

        Args:
            time_val: 时间字符串 (HH:MM 或 HH:MM:SS) 或整数秒数

        Returns:
            int: 时间的总秒数

        Raises:
            ValueError: 时间格式错误
        """
        if isinstance(time_val, int):
            return time_val

        time_str = str(time_val)

        try:
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60
                elif len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return int(time_str)
        except (ValueError, IndexError):
            logger.error(f"无法解析时间字符串: {time_val}")
            raise ValueError(f"无法解析时间字符串: {time_val}") from None

    def _format_time_for_secrandom(self, time_val: str | int) -> str:
        """将时间字符串或秒数格式化为SecRandom需要的格式 (HH:MM:SS)

        Args:
            time_val: 原始时间字符串 (HH:MM 或 HH:MM:SS) 或秒数 (int)

        Returns:
            str: 格式化后的时间字符串 (HH:MM:SS)
        """
        if isinstance(time_val, int):
            hours = time_val // 3600
            minutes = (time_val % 3600) // 60
            seconds = time_val % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        time_str = str(time_val)
        if time_str.count(":") == 1:
            return f"{time_str}:00"
        return time_str

    def _build_subject_teacher_map(self) -> Dict[str, str]:
        """构建科目-老师映射表

        Returns:
            Dict[str, str]: 科目名称到老师名称的映射
        """
        subject_teacher_map = {}
        subjects = self.schedule_data.get("subjects")
        if subjects and isinstance(subjects, list):
            for subject in subjects:
                if isinstance(subject, dict):
                    name = subject.get("name")
                    teacher = subject.get("teacher")
                    if name and teacher:
                        subject_teacher_map[name] = teacher
        return subject_teacher_map

    def _sort_timeslots_by_time(self, timeslots: List[dict]) -> List[dict]:
        """按照开始时间排序时间段

        Args:
            timeslots: 时间段列表

        Returns:
            List[dict]: 排序后的时间段列表
        """

        def get_time_key(slot):
            time_str = str(slot.get("start_time", ""))
            return self._parse_time_string_to_seconds(time_str)

        return sorted(timeslots, key=get_time_key)
