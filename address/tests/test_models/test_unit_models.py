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


def test_create_unit_type(unit_type_data):
    assert unit_type_data.pk is not None


def test_unit_type_unique_name(unit_type_data):
    with pytest.raises(IntegrityError):
        UnitType.objects.create(
            name = unit_type_data.name
        )


def test_unit_type_str_method(unit_type_data):
    assert str(unit_type_data) == "Unit_type_1"


def test_unit_create(unit_data):
    assert unit_data.pk is not None


def test_unit_label_unique_per_floor(unit_data):
    with pytest.raises(IntegrityError):
        Unit.objects.create(
            label = unit_data.label,
            floor = unit_data.floor,
            unit_type = unit_data.unit_type
        )


def test_unit_delete_with_floor(building_data, unit_type_data):
    floor = Floor.objects.create(
        building=building_data,
        label="Floor_1",
    )

    unit = Unit.objects.create(
        label="AAA",
        floor=floor,
        unit_type=unit_type_data,
    )

    unit_id = unit.pk

    floor.delete()

    assert not Unit.objects.filter(pk=unit_id).exists()


def test_deleting_floor_does_not_delete_units_on_other_floors(
    building_data,
    unit_type_data,
):
    floor_1 = Floor.objects.create(
        building=building_data,
        label="Floor_1",
    )
    floor_2 = Floor.objects.create(
        building=building_data,
        label="Floor_2",
    )

    unit_1 = Unit.objects.create(
        label="AAA",
        floor=floor_1,
        unit_type=unit_type_data,
    )
    unit_2 = Unit.objects.create(
        label="BBB",
        floor=floor_2,
        unit_type=unit_type_data,
    )

    floor_1.delete()

    assert not Unit.objects.filter(pk=unit_1.pk).exists()
    assert Unit.objects.filter(pk=unit_2.pk).exists()


def test_unit_type_cannot_be_deleted_with_units(
    building_data,
    unit_type_data,
):
    floor = Floor.objects.create(
        building=building_data,
        label="Floor_1",
    )
    unit = Unit.objects.create(
        label="AAA",
        floor=floor,
        unit_type=unit_type_data,
    )

    with pytest.raises(ProtectedError):
        unit_type_data.delete()


def test_unit_type_can_be_deleted_without_units(
    building_data,
    unit_type_data,
):
    floor = Floor.objects.create(
        building=building_data,
        label="Floor_1",
    )

    unit = Unit.objects.create(
        label="AAA",
        floor=floor,
        unit_type=unit_type_data,
    )

    unit.delete()
    unit_type_id = unit_type_data.pk

    unit_type_data.delete()

    assert not UnitType.objects.filter(pk=unit_type_id).exists()