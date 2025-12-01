import pytest
from django.urls import reverse
from rest_framework import status

from accounts.models import Account


@pytest.mark.unit
@pytest.mark.django_db
class TestAccountProfileView:
    def test_retrieve_includes_athlete_profile(self, api_client, create_athlete):
        user = Account.objects.create_user(email="user@example.com", password="pass")
        athlete = create_athlete(user=user)
        url = reverse("account-detail", kwargs={"pk": user.pk})
        api_client.force_authenticate(user=user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["athlete"] is not None
        assert response.data["coach"] is None
        assert response.data["email"] == "user@example.com"
        assert response.data["athlete"]["uuid"] == str(athlete.uuid)

    def test_retrieve_includes_coach_profile(self, api_client, create_coach):
        user = Account.objects.create_user(email="user@example.com", password="pass")
        coach = create_coach(user=user)
        url = reverse("account-detail", kwargs={"pk": user.pk})
        api_client.force_authenticate(user=user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["coach"] is not None
        assert response.data["athlete"] is None
        assert response.data["email"] == "user@example.com"
        assert response.data["coach"]["uuid"] == str(coach.uuid)
