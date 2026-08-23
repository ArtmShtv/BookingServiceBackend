from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from address.models import Unit
from booking.models import (
    UnitSchedule,
    Booking
)

from booking.services import (
    get_existing_day_schedule_for_unit,
    has_overlapping_intervals
)

from datetime import time


class UnitDetailScheduleAPIView(APIView):
    SAFE_METHODS = ("GET")

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]

    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = UnitSchedule
            fields = ["unit", "date", "start_time", "end_time",
                      "is_active", "recurrence", "updated_at"]


    def get(self, request, unit_id:int):
        unit = get_object_or_404(Unit, id=unit_id)
        unit_schedule = UnitSchedule.objects.filter(unit=unit)

        output_serializer = self.OutputListSerializer(
            unit_schedule, 
            many=True
        ) 
        return Response(
            output_serializer.data, 
            status=status.HTTP_200_OK
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

    def post(self, request, unit_id:int, date):
        unit = get_object_or_404(id=unit_id)

        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid()

        new_unit_schedules = input_serializer["unit_schedule"] 

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

            for ex_start, ex_end in existing_unit_schedule_intervals:
                if new_start < ex_end and ex_start < new_end:
                    break
            else:
                to_create.append(UnitSchedule(
                    unit = unit,
                    date = date,
                    start_time = new_start,
                    end_time = new_end,
                    is_active = True,
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

    def delete(self, request):
        input_serializer = self.InputDeleteSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        UnitSchedule.objects.filter(id__in=input_serializer.validated_data["schedules_id"]).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)







