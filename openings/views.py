from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth.permissions import AllowAthlete, AllowCoach, AllowSameUniversity

from .models import Applicant, Opening
from .serializers import ApplicantSerializer, OpeningSerializer


class OpeningView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), AllowCoach()]
        return [IsAuthenticated()]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="List of openings retrieved successfully"),
        },
    )
    def get(self, request, *args, **kwargs):
        openings = Opening.objects.all()
        serializer = OpeningSerializer(openings, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OpeningSerializer,
        responses={
            201: OpenApiResponse(description="Opening created successfully"),
            400: OpenApiResponse(description="Invalid data"),
            500: OpenApiResponse(description="Creation failed"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = OpeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        opening = Opening.objects.create(
            posted_by=request.user.coach,
            description=validated_data["description"],
            sport=validated_data["sport"],
            gpa=validated_data["gpa"],
            is_gpa_weighted=validated_data["is_gpa_weighted"],
            sat=validated_data["sat"],
            act=validated_data["act"],
            min_budget=validated_data["min_budget"],
            max_budget=validated_data["max_budget"],
            grad_year=validated_data["grad_year"],
        )
        opening.positions.set(validated_data["positions"])
        opening.exam_scores.set(validated_data["exam_scores"])
        return Response(serializer.data, status=201)


class OpeningDetailView(APIView):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Opening retrieved successfully"),
            404: OpenApiResponse(description="Opening not found"),
        },
    )
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        opening_id = kwargs.get("id")
        try:
            opening = Opening.objects.get(id=opening_id)
        except Opening.DoesNotExist:
            return Response({"detail": "Opening not found"}, status=404)
        serializer = OpeningSerializer(opening)
        return Response(serializer.data, status=200)

    @extend_schema(
        request=OpeningSerializer,
        responses={
            200: OpenApiResponse(description="Opening updated successfully"),
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Opening not found"),
        },
    )
    @permission_classes([IsAuthenticated, AllowCoach, AllowSameUniversity])
    def patch(self, request, *args, **kwargs):
        opening_id = kwargs.get("id")
        try:
            opening = Opening.objects.get(id=opening_id)
        except Opening.DoesNotExist:
            return Response({"detail": "Opening not found"}, status=404)
        serializer = OpeningSerializer(opening, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="Applied successfully"),
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Opening not found"),
        },
        summary="Apply to an opening",
    )
    @permission_classes([IsAuthenticated, AllowAthlete])
    def post(self, request, *args, **kwargs):
        opening_id = kwargs.get("id")
        opening = get_object_or_404(Opening, id=opening_id)
        Applicant.objects.create(opening=opening, athlete=request.user.athlete)
        # Logic for applying to the opening goes here
        return Response({"detail": "Applied successfully"}, status=200)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Opening deleted successfully"),
            404: OpenApiResponse(description="Opening not found"),
        },
    )
    @permission_classes([IsAuthenticated, AllowCoach, AllowSameUniversity])
    def delete(self, request, *args, **kwargs):
        opening_id = kwargs.get("id")
        try:
            opening = Opening.objects.get(id=opening_id)
        except Opening.DoesNotExist:
            return Response({"detail": "Opening not found"}, status=404)
        opening.delete()
        return Response(status=204)


class ApplicantListView(generics.ListAPIView):
    # TODO: Only allow authenticated coaches to view applicants for their openings.
    serializer_class = ApplicantSerializer

    def get_queryset(self):
        athlete_id = self.request.query_params.get("athlete_id")
        if athlete_id:
            return Applicant.objects.filter(athlete_id=athlete_id)
        return Applicant.objects.none()
