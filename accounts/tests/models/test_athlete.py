import pytest

from accounts.models import Account, Athlete


@pytest.mark.unit
@pytest.mark.django_db
class TestAthleteModel:
    def test_str_returns_user_name(self):
        user = Account.objects.create_user(email="athlete@example.com", password="pass")
        athlete = Athlete.objects.create(user=user, height=72, weight=200, highschool_grad_year=2025)
        assert str(user) in str(athlete)
