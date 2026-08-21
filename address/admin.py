# locations/admin.py
from django.contrib import admin

from .models import Country, Region, Settlement, SettlementType


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "iso_code")
    search_fields = ("name", "iso_code")


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "country")
    list_filter = ("country",)
    search_fields = (
        "name",
        "code",
        "country__name",
        "country__iso_code",
    )
    list_select_related = ("country",)

@admin.register(SettlementType)
class SettlementTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "settlement_type",
        "region",
        "country",
    )
    list_filter = (
        "settlement_type",
        "region__country",
        "region",
    )
    search_fields = (
        "name",
        "region__name",
        "region__country__name",
        "region__code",
    )
    list_select_related = (
        "settlement_type",
        "region",
        "region__country",
    )
    autocomplete_fields = (
        "settlement_type",
        "region",
    )
    ordering = (
        "region__country__name",
        "region__name",
        "name",
    )

    @admin.display(
        description="Country",
        ordering="region__country__name",
    )
    def country(self, obj):
        return obj.region.country