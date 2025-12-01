from rest_framework import serializers

from core.serializers import AddressSerializer

from .models import AthleteExam, Exam, Highschool, University


class HighschoolSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Highschool
        fields = [
            "uuid",
            "name",
            "address",
            "bio",
            "logo",
            "background_image",
        ]


class UniversitySerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = University
        fields = [
            "uuid",
            "name",
            "address",
            "bio",
            "athletic_division",
            "acceptance_rate",
            "logo",
            "background_image",
        ]
        read_only_fields = ["address"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "uuid",
            "name",
            "exam_type",
        ]


class AthleteExamSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = AthleteExam
        fields = [
            "id",
            "exam",
            "score",
            "date_taken",
        ]
