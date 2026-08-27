from datetime import time
from datetime import date as date_type

from address.models import Unit
from booking.models import UnitSchedule


def get_existing_day_schedule_for_unit(
    unit: Unit,
    schedule_date: date_type,
) -> list[tuple[time, time]]:
    unit_schedules = (
        UnitSchedule.objects.filter(
            unit=unit,
            is_active=True,
        )
        .order_by("start_time")
    )

    intervals: list[tuple[time, time]] = []

    for schedule in unit_schedules:
        if schedule.recurrence == UnitSchedule.RecurrenceStatus.ONCE:
            if schedule.date != schedule_date:
                continue

        elif schedule.recurrence == UnitSchedule.RecurrenceStatus.DAILY:
            if schedule_date < schedule.date:
                continue

        elif schedule.recurrence == UnitSchedule.RecurrenceStatus.WEEKLY:
            if schedule_date < schedule.date:
                continue

            if schedule.date.weekday() != schedule_date.weekday():
                continue

        intervals.append(
            (schedule.start_time, schedule.end_time)
        )

    return intervals


def has_overlapping_intervals(intervals: list[tuple[time, time]]) -> bool:
    for i in range(len(intervals)-1):
        if intervals[i][1] > intervals[i+1][0]:
            return True
    return False