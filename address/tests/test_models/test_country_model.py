import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from address.models import Country


pytestmark = pytest.mark.django_db


def test_create_country():
    country = Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )

    country.refresh_from_db()

    assert country.pk is not None
    assert country.iso_code == "RUS"
    assert country.name == "Russia"


def test_iso_code_is_saved_uppercase():
    country = Country.objects.create(
        iso_code="rus",
        name="Russia",
    )

    country.refresh_from_db()

    assert country.iso_code == "RUS"


def test_iso_code_is_stripped_and_saved_uppercase():
    country = Country.objects.create(
        iso_code=" rus ",
        name="Russia",
    )

    assert country.iso_code == "RUS"


def test_iso_code_with_two_characters_is_invalid():
    country = Country(
        iso_code="AA",
        name="Invalid country",
    )

    with pytest.raises(ValidationError) as exc_info:
        country.full_clean()

    assert "iso_code" in exc_info.value.message_dict


def test_iso_code_with_four_characters_is_invalid():
    country = Country(
        iso_code="RUSS",
        name="Invalid country",
    )

    with pytest.raises(ValidationError) as exc_info:
        country.full_clean()

    assert "iso_code" in exc_info.value.message_dict


def test_iso_code_with_digits_is_invalid():
    country = Country(
        iso_code="RU1",
        name="Invalid country",
    )

    with pytest.raises(ValidationError) as exc_info:
        country.full_clean()

    assert "iso_code" in exc_info.value.message_dict


def test_country_name_must_be_unique():
    Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Country.objects.create(
                iso_code="USA",
                name="Russia",
            )


def test_country_iso_code_must_be_unique_after_normalization():
    Country.objects.create(
        iso_code="rus",
        name="Russia",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Country.objects.create(
                iso_code="RUS",
                name="Russian Federation",
            )


def test_country_string_representation():
    country = Country.objects.create(
        iso_code="RUS",
        name="Russia",
    )

    assert str(country) == "Russia"