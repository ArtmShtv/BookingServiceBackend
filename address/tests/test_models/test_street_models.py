import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from address.models import (
    Country,
    Region,
    Settlement,
    SettlementType,
    District,
    StreetType,
    Street
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
        name = "District_1",
        settlement = settlement_city_data
    )

@pytest.fixture
def districts_data(settlement_city_data):
    district_1 = District.objects.create(
        name = "District_1",
        settlement = settlement_city_data
    )
    district_2 = District.objects.create(
        name = "District_2",
        settlement = settlement_city_data
    )

    return district_1, district_2


@pytest.fixture
def street_type_data():
    return StreetType.objects.create(
        code = "123",
        name = "Street_type_1"
    )


def test_create_street_type():
    street_type = StreetType.objects.create(
        code = "123",
        name = "Street_type_1"
    )

    assert street_type.pk is not None
    assert street_type.code == "123"
    assert street_type.name == "Street_type_1"


def test_street_type_name_unique():
    street_type_1 = StreetType.objects.create(
        code = "123",
        name = "Street_type_1"
    )

    with pytest.raises(IntegrityError):
        street_type_2 = StreetType.objects.create(
            code = "1234",
            name = "Street_type_1"
        )


def test_street_type_code_unique():
    street_type_1 = StreetType.objects.create(
        code = "123",
        name = "Street_type_1"
    )

    with pytest.raises(IntegrityError):
        street_type_2 = StreetType.objects.create(
            code = "123",
            name = "Street_type_2"
        )


def test_street_type_str_method():
    street_type = StreetType.objects.create(
        code = "123",
        name = "Street_type_1"
    )

    assert str(street_type) == "Street_type_1"


def test_street_create(street_type_data, district_data):
    street = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_data
    )

    assert street.pk is not None
    assert street.name =="Street_1"
    assert street.street_code == "321"
    assert street.street_type.name == "Street_type_1"
    assert street.district.name == "District_1"


def test_street_unique_name(street_type_data, district_data):
    street_1 = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_data
    )

    with pytest.raises(IntegrityError):
        street_2 = Street.objects.create(
            name = "Street_1",
            street_code = "123",
            street_type = street_type_data,
            district = district_data
        )


def test_street_unique_code_per_district(street_type_data, district_data):
    street_1 = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_data
    )

    with pytest.raises(IntegrityError):
        street_2 = Street.objects.create(
            name = "Street_2",
            street_code = "321",
            street_type = street_type_data,
            district = district_data
        )


def test_street_unique_name_per_district(street_type_data, district_data):
    street_1 = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_data
    )

    with pytest.raises(IntegrityError):
        street_2 = Street.objects.create(
            name = "Street_1",
            street_code = "123",
            street_type = street_type_data,
            district = district_data
        )

def test_street_unique_name_per_district(street_type_data, districts_data):
    district_1, district_2 = districts_data

    street_1 = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_1
    )
    street_2 = Street.objects.create(
        name = "Street_2",
        street_code = "123",
        street_type = street_type_data,
        district = district_2
    )

    assert street_1.pk is not None
    assert street_2.pk is not None

    assert street_1.district == district_1
    assert street_2.district == district_2


def test_street_str_method(street_type_data, district_data):
    street = Street.objects.create(
        name = "Street_1",
        street_code = "321",
        street_type = street_type_data,
        district = district_data
    )

    assert str(street) == "Street_1 Street_type_1"