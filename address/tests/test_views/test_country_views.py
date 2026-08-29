import pytest

from django.urls import reverse

from address.models import Country

pytestmark = pytest.mark.django_db


def test_get_list_of_countries(api_client, countries_data):
    response = api_client.get(reverse("countries"))

    assert response.status_code == 200
    assert len(response.data) == 3


def test_create_country_as_admin_user( 
    authenticated_admin_user
):
    url = reverse("countries")
    payload = {
        "iso_code": "aaa",
        "name": "aaa_country"
    }

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 1

    assert Country.objects.filter(
        iso_code = "AAA",
        name = "aaa_country"
    ).exists()


def test_create_countries_as_admin_user(
    authenticated_admin_user
):
    url = reverse("countries")
    payload = [
        {
        "iso_code": "aaa",
        "name": "aaa_country"
        },
        {
        "iso_code": "bbb",
        "name": "bbb_country"
        },
        {
        "iso_code": "ccc",
        "name": "ccc_country"
        }
    ]

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 3


def test_create_country_as_auth_user(
    authenticated_user
):
    url = reverse("countries")
    payload = {
        "iso_code": "aaa",
        "name": "aaa_country"
    }

    response = authenticated_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 403
    assert not Country.objects.filter(
        iso_code = "AAA",
        name = "aaa_country"
    ).exists()


def test_create_country_as_anon_user(
    api_client, 
):
    url = reverse("countries")
    payload = {
        "iso_code": "aaa",
        "name": "aaa_country"
    }

    response = api_client.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 401
    assert not Country.objects.filter(
        iso_code = "AAA",
        name = "aaa_country"
    ).exists()


def test_create_country_with_invalid_data_as_admin_user(
    authenticated_admin_user
):
    url = reverse("countries")
    payload = {
        "is_code": "aaa",
        "name": "aaa_country"
    }

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 400
    assert not Country.objects.filter(
        iso_code = "AAA",
        name = "aaa_country"
    ).exists()


def test_create_country_with_same_iso_code_as_admin_user(
    authenticated_admin_user,
    country_data
):
    """Attempt to create country with existing iso_code"""
    url = reverse("countries")
    payload = {
        "iso_code": country_data.iso_code,
        "name": "aaa_country"
    }

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 0

    assert Country.objects.filter(
        iso_code = "RUS",
        name = "Russia"
    ).exists()


def test_create_country_with_same_name_as_admin_user(
    authenticated_admin_user,
    country_data
):
    """Attempt to create country with existing name"""

    url = reverse("countries")
    payload = {
        "iso_code": "AAA",
        "name": country_data.name
    }

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 0

    assert Country.objects.filter(
        iso_code = "RUS",
        name = "Russia"
    ).exists()


def test_create_countries_with_same_names_as_admin_user(
    authenticated_admin_user
):
    url = reverse("countries")
    payload = [
        {
        "iso_code": "aaa",
        "name": "aaa_country"
        },
        {
        "iso_code": "bbb",
        "name": "aaa_country"
        },
        {
        "iso_code": "ccc",
        "name": "ccc_country"
        }
    ]

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 2


def test_create_countries_with_same_iso_code_as_admin_user(
    authenticated_admin_user
):
    url = reverse("countries")
    payload = [
        {
        "iso_code": "aaa",
        "name": "aaa_country"
        },
        {
        "iso_code": "aaa",
        "name": "bbb_country"
        },
        {
        "iso_code": "ccc",
        "name": "ccc_country"
        }
    ]

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 2


def test_create_countries_with_same_names_with_existing_as_admin_user(
    authenticated_admin_user,
    country_data
):
    url = reverse("countries")
    payload = [
        {
        "iso_code": "aaa",
        "name": "Russia"
        },
        {
        "iso_code": "bbb",
        "name": "bbb_country"
        },
        {
        "iso_code": "ccc",
        "name": "ccc_country"
        }
    ]

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 2


def test_create_countries_with_same_iso_codes_with_existing_as_admin_user(
    authenticated_admin_user,
    country_data
):
    url = reverse("countries")
    payload = [
        {
        "iso_code": "aaa",
        "name": "aaa_country"
        },
        {
        "iso_code": "RUS",
        "name": "bbb_country"
        },
        {
        "iso_code": "ccc",
        "name": "ccc_country"
        }
    ]

    response = authenticated_admin_user.post(
        url, data=payload, format="json"
    )

    assert response.status_code == 201

    assert response.data["created_count"] == 2


def test_anonymous_user_cannot_update_country(
    api_client, 
    country_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )
    payload = {
        "name": "Russian Federation",
    }

    response = api_client.patch(
        url,
        data=payload,
        format="json",
    )

    assert response.status_code == 401

    country_data.refresh_from_db()
    assert country_data.name == "Russia"


def test_regular_user_cannot_update_country(
    authenticated_user,
    country_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )
    payload = {
        "name": "Russian Federation",
    }

    response = authenticated_user.patch(
        url,
        data=payload,
        format="json",
    )

    assert response.status_code == 403

    country_data.refresh_from_db()
    assert country_data.name == "Russia"


def test_admin_can_update_only_country_name(
    authenticated_admin_user,
    country_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )
    payload = {
        "name": "Russian Federation",
    }

    response = authenticated_admin_user.patch(
        url,
        data=payload,
        format="json",
    )

    assert response.status_code == 200
    assert response.data == "Country updated"

    country_data.refresh_from_db()

    assert country_data.name == "Russian Federation"
    assert country_data.iso_code == "RUS"


def test_admin_can_update_only_iso_code_and_code_is_normalized(
    authenticated_admin_user,
    country_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )
    payload = {
        "iso_code": "USA",
    }

    response = authenticated_admin_user.patch(
        url,
        data=payload,
        format="json",
    )

    assert response.status_code == 200
    assert response.data == "Country updated"

    country_data.refresh_from_db()

    assert country_data.iso_code == "USA"
    assert country_data.name == "Russia"


def test_admin_can_update_country_name_and_iso_code(
    authenticated_admin_user,
    country_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )
    payload = {
        "iso_code": "deu",
        "name": "Germany",
    }

    response = authenticated_admin_user.patch(
        url,
        data=payload,
        format="json",
    )

    assert response.status_code == 200
    assert response.data == "Country updated"

    country_data.refresh_from_db()

    assert country_data.iso_code == "DEU"
    assert country_data.name == "Germany"


def test_admin_gets_404_when_updating_nonexistent_country(
    authenticated_admin_user,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": 999_999},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "name": "Does not exist",
        },
        format="json",
    )

    assert response.status_code == 404


def test_admin_cannot_update_country_to_duplicate_iso_code(
    authenticated_admin_user,
    countries_data,
):
    country_1, country_2, country_3 = countries_data

    url = reverse(
        "country-detail",
        kwargs={"country_id": country_2.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "iso_code": country_1.iso_code,
        },
        format="json",
    )

    assert response.status_code == 400

    country_2.refresh_from_db()

    assert country_2.iso_code == "USA"
    assert country_2.name == "United States"


def test_admin_cannot_update_country_to_duplicate_name(
    authenticated_admin_user,
    countries_data,
):
    country_1, country_2, country_3 = countries_data

    url = reverse(
        "country-detail",
        kwargs={"country_id": country_2.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "name": country_1.name,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "name" in response.data

    country_2.refresh_from_db()

    assert country_2.name == "United States"


def test_admin_can_delete_country(
    authenticated_admin_user,
    country_data,
):
    country_id = country_data.pk

    url = reverse(
        "country-detail",
        kwargs={"country_id": country_id},
    )

    response = authenticated_admin_user.delete(url)

    assert response.status_code == 204
    assert not Country.objects.filter(pk=country_id).exists()


def test_admin_gets_404_when_deleting_nonexistent_country(
    authenticated_admin_user,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": 999_999},
    )

    response = authenticated_admin_user.delete(url)

    assert response.status_code == 404


def test_admin_cannot_delete_country_with_regions(
    authenticated_admin_user,
    country_data,
    region_data,
):
    url = reverse(
        "country-detail",
        kwargs={"country_id": country_data.pk},
    )

    response = authenticated_admin_user.delete(url)

    assert response.status_code == 400
    assert Country.objects.filter(pk=country_data.pk).exists()