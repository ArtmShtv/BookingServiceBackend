from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from decimal import Decimal


User = get_user_model()


class Country(models.Model):
    iso_code = models.CharField(
        max_length=3, 
        unique=True, 
        help_text="ISO 3166-1 alpha-3 code (USA, RUS, etc.)"
    )
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "country"
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class Region(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="regions",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9-]+$",
                message="Use uppercase letters, digits, and hyphens only.",
            ),
        ],
        help_text="Region code in 'AAA-XX' form, where AAA-country code, XX-region letter or digit code"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "region"
        verbose_name_plural = "regions"
        constraints = [
            models.UniqueConstraint(
                fields=["country", "code"],
                name="unique_region_code_per_country",
            ),
            models.UniqueConstraint(
                fields=["country", "name"],
                name="unique_region_name_per_country",
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.country.iso_code}"


class SettlementType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "settlement type"
        verbose_name_plural = "settlement types"

    def __str__(self):
        return self.name


class Settlement(models.Model):
    name = models.CharField(max_length=255)
    settlement_type = models.ForeignKey(
        SettlementType,
        on_delete=models.PROTECT,
        related_name="settlements",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="settlements",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "settlement"
        verbose_name_plural = "settlements"
        constraints = [
            models.UniqueConstraint(
                fields=["region", "settlement_type", "name"],
                name="unique_settlement_type_name_per_region",
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.settlement_type.name}"


class District(models.Model):
    name = models.CharField(max_length=100)
    settlement = models.ForeignKey(
        to=Settlement,
        on_delete=models.PROTECT,
        related_name="districts"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "district"
        verbose_name_plural = "districts"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "settlement"],
                name="unique_district_name_per_settlement"
            ),
        ]

    def __str__(self):
        return f"{self.name}"


class StreetType(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "street type"
        verbose_name_plural = "street types"

    def __str__(self):
        return self.name


class Street(models.Model):
    name = models.CharField(max_length=255)
    street_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="official or external street identifie",
    )
    street_type = models.ForeignKey(
        StreetType,
        on_delete=models.PROTECT,
        related_name="streets",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="streets",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "street"
        verbose_name_plural = "streets"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "district"],
                name="unique_street_name_per_district",
            ),
        ]

    def __str__(self):
        return f"{self.name} {self.street_type.name}"


class Address(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    settlement = models.ForeignKey(
        Settlement,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    street = models.ForeignKey(
        Street,
        on_delete=models.PROTECT,
        related_name="addresses",
    )

    house_number = models.CharField(max_length=50)
    building_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    postal_code = models.CharField(max_length=20)

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    @property
    def coordinates(self) -> tuple[Decimal, Decimal]:
        return self.longitude, self.latitude

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "street",
                    "house_number",
                    "building_name",
                ],
                name="unique_address_per_street",
            ),
        ]

    def __str__(self):
        parts = [
            self.street.name,
            self.house_number,
        ]

        if self.building_name:
            parts.append(self.building_name)

        parts.extend([
            self.settlement.name,
            self.postal_code,
        ])

        return ", ".join(parts)


class BuildingType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "building type"
        verbose_name_plural = "building types"

    def __str__(self):
        return f"{self.name}"


class Building(models.Model):
    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="buildings",
    )
    building_type = models.ForeignKey(
        BuildingType,
        on_delete=models.PROTECT,
        related_name="buildings",
    )
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["address", "code", "name"]
        verbose_name = "building"
        verbose_name_plural = "buildings"
        constraints = [
            models.UniqueConstraint(
                fields=["address", "code"],
                name="unique_building_code_per_address",
            ),
        ]

    def __str__(self):
        label = self.name or self.code or self.building_type.name
        return f"{label} at {self.address}"


class Floor(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="floors",
    )
    label = models.CharField(
        max_length=10,
        help_text="Floor label (1, 2, G, B1, etc.)",
    )

    class Meta:
        verbose_name = "floor"
        verbose_name_plural = "floors"
        constraints = [
            models.UniqueConstraint(
                fields=["building", "label"],
                name="unique_floor_number_per_building",
            ),
        ]

    def __str__(self):
        return f"{self.building.name} — floor {self.label}"


class UnitType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "unit_type"
        verbose_name_plural = "unit_types"

    def __str__(self):
        return f"{self.name}"


class Unit(models.Model):
    label = models.CharField(max_length=100)
    floor = models.ForeignKey(
        to=Floor,
        on_delete=models.CASCADE,
        related_name="units"
    )
    unit_type = models.ForeignKey(
        to=UnitType,
        on_delete=models.PROTECT,
        related_name="units"
    )

    # add in future
    # image = review = models.ForeignKey(to=UnitImage, on_delete=models.CASCADE, related_name="units")
    # review = models.ForeignKey(to=Review, on_delete=models.CASCADE, related_name="units")
    # schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE, related_name="units")

    class Meta:
        verbose_name = "unit"
        verbose_name_plural = "units"
        constraints = [
            models.UniqueConstraint(
                fields=["floor", "label"],
                name="unique_label_per_floor",
            ),
        ]


# class UnitImage(models.Model):
#     unit = models.ForeignKey(
#         Unit,
#         on_delete=models.CASCADE,
#         related_name="images",
#     )
#     image = models.ImageField(upload_to="units/")
#     caption = models.CharField(max_length=255, blank=True)
#     is_primary = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)


# class Review(models.Model):
#     unit = models.ForeignKey(
#         Unit,
#         on_delete=models.CASCADE,
#         related_name="reviews",
#     )
#     text = models.TextField()
#     rating = models.PositiveSmallIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)