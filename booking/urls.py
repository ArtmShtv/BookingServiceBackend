from django.urls import path

from booking.views import (
    UnitScheduleAPIView,
    UnitScheduleDetailAPIView,
    BookingAPIView,
    BookingsUnitListAPIView,
    BookingsUserListAPIView,
    UnitReviewAPIView
)


urlpatterns = [
    # Schedules endpoints
    path(
        "units/<int:unit_id>/schedules/",
        UnitScheduleAPIView.as_view(),
        name="unit-schedules",
    ),
    path(
        "schedules/<int:schedule_id>/", 
        UnitScheduleDetailAPIView.as_view(), 
        name="unit-schedule-detail"
    ),

    # Booking endpoint
    path(
        "unit_schedules/",
        BookingAPIView.as_view(),
        name="booking"
    ),
    path(
        "unit/<int:unit_id>/",
        BookingsUnitListAPIView.as_view(),
        name="bookings-unit"
    ),
    path(
        "user/",
        BookingsUserListAPIView.as_view(),
        name="bookings-user"
    ),

    # UnitReview endpoints
    path(
        "units/<int:unit_id>/review/",
        UnitReviewAPIView.as_view(),
        name="unit-reviews",
    ),
]