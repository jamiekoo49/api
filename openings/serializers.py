from rest_framework import serializers

from .models import Applicant, Opening


class OpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opening
        fields = [
            "id",
            "posted_by",
            "description",
            "sport",
            "positions",
            "gpa",
            "is_gpa_weighted",
            "sat",
            "act",
            "min_budget",
            "max_budget",
            "grad_year",
            "created_at",
            "updated_at",
            "exam_scores",
        ]
        read_only_fields = ["id", "posted_by", "created_at", "updated_at"]


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = [
            "id",
            "opening",
            "athlete",
            "applied_at",
            "is_new",
            "status",
            "status_updated_at",
        ]
