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
    Floor
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

@pytest.fixture
def floor_data(building_data):
    return Floor.objects.create(
        building = building_data,
        label = "Floor_1"
    )


def test_create_floor(building_data):
    floor = Floor.objects.create(
        building=building_data,
        label="1",
    )

    assert floor.pk is not None
    assert floor.building == building_data
    assert floor.label == "1"


def test_floor_str(building_data):
    floor = Floor.objects.create(
        building=building_data,
        label="1",
    )

    assert str(floor) == f"{building_data.name} — floor 1"


def test_floor_label_is_unique_per_building(building_data):
    Floor.objects.create(
        building=building_data,
        label="1",
    )

    with pytest.raises(IntegrityError):
        Floor.objects.create(
            building=building_data,
            label="1",
        )


def test_same_floor_label_allowed_for_different_buildings(
    building_data,
    address_data,
    building_type_data,
):
    another_building = Building.objects.create(
        address=address_data,
        building_type=building_type_data,
        name="Another_Building",
    )

    floor_1 = Floor.objects.create(
        building=building_data,
        label="1",
    )

    floor_2 = Floor.objects.create(
        building=another_building,
        label="1",
    )

    assert floor_1.pk != floor_2.pk


def test_deleting_building_deletes_floors(building_data):
    floor = Floor.objects.create(
        building=building_data,
        label="1",
    )

    floor_id = floor.pk

    building_data.delete()

    assert not Floor.objects.filter(pk=floor_id).exists()