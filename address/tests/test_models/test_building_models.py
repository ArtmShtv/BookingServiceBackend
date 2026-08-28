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
    Building
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def country_data():
    return Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )


@pytest.fixture
def region_data(country_data):
    return Region.objects.create(
        country=country_data,
        name="Region 1",
        code="REG1",
    )


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


def test_building_type_unique(building_type_data):
    with pytest.raises(IntegrityError):
        BuildingType.objects.create(
            name = "Building_type_1"
        )

def test_building_type_str_method(building_type_data):
    assert str(building_type_data) == "Building_type_1"


def test_building_unique_code_per_address(building_data):
    with pytest.raises(IntegrityError):
        Building.objects.create(
            address = building_data.address,
            building_type = building_data.building_type,
            name = "Building_2",
            code = building_data.code
        )

def test_building_str_uses_name(address_data, building_type_data):
    building = Building.objects.create(
        address=address_data,
        building_type=building_type_data,
        name="Main Building",
        code="B001",
    )

    assert str(building) == f"Main Building at {address_data}"


def test_building_str_falls_back_to_code(
    address_data,
    building_type_data,
):
    building = Building.objects.create(
        address=address_data,
        building_type=building_type_data,
        name="",
        code="B001",
    )

    assert str(building) == f"B001 at {address_data}"


def test_building_str_falls_back_to_building_type(
    address_data,
    building_type_data,
):
    building = Building.objects.create(
        address=address_data,
        building_type=building_type_data,
        name="",
        code="",
    )

    assert str(building) == (
        f"{building_type_data.name} at {address_data}"
    )


def test_address_cannot_be_deleted_with_buildings(building_type_data, address_data):
    building = Building.objects.create(
        address = address_data,
        building_type = building_type_data,
        name = "aaa",
        code = "aaa"
    )
    with pytest.raises(ProtectedError):
        address_data.delete()


def test_building_type_cannot_be_deleted_with_buildings(building_type_data, address_data):
    building = Building.objects.create(
        address = address_data,
        building_type = building_type_data,
        name = "aaa",
        code = "aaa"
    )
    with pytest.raises(ProtectedError):
        building_type_data.delete()