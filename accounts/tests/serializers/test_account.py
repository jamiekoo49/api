import pytest

from accounts.models import Account
from accounts.serializers import AccountSerializer


@pytest.mark.unit
@pytest.mark.django_db
class TestAccountSerializer:
    def test_serializer_fields(self):
        user = Account.objects.create_user(
            email="serial@example.com",
            password="pass",
            first_name="Test",
            last_name="User",
        )
        serializer = AccountSerializer(user)
        data = serializer.data
        assert data["email"] == "serial@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert "avatar" in data
        assert "background_image" in data
