import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user = (
        User.objects
        .create_user(
            email = "user@mail.com",
            password="pass123",
            first_name = "user_first_name",
            last_name = "user_last_name",
        )
    )
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    admin_user = (
        User.objects
        .create_superuser(
            email = "admin@mail.com",
            password="admin123",
            first_name = "admin_first_name",
            last_name = "admin_last_name",
        )
    )
    return admin_user


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
