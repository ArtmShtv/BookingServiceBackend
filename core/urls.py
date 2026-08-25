from django.contrib import admin
from django.urls import path, include

from address import urls as address_urls
from booking import urls as booking_urls
from user import urls as user_urls

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/user/", include(user_urls)),
    path("api/address/", include(address_urls)),
    path("api/booking/", include(booking_urls)),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
