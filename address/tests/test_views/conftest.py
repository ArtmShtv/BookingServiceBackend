import pytest

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from address.models import (
    Address,
    Country,
    District,
    Region,
    Settlement,
    SettlementType,
    Street,
    StreetType,
    BuildingType,
    Building,
    Floor,
    UnitType,
    Unit
)


@pytest.fixture
def country_data():
    return Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )


@pytest.fixture
def countries_data():
    country_1 = Country.objects.create(iso_code="RUS", name="Russia")
    country_2 = Country.objects.create(iso_code="USA", name="United States")
    country_3 = Country.objects.create(iso_code="USB", name="Port")
    return country_1, country_2, country_3


@pytest.fixture
def region_data(country_data):
    return Region.objects.create(
        country=country_data,
        name="Region 1",
        code="REG1",
    )

@pytest.fixture
def regions_data(country_data):
    region_1 = Region.objects.create(
        country=country_data,
        name="Region 1",
        code="REG1",
    )
    region_2 = Region.objects.create(
        country=country_data,
        name="Region 2",
        code="REG2",
    )
    region_3 = Region.objects.create(
        country=country_data,
        name="Region 3",
        code="REG3",
    )
    return region_1, region_2, region_3


@pytest.fixture
def settlement_type_city_data():
    return SettlementType.objects.create(
        name="City",
    )


@pytest.fixture
def settlement_city_data(region_data, settlement_type_city_data):
    return Settlement.objects.create(
        name="Settlement1",
        settlement_type=settlement_type_city_data,
        region=region_data,
    )


@pytest.fixture
def district_data(settlement_city_data):
    return District.objects.create(
        name="District_1",
        settlement=settlement_city_data,
    )


@pytest.fixture
def street_type_data():
    return StreetType.objects.create(
        code="123",
        name="Street_type_1",
    )


@pytest.fixture
def street_data(district_data, street_type_data):
    return Street.objects.create(
        name="Lenina",
        street_code="ST001",
        street_type=street_type_data,
        district=district_data,
    )


@pytest.fixture
def address_data(
    country_data,
    region_data,
    settlement_city_data,
    district_data,
    street_data,
):
    return Address.objects.create(
        country=country_data,
        region=region_data,
        settlement=settlement_city_data,
        district=district_data,
        street=street_data,
        house_number="10",
        building_name="Building A",
        postal_code="123456",
        longitude="37.617300",
        latitude="55.755800",
    )


@pytest.fixture
def building_type_data():
    return BuildingType.objects.create(
        name = "Building_type_1"
    )


@pytest.fixture
def building_data(
    address_data,
    building_type_data
):
    return Building.objects.create(
        address = address_data,
        building_type = building_type_data,
        name = "Building_1",
        code = "123"
    )

@pytest.fixture
def floor_data(building_data):
    return Floor.objects.create(
        building = building_data,
        label = "Floor_1"
    )

@pytest.fixture
def unit_type_data():
    return UnitType.objects.create(
        name = "Unit_type_1"
    )

@pytest.fixture
def unit_data(unit_type_data, floor_data):
    return Unit.objects.create(
        label = "Unit_1",
        floor = floor_data,
        unit_type = unit_type_data
    )