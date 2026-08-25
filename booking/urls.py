from django.urls import path

from booking.views import (
    UnitDetailScheduleAPIView,
    BookingAPIView
)


urlpatterns = [
    path(
        "units/<int:unit_id>/schedules/<str:date>/",
        UnitDetailScheduleAPIView.as_view(),
        name="unit-schedules",
    ),
    path(
        "unit_schedules/<int:schedule_id>/",
        BookingAPIView.as_view(),
        name="booking"
    )
]