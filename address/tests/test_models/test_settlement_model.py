import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from address.models import (
    Country, 
    Region, 
    Settlement,
    SettlementType
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def country():
    return Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )


@pytest.fixture
def region(country):
    return Region.objects.create(
        country=country,
        name="Saint Petersburg",
        code="RUS-SPE",
    )


@pytest.fixture
def another_region(country):
    return Region.objects.create(
        country=country,
        name="Moscow",
        code="RUS-MOW",
    )


@pytest.fixture
def city_type():
    return SettlementType.objects.create(
        name="City",
    )


@pytest.fixture
def village_type():
    return SettlementType.objects.create(
        name="Village",
    )


def test_create_settlement(region, city_type):
    settlement = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    assert settlement.pk is not None
    assert settlement.name == "Saint Petersburg"
    assert settlement.region == region
    assert settlement.settlement_type == city_type


def test_settlement_string_representation(region, city_type):
    settlement = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    assert str(settlement) == "Saint Petersburg, City"


def test_region_has_related_settlements(region, city_type):
    settlement_1 = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )
    settlement_2 = Settlement.objects.create(
        name="Pushkin",
        settlement_type=city_type,
        region=region,
    )

    assert region.settlements.count() == 2
    assert settlement_1 in region.settlements.all()
    assert settlement_2 in region.settlements.all()


def test_settlement_type_has_related_settlements(region, city_type):
    settlement = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    assert city_type.settlements.count() == 1
    assert settlement in city_type.settlements.all()


def test_same_name_and_type_cannot_exist_twice_in_same_region(
    region,
    city_type,
):
    Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=region,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Settlement.objects.create(
                name="Central",
                settlement_type=city_type,
                region=region,
            )


def test_same_name_with_different_types_can_exist_in_same_region(
    region,
    city_type,
    village_type,
):
    city = Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=region,
    )
    village = Settlement.objects.create(
        name="Central",
        settlement_type=village_type,
        region=region,
    )

    assert city.pk is not None
    assert village.pk is not None
    assert city.name == village.name == "Central"
    assert city.region == village.region == region
    assert city.settlement_type != village.settlement_type


def test_same_name_and_type_can_exist_in_different_regions(
    region,
    another_region,
    city_type,
):
    first_settlement = Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=region,
    )
    second_settlement = Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=another_region,
    )

    assert first_settlement.pk is not None
    assert second_settlement.pk is not None

    assert first_settlement.name == second_settlement.name == "Central"
    assert first_settlement.settlement_type == second_settlement.settlement_type
    assert first_settlement.region != second_settlement.region


def test_same_name_and_type_can_exist_in_different_regions(
    region,
    another_region,
    city_type,
):
    Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=region,
    )
    Settlement.objects.create(
        name="Central",
        settlement_type=city_type,
        region=another_region,
    )

    assert Settlement.objects.filter(
        name="Central",
        settlement_type=city_type,
    ).count() == 2


def test_settlements_are_ordered_by_name(region, city_type):
    Settlement.objects.create(
        name="ASettlement",
        settlement_type=city_type,
        region=region,
    )
    Settlement.objects.create(
        name="BSettlement",
        settlement_type=city_type,
        region=region,
    )
    Settlement.objects.create(
        name="BASettlement",
        settlement_type=city_type,
        region=region,
    )

    names = list(
        Settlement.objects.values_list("name", flat=True)
    )

    assert names == [
        "ASettlement",
        "BASettlement",
        "BSettlement",
    ]


def test_region_with_settlements_cannot_be_deleted(region, city_type):
    Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    with pytest.raises(ProtectedError):
        region.delete()


def test_settlement_type_with_settlements_cannot_be_deleted(
    region,
    city_type,
):
    Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    with pytest.raises(ProtectedError):
        city_type.delete()


def test_region_can_be_deleted_after_its_settlements_are_deleted(
    region,
    city_type,
):
    settlement = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    region_id = region.pk
    settlement_id = settlement.pk

    settlement.delete()
    region.delete()

    assert settlement.pk is None
    assert region.pk is None

    assert not Settlement.objects.filter(pk=settlement_id).exists()
    assert not Region.objects.filter(pk=region_id).exists()


def test_settlement_type_can_be_deleted_after_its_settlements_are_deleted(
    region,
    city_type,
):
    settlement = Settlement.objects.create(
        name="Saint Petersburg",
        settlement_type=city_type,
        region=region,
    )

    settlement_type_id = city_type.pk
    settlement_id = settlement.pk

    settlement.delete()
    city_type.delete()

    assert settlement.pk is None
    assert city_type.pk is None

    assert not Settlement.objects.filter(pk=settlement_id).exists()
    assert not SettlementType.objects.filter(pk=settlement_type_id).exists()