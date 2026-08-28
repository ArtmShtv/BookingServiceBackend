import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from address.models import (
    Country, 
    Region
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def country_data(db):
    country = Country.objects.create(
        iso_code = "AAA",
        name = "Country"
    )

    return country

@pytest.fixture
def countries_data(db):
    country_1 = Country.objects.create(
        iso_code = "AAA",
        name = "Country_1"
    )
    country_2 = Country.objects.create(
        iso_code = "BBB",
        name = "Country_2"
    )

    return country_1, country_2


def test_region_create(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    assert region.pk is not None
    assert region.country == country
    assert region.name == "Region 1"
    assert region.code == "AAA-REG1"


def test_region_string_representation(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    assert str(region) == "Region 1, AAA-REG1"


def test_country_has_regions_reverse_relation(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    assert country.regions.count() == 1
    assert region in country.regions.all()


def test_region_code_is_saved_uppercase(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    assert region.code == "AAA-REG1"

def test_region_code_is_stripped_and_saved_uppercase(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code=f"  reg1  ",
    )

    assert region.code == "AAA-REG1"


def test_region_code_mixed_case_is_saved_uppercase(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    assert region.code == "AAA-REG1"


def test_region_code_is_normalized_when_updated(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    region.code = f"region1"
    region.save()

    region.refresh_from_db()

    assert region.code == "AAA-REGION1"


def test_region_code_must_be_unique_within_country(country_data):
    country = country_data

    region_1 = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            region_2 = Region.objects.create(
                country=country,
                name="Region 2",
                code="REG1",
            )


def test_same_region_code_with_different_case_is_forbidden(country_data):
    country = country_data

    region_1 = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            region_2 = Region.objects.create(
                country=country,
                name="Region 2",
                code="REG1",
            )


def test_region_name_unique_within_country(country_data):
    country = country_data

    region_1 = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            region_2 = Region.objects.create(
                country=country,
                name="Region 1",
                code=f"REG2",
            )


def test_region_name_can_exist_in_different_countries(countries_data):
    country1, country2 = countries_data

    region_1 = Region.objects.create(
        country=country1,
        name="Region 1",
        code="REG1",
    )
    region_2 = Region.objects.create(
        country=country2,
        name="Region 1",
        code="REG2",
    )

    assert region_1.pk is not None
    assert region_2.pk is not None

    assert region_1.name == region_2.name == "Region 1"
    assert region_1.country == country1
    assert region_2.country == country2

    assert Region.objects.filter(
        country=country1,
        name="Region 1",
    ).exists()

    assert Region.objects.filter(
        country=country2,
        name="Region 1",
    ).exists()

    assert Region.objects.filter(name="Region 1").count() == 2


def test_same_region_code_can_exist_in_different_countries(countries_data):
    country1, country2 = countries_data

    region_1 = Region.objects.create(
        country=country1,
        name="Region 1",
        code="REG1",
    )
    region_2 = Region.objects.create(
        country=country2,
        name="Region 2",
        code="REG1",
    )

    assert region_1.pk is not None
    assert region_2.pk is not None

    assert region_1.code == "AAA-REG1"
    assert region_2.code == "BBB-REG1"


def test_region_code_valid_after_update(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    region.code = "REG2"
    region.save()

    region.refresh_from_db()

    assert region.code == "AAA-REG2"


def test_country_cannot_be_deleted_if_it_has_regions(country_data):
    country = country_data

    Region.objects.create(
        country=country,
        name="Region 1",
        code=f"{country.iso_code}-REG1",
    )

    with pytest.raises(ProtectedError):
        country.delete()


def test_country_can_be_deleted_after_its_regions_are_deleted(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="Region 1",
        code="REG1",
    )

    country_id = country.pk
    region_id = region.pk

    region.delete()
    country.delete()

    assert region.pk is None
    assert country.pk is None

    assert not Region.objects.filter(pk=region_id).exists()
    assert not Country.objects.filter(pk=country_id).exists()


def test_regions_are_ordered_by_name(country_data):
    country = country_data

    region_1 = Region.objects.create(
        country=country,
        name="ARegion",
        code="REG1",
    )
    region_2 = Region.objects.create(
        country=country,
        name="BRegion",
        code="REG2",
    )
    region_3 = Region.objects.create(
        country=country,
        name="CRegion",
        code="REG3",
    )

    regions = Region.objects.all()

    assert list(regions.values_list("name", flat=True)) == ["ARegion", "BRegion", "CRegion"]


def test_region_code_with_underscore_is_invalid(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="ARegion",
        code="_REG1",
    )

    with pytest.raises(ValidationError):
        region.full_clean()


def test_region_code_with_special_symbol_is_invalid(country_data):
    country = country_data

    region = Region.objects.create(
        country=country,
        name="ARegion",
        code="@REG1",
    )

    with pytest.raises(ValidationError):
        region.full_clean()

