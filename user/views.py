from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.serializers import ModelSerializer

from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterAPIView(APIView):
    class InputSerializer(ModelSerializer):
        class Meta:
            model = User
