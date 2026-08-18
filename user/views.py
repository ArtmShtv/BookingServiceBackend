from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterAPIView(APIView):
    class InputSerializer(serializers.ModelSerializer):
        password = serializers.CharField(
            write_only=True,
            min_length=8,
            style={"input_type": "password"},
        )
        password_confirm = serializers.CharField(
            write_only=True,
            min_length=8,
            style={"input_type": "password"},
        )

        class Meta:
            model = User
            fields = [
                "email",
                "first_name",
                "last_name",
                "password",
                "password_confirm",
            ]

        def validate_email(self, value):
            email = value.strip().lower()

            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )

            return email

        def validate(self, attrs):
            if attrs["password"] != attrs["password_confirm"]:
                raise serializers.ValidationError(
                    {"password_confirm": "Passwords do not match"}
                )

            return attrs

        def create(self, validated_data):
            password = validated_data.pop("password")
            validated_data.pop("password_confirm")

            return User.objects.create_user(
                password=password,
                **validated_data,
            )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )
