import pytest

from academics.models import University
from accounts.models import Account, Coach


@pytest.mark.unit
@pytest.mark.django_db
class TestCoachModel:
    def test_str_returns_user_and_university(self):
        user = Account.objects.create_user(email="coach@example.com", password="pass")
        university = University.objects.create(name="Test U")
        coach = Coach.objects.create(user=user, university=university, title="Assistant Coach")
        assert str(user) in str(coach)
        assert "Test U" in str(coach)
