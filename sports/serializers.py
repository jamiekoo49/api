from rest_framework import serializers

from academics.serializers import HighschoolSerializer

from .models import Club, League, PersonalStatistic, Position, Sport, SportStatistic


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "name", "gender"]


class ClubSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "sport"]


class PersonalStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalStatistic
        fields = ["id", "name", "value"]


class SportStatisticSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)
    highschool = HighschoolSerializer(read_only=True)
    club = ClubSerializer(read_only=True)

    class Meta:
        model = SportStatistic
        fields = [
            "id",
            "sport",
            "name",
            "year",
            "season",
            "club",
            "highschool",
            "value",
        ]


class PositionSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)

    class Meta:
        model = Position
        fields = ["id", "sport", "abbreviation", "name"]


class LeagueSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)

    class Meta:
        model = League
        fields = ["id", "name", "sport", "level"]
