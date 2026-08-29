import pytest

from django.urls import reverse

from address.models import Country, Region

pytestmark = pytest.mark.django_db


def test_get_list_of_regions_for_country(
    api_client,
    country_data,
    regions_data
):
    url = reverse(
        "regions",
        kwargs={"country_id":country_data.pk}
    )
    response = api_client.get(
        url
    )

    assert response.status_code == 200
    assert len(response.data) == 3


def test_admin_can_create_one_region(
    authenticated_admin_user,
    country_data
):
    url = reverse(
        "regions",
        kwargs={"country_id":country_data.pk}
    )
    payload = {
        "regions": [
            {
                "country": country_data.pk,
                "name": "Region N",
                "code": "REGN"
            }
        ]
    }

    response = authenticated_admin_user.post(
        url,
        payload,
        format="json"
    )

    assert response.status_code == 201
    assert response.data["created_count"] == 1


def test_admin_can_create_several_region(
    authenticated_admin_user,
    country_data
):
    url = reverse(
        "regions",
        kwargs={"country_id":country_data.pk}
    )
    payload = {
        "regions": [
            {
                "country": country_data.pk,
                "name": "Region 1",
                "code": "REG1"
            },
            {
                "country": country_data.pk,
                "name": "Region 2",
                "code": "REG2"
            },
            {
                "country": country_data.pk,
                "name": "Region 3",
                "code": "REG3"
            }
        ]
    }

    response = authenticated_admin_user.post(
        url,
        payload,
        format="json"
    )

    assert response.status_code == 201
    assert response.data["created_count"] == 3


def test_admin_can_not_create_several_region_with_same_name_in_one_country(
    authenticated_admin_user,
    country_data
):
    url = reverse(
        "regions",
        kwargs={"country_id":country_data.pk}
    )
    payload = {
        "regions": [
            {
                "country": country_data.pk,
                "name": "Region 1",
                "code": "REG1"
            },
            {
                "country": country_data.pk,
                "name": "Region 1",
                "code": "REG2"
            },
            {
                "country": country_data.pk,
                "name": "Region 3",
                "code": "REG3"
            }
        ]
    }

    response = authenticated_admin_user.post(
        url,
        payload,
        format="json"
    )

    assert response.status_code == 201
    assert response.data["created_count"] == 2


def test_admin_can_not_create_several_region_with_same_code_in_one_country(
    authenticated_admin_user,
    country_data
):
    url = reverse(
        "regions",
        kwargs={"country_id":country_data.pk}
    )
    payload = {
        "regions": [
            {
                "country": country_data.pk,
                "name": "Region 1",
                "code": "REG1"
            },
            {
                "country": country_data.pk,
                "name": "Region 2",
                "code": "REG1"
            },
            {
                "country": country_data.pk,
                "name": "Region 3",
                "code": "REG3"
            }
        ]
    }

    response = authenticated_admin_user.post(
        url,
        payload,
        format="json"
    )

    assert response.status_code == 201
    assert response.data["created_count"] == 2


def test_admin_can_create_regions_with_same_name_in_different_countries(
    authenticated_admin_user,
    countries_data,
):
    country_1, country_2, _ = countries_data

    url_1 = reverse(
        "regions",
        kwargs={"country_id": country_1.pk},
    )
    url_2 = reverse(
        "regions",
        kwargs={"country_id": country_2.pk},
    )

    payload_1 = {
        "regions": [
            {
                "country": country_1.pk,
                "name": "Region 1",
                "code": "REG1",
            },
        ]
    }

    payload_2 = {
        "regions": [
            {
                "country": country_2.pk,
                "name": "Region 1",
                "code": "REG1",
            },
        ]
    }

    response_1 = authenticated_admin_user.post(
        url_1,
        data=payload_1,
        format="json",
    )
    response_2 = authenticated_admin_user.post(
        url_2,
        data=payload_2,
        format="json",
    )

    assert response_1.status_code == 201, response_1.data
    assert response_2.status_code == 201, response_2.data

    assert Region.objects.filter(
        country=country_1,
        name="Region 1",
        code="REG1",
    ).exists()

    assert Region.objects.filter(
        country=country_2,
        name="Region 1",
        code="REG1",
    ).exists()

    assert Region.objects.filter(name="Region 1").count() == 2


def test_admin_can_delete_several_regions(
    authenticated_admin_user,
    regions_data,
    country_data
):
    region_1, region_2, region_3 = regions_data
    payload = {
        "regions_id": [region_1.pk, region_2.pk, region_3.pk]
    }

    url = reverse(
        "regions",
        kwargs={"country_id": country_data.pk}
    )

    response = authenticated_admin_user.delete(
        url,
        payload,
        format = "json"
    )

    assert response.status_code == 204
    assert len(Region.objects.all()) == 0


def test_admin_delete_non_existing_regions(
    authenticated_admin_user,
    country_data
):
    payload = {
        "regions_id": [999]
    }

    url = reverse(
        "regions",
        kwargs={"country_id": country_data.pk}
    )

    response = authenticated_admin_user.delete(
        url,
        payload,
        format = "json"
    )

    assert response.status_code == 204


def test_anonymous_user_cannot_update_region(
    api_client, 
    region_data
):
    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = api_client.patch(
        url,
        data={
            "name": "Updated region",
        },
        format="json",
    )

    assert response.status_code in (401, 403)

    region_data.refresh_from_db()

    assert region_data.name == "Region 1"
    assert region_data.code == "RUS-REG1"


def test_regular_user_cannot_update_region(
    authenticated_user,
    region_data,
):
    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = authenticated_user.patch(
        url,
        data={
            "name": "Updated region",
        },
        format="json",
    )

    assert response.status_code == 403

    region_data.refresh_from_db()

    assert region_data.name == "Region 1"
    assert region_data.code == "RUS-REG1"


def test_admin_can_update_all_region_fields(
    authenticated_admin_user,
    region_data,
):
    another_country = Country.objects.create(
        iso_code = "AAA",
        name = "aaa"
    )

    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "country": another_country.pk,
            "name": "SUKA",
            "code": "KAK",
        },
        format="json",
    )

    assert response.status_code == 200, response.data

    region_data.refresh_from_db()

    assert region_data.country == another_country
    assert region_data.name == "SUKA"
    assert region_data.code == "AAA-KAK"


def test_admin_gets_404_when_updating_nonexistent_region(
    authenticated_admin_user,
):
    url = reverse(
        "region-detail",
        kwargs={"region_id": 999},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "name": "Does not exist",
        },
        format="json",
    )

    assert response.status_code == 404


def test_admin_cannot_update_region_to_invalid_country(
    authenticated_admin_user,
    region_data,
):
    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "country": 999,
        },
        format="json",
    )

    assert response.status_code == 400, response.data
    assert "country" in response.data

    region_data.refresh_from_db()

    assert region_data.country.iso_code == "RUS"


def test_admin_cannot_update_region_to_duplicate_name_in_same_country(
    authenticated_admin_user,
    country_data,
    region_data,
):
    Region.objects.create(
        country=country_data,
        name="Another region",
        code="RUS-02",
    )

    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "name": "Another region",
        },
        format="json",
    )

    assert response.status_code == 400, response.data

    region_data.refresh_from_db()

    assert region_data.name == "Region 1"
    assert region_data.code == "RUS-REG1"


def test_admin_cannot_update_region_to_duplicate_code_in_same_country(
    authenticated_admin_user,
    country_data,
    region_data,
):
    Region.objects.create(
        country=country_data,
        name="Another region",
        code="RUS-02",
    )

    url = reverse(
        "region-detail",
        kwargs={"region_id": region_data.pk},
    )

    response = authenticated_admin_user.patch(
        url,
        data={
            "code": "RUS-02",
        },
        format="json",
    )

    assert response.status_code == 400, response.data

    region_data.refresh_from_db()

    assert region_data.name == "Region 1"
    assert region_data.code == "RUS-REG1"
