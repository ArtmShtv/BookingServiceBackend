from django.urls import path

from address import views


urlpatterns = [
    # Country enpoints
    path("country/", 
        views.CountryAPIView.as_view(), 
        name="country"
    ),
    path(
        "country/<int:country_id>/",
        views.CountryDetailAPIView.as_view(),
        name="country-detail",
    ),
    # Region enpoints
    path(
        "country/<int:country_id>/region/",
        views.RegionAPIView.as_view(),
        name="region",
    ),
    path(
        "region/<int:region_id>/",
        views.RegionDetailAPIView.as_view(),
        name="region-detail",
    ),
    # Settlement endpoints
    path(
        "settlement/type/",
        views.SettlementTypesAPIView.as_view(),
        name="settlement-type"
    ),
    path(
        "settlement/type/<int:settlement_type_id>",
        views.SettlementTypeDetailAPIView.as_view(),
        name="settlement-type-detail"
    ),
    path(
        "region/<int:region_id>/settlement/",
        views.SettlementAPIView.as_view(),
        name="settlement"
    ),
    path(
        "settlement/<int:settlement_id>/",
        views.SettlementDetailAPIView.as_view(),
        name="settlement-detail"
    ),
    # District endpoints
    path(
        "settlement/<int:settlement_id>/district/", 
        views.DistrictAPIView.as_view(), 
        name="district"
    ),
    path(
        "district/<int:district_id>/",
        views.DistrictDetailAPIView.as_view(), 
        name="district-detail"
    ),
    # Street endpoint
    path(
        "street/type/", 
        views.StreetTypeAPIView.as_view(), 
        name="street-type"
    ),
    path(
        "street/type/<int:street_type_id>/",
        views.StreetTypeDetailAPIView.as_view(),
        name="street-type-detail"
    ),
    path(
        "district/<int:district_id>/street/", 
        views.StreetAPIView.as_view(), 
        name="street"
    ),
    path(
        "street/<int:street_id>/",
        views.StreetDetailAPIView.as_view(),
        name="street-detail"
    ),
    # Address path
    path(
        "street/<int:street_id>/address/", 
        views.AdressAPIView.as_view(), 
        name="address"
    ),
    path(
        "address/<int:street_id>/",
        views.AddressDetailAPIView.as_view(),
        name="address-detail"
    ),
    # Building endpoints
    path(
        "building/types/",
        views.BuildingTypesAPIView.as_view(),
        name="building-types"
    ),
    path(
        "building/types/<int:building_type_id>/",
        views.BuildingTypesDetailAPIView.as_view(),
        name="building-types-detail"
    ),
]
