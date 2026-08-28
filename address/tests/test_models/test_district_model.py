import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from address.models import (
    Country,
    Region,
    Settlement,
    SettlementType,
    District,
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
def settlement_type_village_data():
    return SettlementType.objects.create(
        name="Village",
    )

@pytest.fixture
def settlement_city_data(region_data, settlement_type_city_data):
    return Settlement.objects.create(
        name="Settlement1",
        settlement_type=settlement_type_city_data,
        region=region_data,
    )

@pytest.fixture
def settlement_village_data(region_data, settlement_type_village_data):
    return Settlement.objects.create(
        name="Settlement2",
        settlement_type=settlement_type_village_data,
        region=region_data,
    )


def test_create_district(settlement_city_data):
    district = District.objects.create(
        name="District 1",
        settlement=settlement_city_data,
    )

    assert district.pk is not None
    assert district.name == "District 1"
    assert district.settlement == settlement_city_data


def test_str_returns_name(settlement_city_data):
    district = District.objects.create(
        name="District 1",
        settlement=settlement_city_data,
    )

    assert str(district) == "District 1"


def test_districts_are_ordered_by_name(settlement_city_data):
    District.objects.create(
        name="Zeta",
        settlement=settlement_city_data,
    )
    District.objects.create(
        name="Alpha",
        settlement=settlement_city_data,
    )
    District.objects.create(
        name="Beta",
        settlement=settlement_city_data,
    )

    districts = list(District.objects.values_list("name", flat=True))

    assert districts == [
        "Alpha",
        "Beta",
        "Zeta",
    ]


def test_district_name_must_be_unique_within_settlement(settlement_city_data):
    District.objects.create(
        name="Central",
        settlement=settlement_city_data,
    )

    with pytest.raises(IntegrityError):
        District.objects.create(
            name="Central",
            settlement=settlement_city_data,
        )


def test_same_district_name_is_allowed_in_different_settlements(
    settlement_city_data, 
    settlement_village_data
):
    district_1 = District.objects.create(
        name="Central",
        settlement=settlement_city_data,
    )
    district_2 = District.objects.create(
        name="Central",
        settlement=settlement_village_data,
    )

    assert district_1.pk != district_2.pk


def test_settlement_cannot_be_deleted_if_it_has_districts(settlement_city_data):
    District.objects.create(
        name="Central",
        settlement=settlement_city_data,
    )

    with pytest.raises(ProtectedError):
        settlement_city_data.delete()