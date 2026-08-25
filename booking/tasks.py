from celery import shared_task
from django.contrib.auth import get_user_model

from booking.models import UnitSchedule

User = get_user_model()


@shared_task
def send_email(
    user_id: int,
    unit_schedule_id: int,
    notes: str,
) -> None:
    user = User.objects.get(pk=user_id)
    unit_schedule = UnitSchedule.objects.get(pk=unit_schedule_id)

    print("Hui")