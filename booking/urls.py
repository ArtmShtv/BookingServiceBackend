from django.urls import path

from booking.views import (
    UnitScheduleAPIView,
    BookingAPIView
)


urlpatterns = [
    path(
        "units/<int:unit_id>/schedules/",
        UnitScheduleAPIView.as_view(),
        name="unit-schedules",
    ),
    path(
        "booking/unit_schedules/<int:schedule_id>/",
        BookingAPIView.as_view(),
        name="booking"
    )
]