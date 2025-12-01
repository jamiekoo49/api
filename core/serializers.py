from rest_framework import serializers

from .models import Address, Country, State


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["name", "code"]


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["name", "code"]


class AddressSerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "address_one",
            "address_two",
            "postal_code",
            "state",
            "country",
        ]
