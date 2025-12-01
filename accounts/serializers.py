from django.contrib.auth import get_user_model
from rest_framework import fields, serializers
from rest_framework.serializers import ModelSerializer

from academics.serializers import (
    AthleteExamSerializer,
    HighschoolSerializer,
    UniversitySerializer,
)
from accounts.models import Athlete, Coach, NotificationToken, SavedAccount
from sports.serializers import (
    ClubSerializer,
    LeagueSerializer,
    PersonalStatisticSerializer,
    PositionSerializer,
    SportSerializer,
    SportStatisticSerializer,
)


class ValidateSearchQueryParams(serializers.Serializer):
    name = fields.RegexField("^[\u0621-\u064a\u0660-\u0669 a-zA-Z0-9]{1,30}$", required=False)


class NotificationTokenSerializer(ModelSerializer):
    account_email = serializers.EmailField(source="account.email", read_only=True)

    class Meta:
        model = NotificationToken
        fields = [
            "account_email",
            "token",
        ]
        # read_only_fields = ["account_email", "token"]


class AccountSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "avatar",
            "background_image",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "email"]


class SavedAccountResponseSerializer(ModelSerializer):
    athlete = serializers.PrimaryKeyRelatedField(read_only=True)
    coach = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SavedAccount
        fields = [
            "id",
            "athlete",
            "coach",
            "saved_at",
        ]
        read_only_fields = ["id", "athlete", "coach", "saved_at"]


class AthleteSerializer(ModelSerializer):
    sport = SportSerializer(required=False)
    position = PositionSerializer(required=False)
    clubs = ClubSerializer(many=True, required=False)
    leagues = LeagueSerializer(many=True, required=False)
    highschool = HighschoolSerializer(required=False)
    university = UniversitySerializer(required=False)
    sport_statistics = SportStatisticSerializer(source="sportstatistic_set", many=True, required=False)
    personal_statistics = PersonalStatisticSerializer(source="personalstatistic_set", many=True, required=False)
    exams = AthleteExamSerializer(source="athleteexam_set", many=True, required=False)

    class Meta:
        model = Athlete
        fields = [
            "uuid",
            "height",
            "weight",
            "sport",
            "position",
            "gpa",
            "is_gpa_weighted",
            "sat",
            "act",
            "budget",
            "highschool_grad_year",
            "highschool",
            "university",
            "clubs",
            "leagues",
            "sport_statistics",
            "personal_statistics",
            "exams",
        ]

    sensitive_fields = ["gpa", "sat", "act", "budget"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        hide_sensitive = self.context.get("hide_sensitive", False)
        if hide_sensitive:
            for field in self.sensitive_fields:
                rep.pop(field, None)
        return rep


class CoachSerializer(ModelSerializer):
    university = UniversitySerializer(required=False)

    class Meta:
        model = Coach
        fields = [
            "uuid",
            "university",
            "title",
        ]


excluded_fields = [
    "last_login",
    "is_superuser",
    "is_staff",
    "is_active",
    "date_joined",
    "password",
]


# TODO: Do not show notifications preferences to other users
class AccountResponseSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        # Get all concrete fields from the Account model, excluding specified fields
        model_fields = [
            f.name
            for f in model._meta.get_fields()
            if f.concrete and not f.many_to_many and not f.one_to_many and f.name not in excluded_fields
        ]
        # Add nested fields
        fields = model_fields + ["athlete", "coach"]
        read_only_fields = ["id", "email", "athlete", "coach"]

    athlete = AthleteSerializer()
    coach = CoachSerializer()


class AccountUpdateSerializer(ModelSerializer):
    email = serializers.EmailField(required=False)
    avatar = serializers.FileField(required=False, allow_null=True)
    background_image = serializers.FileField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    athlete = AthleteSerializer(required=False)
    coach = CoachSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "avatar",
            "background_image",
            "notify_applications_in_app",
            "notify_messages_in_app",
            "notify_profile_updates_in_app",
            "notify_profile_updates_email",
            "notify_feedback_email",
            "notify_product_updates_email",
            "first_name",
            "last_name",
            "athlete",
            "coach",
        ]
        read_only_fields = ["id", "email"]

    def update(self, instance, validated_data):
        athlete_data = validated_data.pop("athlete", None)
        coach_data = validated_data.pop("coach", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if athlete_data:
            clubs = athlete_data.pop("clubs", None)
            leagues = athlete_data.pop("leagues", None)
            athlete, _ = Athlete.objects.update_or_create(user=instance, defaults=athlete_data)
            sport_id = athlete.sport.id if athlete.sport else None
            if clubs is not None:
                if not sport_id:
                    raise serializers.ValidationError("Sport must be specified when updating clubs.")
                # Get or create clubs before setting them
                club_instances = []
                for club in clubs:
                    club["sport_id"] = sport_id
                    club_instance, _ = athlete.clubs.model.objects.get_or_create(**club)
                    club_instances.append(club_instance)
                athlete.clubs.set(club_instances)
            if leagues is not None:
                if not sport_id:
                    raise serializers.ValidationError("Sport must be specified when updating leagues.")
                league_instances = []
                for league in leagues:
                    league["sport_id"] = sport_id
                    league_instance, _ = athlete.leagues.model.objects.get_or_create(**league)
                    league_instances.append(league_instance)
                athlete.leagues.set(league_instances)
        if coach_data:
            Coach.objects.update_or_create(user=instance, defaults=coach_data)
        return instance
