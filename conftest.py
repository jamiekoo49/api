from typing import Optional

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(email: str, password: str, is_staff: bool = False):
        return User.objects.create_user(email=email, password=password, is_staff=is_staff)

    return _create_user


@pytest.fixture
def create_athlete(create_user):
    def _create_athlete(
        email: Optional[str] = None,
        password: Optional[str] = None,
        user=None,
        **kwargs,
    ):
        if user is None:
            if email is None or password is None:
                raise ValueError("Email and password must be provided if user is not provided")
            user = create_user(email=email, password=password)
        from accounts.models import Athlete

        athlete = Athlete.objects.create(
            user=user,
            **kwargs,
        )
        return athlete

    return _create_athlete


@pytest.fixture
def create_coach(create_user):
    def _create_coach(
        email: Optional[str] = None,
        password: Optional[str] = None,
        user=None,
        **kwargs,
    ):
        if user is None:
            if email is None or password is None:
                raise ValueError("Email and password must be provided if user is not provided")
            user = create_user(email=email, password=password)
        from accounts.models import Coach

        coach = Coach.objects.create(
            user=user,
            **kwargs,
        )
        return coach

    return _create_coach
