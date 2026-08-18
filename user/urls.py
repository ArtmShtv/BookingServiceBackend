from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from user.views import UserRegisterAPIView


urlpatterns = [
    path("reg/", UserRegisterAPIView.as_view(), name="reg"),
    path('auth/', TokenObtainPairView.as_view(), name='auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]