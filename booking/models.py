from django.db import models

from address.models import Unit

from django.contrib.auth import get_user_model

User = get_user_model()


class UnitSchedule(models.Model):
    class RecurrenceStatus(models.TextChoices):
        ONCE = "once", "Once"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    
    date = models.DateField(
        null=True,
        blank=True,
        help_text="Specific date / null for recurring templates",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this schedule is currently active",
    )

    recurrence = models.CharField(
        max_length=10,
        choices=RecurrenceStatus.choices,
        default=RecurrenceStatus.ONCE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="start_time_before_end_time",
            ),
        ]

    def __str__(self):
        if self.date:
            return f"{self.unit} — {self.date} ({self.start_time}–{self.end_time})"
        return f"{self.unit} — recurring {self.recurrence} ({self.start_time}–{self.end_time})"


class Booking(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    unit_schedule = models.ForeignKey(
        UnitSchedule,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="confirmed",
    )

    notes = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit_schedule"],
                condition=models.Q(status="confirmed"),
                name="one_confirmed_booking_per_schedule",
            ),
        ]

    def __str__(self):
        return f"{self.user} — {self.unit_schedule.unit} ({self.unit_schedule.date})"
