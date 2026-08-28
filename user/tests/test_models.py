import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_create_user():
    user = User.objects.create_user(
        email="user@mail.com",
        password="pass123",
        first_name="Ivan",
        last_name="Petrov",
    )

    assert user.pk is not None
    assert user.email == "user@mail.com"
    assert user.first_name == "Ivan"
    assert user.last_name == "Petrov"

    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False

    assert user.check_password("pass123") is True
    assert user.password != "pass123"


def test_create_user_normalizes_email():
    user = User.objects.create_user(
        email="user@MAIL.COM",
        password="pass123",
    )

    assert user.email == "user@mail.com"


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="An email address is required"):
        User.objects.create_user(
            email="",
            password="pass123",
        )


def test_create_superuser():
    admin = User.objects.create_superuser(
        email="admin@mail.com",
        password="admin123",
        first_name="Admin",
        last_name="User",
    )

    assert admin.pk is not None
    assert admin.email == "admin@mail.com"

    assert admin.is_active is True
    assert admin.is_staff is True
    assert admin.is_superuser is True

    assert admin.check_password("admin123") is True
    assert admin.password != "admin123"


def test_create_superuser_requires_is_staff_true():
    with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
        User.objects.create_superuser(
            email="admin@mail.com",
            password="admin123",
            is_staff=False,
        )


def test_create_superuser_requires_is_superuser_true():
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
        User.objects.create_superuser(
            email="admin@mail.com",
            password="admin123",
            is_superuser=False,
        )


def test_user_string_representation():
    user = User.objects.create_user(
        email="user@mail.com",
        password="pass123",
    )

    assert str(user) == "user@mail.com"


def test_user_phone_defaults():
    user = User.objects.create_user(
        email="user@mail.com",
        password="pass123",
    )

    assert user.phone_number == ""
    assert user.phone_verified is False


def test_email_is_unique():
    User.objects.create_user(
        email="user@mail.com",
        password="pass123",
    )

    with pytest.raises(Exception):
        User.objects.create_user(
            email="user@mail.com",
            password="another-pass",
        )