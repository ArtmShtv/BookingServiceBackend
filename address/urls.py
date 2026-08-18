from django.urls import path

from address import views


urlpatterns = [
    # # Hotel endpoints
    # path("hotel/", views.HotelAPIView.as_view(), name="hotel-list"),
    # path(
    #     "hotel/<int:hotel_id>/", views.HotelDetailAPIView.as_view(), name="hotel-detail"
    # ),
    # path("hotel/<int:hotel_id>/rooms/", views.RoomAPIView.as_view(), name="room-list"),
    # path(
    #     "hotel/<int:hotel_id>/rooms/<int:room_id>/",
    #     views.RoomDetailAPIView.as_view(),
    #     name="room-detail",
    # ),
    # # Room categories endpoints
    # path(
    #     "hotel/<int:hotel_id>/categories/",
    #     views.RoomCategoryAPIView.as_view(),
    #     name="room-category-list",
    # ),
    # path(
    #     "hotel/<int:hotel_id>/categories/<int:category_id>/",
    #     views.RoomCategoryDetailAPIView.as_view(),
    #     name="room-category-detail",
    # ),
    # # Address enpoints
    # path("address/", views.AddressAPIView.as_view(), name="hotel-country"),
    # path(
    #     "address/<int:address_id>/",
    #     views.AddressDetailAPIView.as_view(),
    #     name="hotel-country-detail",
    # ),
    # # Country enpoints
    # path("country/", views.CountryAPIView.as_view(), name="hotel-country"),
    # path(
    #     "country/<int:country_id>/",
    #     views.CountryDetailAPIView.as_view(),
    #     name="hotel-country-detail",
    # ),
    # # Region enpoints
    # path(
    #     "country/<int:country_id>/regions/",
    #     views.RegionAPIView.as_view(),
    #     name="hotel-region",
    # ),
    # path(
    #     "region/<int:region_id>/",
    #     views.RegionAPIView.as_view(),
    #     name="hotel-region-detail",
    # ),
    # # City enpoints
    # path(
    #     "region/<int:region_id>/city/", views.CityAPIView.as_view(), name="hotel-city"
    # ),
    # path(
    #     "city/<int:city_id>/",
    #     views.CityDetailAPIView.as_view(),
    #     name="hotel-city-detail",
    # ),
]
