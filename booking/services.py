from datetime import datetime, date, time
from typing import List, Tuple

from django.db.models import QuerySet

from address.models import Unit
from booking.models import UnitSchedule


def get_existing_day_schedule_for_unit(
    unit: Unit,
    date: date,
) -> list[tuple[time, time]]:
    unit_schedules = (
        UnitSchedule.objects.filter(
            unit=unit,
            date=date,
            is_active=True,
        )
        .order_by("start_time")
    )

    res = []
    for schedule in unit_schedules:
        start_time = schedule.start_time
        end_time = schedule.end_time

        res.append((start_time, end_time))

    return res


def has_overlapping_intervals(intervals: list[tuple[time, time]]) -> bool:
    for i in range(len(intervals)-1):
        if intervals[i][1] > intervals[i+1][0]:
            return True
    return False