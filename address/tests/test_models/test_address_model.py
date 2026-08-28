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


def test_create_address(address_data):
    assert address_data.pk is not None
    assert address_data.house_number == "10"
    assert address_data.building_name == "Building A"
    assert address_data.postal_code == "123456"
    assert address_data.longitude == "37.617300"
    assert address_data.latitude == "55.755800"


def test_coordinate_property(address_data):
    assert address_data.coordinates == (
        address_data.longitude,
        address_data.latitude,
    )


def test_address_str_with_building_name(address_data):
    assert str(address_data) == (
        "Lenina, 10, Building A, Settlement1, 123456"
    )


def test_address_str_without_building_name(
    country_data,
    region_data,
    settlement_city_data,
    district_data,
    street_data,
):
    address = Address.objects.create(
        country=country_data,
        region=region_data,
        settlement=settlement_city_data,
        district=district_data,
        street=street_data,
        house_number="20",
        postal_code="654321",
        longitude="37.617300",
        latitude="55.755800",
    )

    assert str(address) == (
        "Lenina, 20, Settlement1, 654321"
    )


def test_address_is_unique_per_street(address_data):
    with pytest.raises(IntegrityError):
        Address.objects.create(
            country=address_data.country,
            region=address_data.region,
            settlement=address_data.settlement,
            district=address_data.district,
            street=address_data.street,
            house_number=address_data.house_number,
            building_name=address_data.building_name,
            postal_code="999999",
            longitude="40.000000",
            latitude="50.000000",
        )


def test_different_buildings_are_allowed_on_same_house(
    address_data,
):
    address = Address.objects.create(
        country=address_data.country,
        region=address_data.region,
        settlement=address_data.settlement,
        district=address_data.district,
        street=address_data.street,
        house_number=address_data.house_number,
        building_name="Building B",
        postal_code=address_data.postal_code,
        longitude=address_data.longitude,
        latitude=address_data.latitude,
    )

    assert address.pk is not None


def test_different_house_numbers_are_allowed(
    address_data,
):
    address = Address.objects.create(
        country=address_data.country,
        region=address_data.region,
        settlement=address_data.settlement,
        district=address_data.district,
        street=address_data.street,
        house_number="11",
        building_name=address_data.building_name,
        postal_code=address_data.postal_code,
        longitude=address_data.longitude,
        latitude=address_data.latitude,
    )

    assert address.pk is not None


def test_country_cannot_be_deleted(address_data):
    with pytest.raises(ProtectedError):
        address_data.country.delete()


def test_region_cannot_be_deleted(address_data):
    with pytest.raises(ProtectedError):
        address_data.region.delete()


def test_settlement_cannot_be_deleted(address_data):
    with pytest.raises(ProtectedError):
        address_data.settlement.delete()


def test_district_cannot_be_deleted(address_data):
    with pytest.raises(ProtectedError):
        address_data.district.delete()


def test_street_cannot_be_deleted(address_data):
    with pytest.raises(ProtectedError):
        address_data.street.delete()