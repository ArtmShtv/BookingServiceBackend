from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema, 
    OpenApiResponse, 
    OpenApiExample,
    OpenApiParameter,
)

from datetime import date as date_type

from address.models import Unit
from booking.models import (
    UnitSchedule,
    Booking
)

from booking.services import (
    get_existing_day_schedule_for_unit,
    has_overlapping_intervals
)
from booking.tasks import(
    send_confirm_email
)

from datetime import time

User = get_user_model()


class UnitScheduleAPIView(APIView):
    SAFE_METHODS = ("GET")

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = UnitSchedule
            fields = [
                "unit", 
                "date", 
                "start_time", 
                "end_time",
                "recurrence", 
                "updated_at"
            ]

    @extend_schema(
        operation_id="list_unit_schedules",
        summary="List unit schedules",
        description=(
            "Returns all schedules for the specified unit"
            "Optionally filter schedules by an exact date in `YYYY-MM-DD` format"
        ),
        tags=["Unit Schedules"],
        parameters=[
            OpenApiParameter(
                name="unit_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the unit",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Optional exact schedule date in YYYY-MM-DD format"
                    "If omitted, returns schedules for that date"
                ),
                examples=[
                    OpenApiExample(
                        "Date filter example",
                        value="2026-08-25",
                    ),
                ],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OutputListSerializer(many=True),
                description="A list of schedules for the unit",
            ),
            404: OpenApiResponse(
                description="Unit not found",
            ),
        },
        examples=[
            OpenApiExample(
                name="Schedules returned",
                response_only=True,
                status_codes=["200"],
                value=[
                    {
                        "unit": 1,
                        "date": "2026-08-25",
                        "start_time": "09:00:00",
                        "end_time": "10:30:00",
                        "recurrence": "once",
                        "updated_at": "2026-08-25T18:13:27.434515Z",
                    },
                    {
                        "unit": 1,
                        "date": "2026-08-25",
                        "start_time": "13:00:00",
                        "end_time": "16:00:00",
                        "recurrence": "weekly",
                        "updated_at": "2026-08-25T18:15:10.000000Z",
                    },
                ],
            ),
        ],
    )
    def get(self, request, unit_id: int):
        unit = get_object_or_404(Unit, id=unit_id)

        unit_schedules = UnitSchedule.objects.filter(
            unit=unit,
        ).order_by("date", "start_time")

        date = request.query_params.get("date")

        if date:
            unit_schedules = unit_schedules.filter(date=date)

        output_serializer = self.OutputListSerializer(
            unit_schedules,
            many=True,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


    class InputCreateSerializer(serializers.Serializer):
        class UnitScheduleSerializer(serializers.Serializer):
            start_time = serializers.TimeField()
            end_time = serializers.TimeField()
            is_active = serializers.BooleanField(
                required=False,
                default=True,
            )
            recurrence = serializers.ChoiceField(
                choices=UnitSchedule.RecurrenceStatus.choices,
                required=False,
                default=UnitSchedule.RecurrenceStatus.ONCE,
            )

            def validate(self, attrs):
                start_time: time = attrs["start_time"]
                end_time: time = attrs["end_time"]

                if start_time >= end_time:
                    raise serializers.ValidationError(
                        "start_time must be earlier than end_time."
                    )

                min_time = time(0, 0)
                max_time = time(23, 59, 59)

                if not (min_time <= start_time <= max_time):
                    raise serializers.ValidationError(
                        "start_time must be between 00:00 and 23:59"
                    )
                if not (min_time <= end_time <= max_time):
                    raise serializers.ValidationError(
                        "end_time must be between 00:00 and 23:59"
                    )

                return attrs

        unit_schedules = UnitScheduleSerializer(
            many=True,
            allow_empty=False
        )

    @extend_schema(
        operation_id="create_unit_schedules",
        summary="Create unit schedules",
        description=(
            "Creates one or more schedules for a unit on the date provided in the URL"
            "Schedules in the request must not overlap each other or existing active schedules"
        ),
        tags=["Unit Schedules"],
        parameters=[
            OpenApiParameter(
                name="unit_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the unit",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.PATH,
                required=True,
                description="Schedule date in YYYY-MM-DD format",
                examples=[
                    OpenApiExample(
                        "Date example",
                        value="2026-08-25",
                    ),
                ],
            ),
        ],
        request=InputCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Unit schedules were created successfully",
                examples=[
                    OpenApiExample(
                        "Created schedules count",
                        value={"created_count": 2},
                        response_only=True,
                        status_codes=["201"],
                    ),
                ],
            ),
            400: OpenApiResponse(
                description=(
                    "Invalid request, invalid date, invalid time range"
                    "or overlapping schedules"
                ),
                examples=[
                    OpenApiExample(
                        "Schedules overlap each other",
                        value={
                            "detail": "New schedules overlap with each other"
                        },
                        response_only=True,
                        status_codes=["400"],
                    ),
                    OpenApiExample(
                        "Invalid time range",
                        value={
                            "non_field_errors": [
                                "start_time must be earlier than end_time"
                            ]
                        },
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Unit not found",
            ),
        },
        examples=[
            OpenApiExample(
                name="Create one schedule",
                value={
                    "unit_schedules": [
                        {
                            "start_time": "09:00",
                            "end_time": "10:00",
                            "is_active": True,
                            "recurrence": "daily",
                        },
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Create multiple schedules",
                value={
                    "unit_schedules": [
                        {
                            "start_time": "09:00",
                            "end_time": "10:00",
                            "is_active": True,
                            "recurrence": "daily",
                        },
                        {
                            "start_time": "10:00",
                            "end_time": "11:00",
                            "is_active": True,
                            "recurrence": "daily",
                        },
                    ],
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, unit_id:int, date):
        try:
            date = date_type.fromisoformat(date)
        except ValueError:
            raise ValidationError({
                "date": "Expected format: YYYY-MM-DD."
            })
        unit = get_object_or_404(Unit, id=unit_id)

        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid()

        new_unit_schedules = input_serializer.validated_data["unit_schedules"] 

        existing_unit_schedule_intervals = get_existing_day_schedule_for_unit(unit, date)

        
        new_unit_schedule_intervals = sorted(
            [(s["start_time"], s["end_time"]) for s in new_unit_schedules],
            key=lambda x: x[0]
        )
        if has_overlapping_intervals(new_unit_schedule_intervals):
            return Response(
                {"detail": "New schedules overlap with each other"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        to_create = []
        for schedule in new_unit_schedules:
            new_start = schedule["start_time"]
            new_end = schedule["end_time"]
            recurrence = schedule["recurrence"]
            is_active = schedule["is_active"]

            for ex_start, ex_end in existing_unit_schedule_intervals:
                if new_start < ex_end and ex_start < new_end:
                    break
            else:
                to_create.append(UnitSchedule(
                    unit = unit,
                    date = date,
                    start_time = new_start,
                    end_time = new_end,
                    is_active = is_active,
                    recurrence = recurrence
                ))
        
        with transaction.atomic():
            UnitSchedule.objects.bulk_create(
                to_create
            )

        return Response({
            "created_count": len(to_create)
        }, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        schedules_id = serializers.ListField(
            child = serializers.IntegerField()
        )

    @extend_schema(
        operation_id="delete_unit_schedules",
        summary="Delete unit schedules",
        description=(
            "Deletes all unit schedules whose IDs are included in schedules_id"
            "If an ID does not exist, it is ignored."
        ),
        tags=["Unit Schedules"],
        request=InputDeleteSerializer,
        responses={
            204: OpenApiResponse(
                description="Schedules deleted successfully. Response body is empty",
            ),
            400: OpenApiResponse(
                description="Invalid request body.",
                examples=[
                    OpenApiExample(
                        name="Invalid schedule ID",
                        value={
                            "schedules_id": {
                                "0": ["A valid integer is required"]
                            }
                        },
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                name="Delete one schedule",
                value={
                    "schedules_id": [15],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Delete several schedules",
                value={
                    "schedules_id": [15, 16, 24],
                },
                request_only=True,
            ),
        ],
    )
    def delete(self, request):
        input_serializer = self.InputDeleteSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        UnitSchedule.objects.filter(id__in=input_serializer.validated_data["schedules_id"]).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UnitScheduleDetailAPIView(APIView):
    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = UnitSchedule
            fields = ["unit", "date", "start_time", "end_time", "is_active", "recurrence"]

    @extend_schema(
        request=InputUpdateSerializer(),
        responses={
            200: OpenApiResponse(description="Unit schedule updated"),
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Unit schedule not found"),
        },
        examples=[
            OpenApiExample(
                name="Update unit schedule",
                value={
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "is_active": True,
                    "recurrence": "daily"
                },
                request_only = True,
            )
        ],
        description="Update (Patch) unit schedule by its pk",
        tags=["Unit Schedule"],
    )
    def patch(self, request):
        pass


class BookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class OutputListSerializer(serializers.ModelSerializer):
        date = serializers.DateField(
            source="unit_schedule.date",
            read_only=True,
        )
        interval = serializers.SerializerMethodField()

        class Meta:
            model = Booking
            fields = [
                "id",
                "date",
                "interval",
                "status",
                "notes",
                "created_at",
            ]

        def get_interval(self, obj):
            return (
                f"{obj.unit_schedule.start_time}"
                f"-{obj.unit_schedule.end_time}"
            )

    @extend_schema(
        operation_id="list_my_bookings",
        summary="List my bookings",
        description=(
            "Returns all bookings belonging to the authenticated user"
            "ordered by schedule date and start time."
        ),
        tags=["Booking"],
        responses={
            200: OpenApiResponse(
                response=OutputListSerializer(many=True),
                description="List of bookings for the authenticated user.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
        },
        examples=[
            OpenApiExample(
                name="User bookings returned",
                value=[
                    {
                        "id": 42,
                        "date": "2026-08-25",
                        "interval": "09:00-10:30",
                        "status": "confirmed",
                        "notes": "Please prepare the room",
                        "created_at": "2026-08-25T18:13:27.434515Z",
                    },
                    {
                        "id": 43,
                        "date": "2026-08-26",
                        "interval": "14:00-15:00",
                        "status": "pending",
                        "notes": "",
                        "created_at": "2026-08-25T19:00:00Z",
                    },
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):
        bookings = (
            Booking.objects
            .filter(user=request.user)
            .select_related("unit_schedule")
            .order_by(
                "unit_schedule__date",
                "unit_schedule__start_time",
            )
        )

        output_serializer = self.OutputListSerializer(
            bookings,
            many=True,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class BookingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]


    class InputCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Booking
            fields = ["notes"]

    @extend_schema(
        operation_id="create_booking",
        summary="Book a unit schedule",
        description=(
            "Creates a booking for the authenticated user and the selected unit schedule"
            "A schedule can be booked only once"
        ),
        tags=["Booking"],
        parameters=[
            OpenApiParameter(
                name="schedule_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the unit schedule to book",
                examples=[
                    OpenApiExample(
                        "Schedule ID example",
                        value=12,
                    ),
                ],
            ),
        ],
        request=InputCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Booking created successfully",
                examples=[
                    OpenApiExample(
                        name="Booking created",
                        value={
                            "id": 42,
                            "message": (
                                "Unit booked for 2026-08-25 09:00:00-10:00:00"
                            ),
                        },
                        response_only=True,
                        status_codes=["201"],
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Invalid request body.",
                examples=[
                    OpenApiExample(
                        name="Invalid notes type",
                        value={
                            "notes": [
                                "Not a valid string."
                            ],
                        },
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            404: OpenApiResponse(
                description="Unit schedule not found.",
            ),
            409: OpenApiResponse(
                description="The unit schedule has already been booked.",
                examples=[
                    OpenApiExample(
                        name="Schedule already booked",
                        value={
                            "detail": "This schedule is already booked.",
                        },
                        response_only=True,
                        status_codes=["409"],
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                name="Book with notes",
                value={
                    "notes": "Please prepare the room",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Book without notes",
                value={},
                request_only=True,
            ),
        ],
    )
    def post(self, request, schedule_id: int):
        user = request.user
        unit_schedule = get_object_or_404(
            UnitSchedule,
            id=schedule_id,
        )

        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        notes = input_serializer.validated_data.get("notes", "")

        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    unit_schedule=unit_schedule,
                    user=user,
                    notes=notes,
                )

                transaction.on_commit(
                    lambda: send_confirm_email.delay(
                        user_id=user.id,
                        unit_schedule_id=unit_schedule.id,
                        notes=notes,
                    )
                )

        except IntegrityError:
            return Response(
                {"detail": "This schedule is already booked."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "id": booking.id,
                "message": (
                    f"Unit booked for {unit_schedule.date} "
                    f"{unit_schedule.start_time}-{unit_schedule.end_time}"
                ),
            },
            status=status.HTTP_201_CREATED,
        )


    @extend_schema(
        operation_id="cancel_booking",
        summary="Cancel a booking",
        description=(
            "Cancels a booking belonging to the authenticated user"
            "A cancelled booking frees its unit schedule for a new booking"
        ),
        tags=["Bookings"],
        parameters=[
            OpenApiParameter(
                name="booking_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the booking to cancel",
                examples=[
                    OpenApiExample(
                        "Booking ID example",
                        value=42,
                    ),
                ],
            ),
        ],
        request=None,
        responses={
            204: OpenApiResponse(
                description="Booking cancelled successfully. Response body is empty",
            ),
            400: OpenApiResponse(
                description="Booking has already been cancelled",
                examples=[
                    OpenApiExample(
                        name="Already cancelled",
                        value={
                            "detail": "Booking is already cancelled",
                        },
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided",
            ),
            404: OpenApiResponse(
                description=(
                    "Booking was not found, or it does not belong"
                    "to the authenticated user"
                ),
            ),
        },
    )
    def patch(self, request, booking_id: int):
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            user=request.user,
        )

        if booking.status == Booking.Status.CANCELLED:
            return Response(
                {"detail": "Booking is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
