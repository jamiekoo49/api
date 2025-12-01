from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account, Athlete, Coach, NotificationToken, SavedAccount
from accounts.serializers import (
    AccountResponseSerializer,
    AccountUpdateSerializer,
    AthleteSerializer,
    CoachSerializer,
    NotificationTokenSerializer,
    SavedAccountResponseSerializer,
    ValidateSearchQueryParams,
)
from user_auth.permissions import AllowCoach, AllowSelf


class NotificationAddTokenView(APIView):
    permission_classes = [IsAuthenticated, AllowSelf]

    @extend_schema(
        request=NotificationTokenSerializer,
        responses={
            200: OpenApiResponse(description="Notification token added successfully"),
            400: OpenApiResponse(description="Invalid data"),
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = NotificationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")
        NotificationToken.objects.create(account=user, token=token)
        return Response({"detail": "Notification token added successfully."}, status=status.HTTP_200_OK)


class NotificationDeleteTokenView(APIView):
    @extend_schema(
        responses={
            204: OpenApiResponse(description="Notification token deleted successfully"),
        },
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        token = kwargs.get("token")
        NotificationToken.objects.filter(account=user, token=token).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountUpdateView(APIView):
    permission_classes = [IsAuthenticated, AllowSelf]

    @extend_schema(
        request=AccountUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=AccountResponseSerializer,
            )
        },
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = AccountUpdateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AccountResponseSerializer(user).data, status=status.HTTP_200_OK)


class SaveAccountCreateDeleteView(APIView):
    permission_classes = [IsAuthenticated, AllowSelf, AllowCoach]

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=SavedAccountResponseSerializer,
            )
        },
    )
    def post(self, request, athlete_uuid, *args, **kwargs):
        user = request.user
        coach = get_object_or_404(Coach, user=user)
        athlete = get_object_or_404(Athlete, uuid=athlete_uuid)
        saved_account, created = SavedAccount.objects.get_or_create(athlete=athlete, coach=coach)
        if not created:
            return Response({"detail": "Account already saved."}, status=status.HTTP_409_CONFLICT)
        return Response(SavedAccountResponseSerializer(saved_account).data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Account unsaved successfully"),
        },
    )
    def delete(self, request, athlete_uuid, *args, **kwargs):
        user = request.user
        coach = get_object_or_404(Coach, user=user)
        athlete = get_object_or_404(Athlete, uuid=athlete_uuid)
        saved_account = get_object_or_404(SavedAccount, athlete=athlete, coach=coach)
        saved_account.delete()
        return Response({"detail": "Account unsaved successfully"}, status=status.HTTP_204_NO_CONTENT)


class SaveAccountListView(APIView):
    permission_classes = [IsAuthenticated, AllowSelf, AllowCoach]

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=AccountResponseSerializer(many=True),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        coach = get_object_or_404(Coach, user=user)
        saved_accounts = SavedAccount.objects.filter(coach=coach).select_related("athlete__user")
        athletes = [saved_account.athlete.user for saved_account in saved_accounts]
        return Response(AccountResponseSerializer(athletes, many=True).data, status=status.HTTP_200_OK)


class DeleteAthleteDataView(APIView):
    permission_classes = [IsAuthenticated, AllowSelf]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="object",
                location=OpenApiParameter.PATH,
                required=True,
                type=str,
                enum=["athleteexam", "sportstatistic", "personalstatistic", "clubs", "leagues"],
                description="Type of athlete data to delete",
            ),
        ],
        responses={
            204: OpenApiResponse(description="Athlete data deleted successfully"),
            404: OpenApiResponse(description="Athlete data not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        model = kwargs.get("object")
        pk = kwargs.get("pk")
        user = request.user
        athlete = get_object_or_404(Athlete, user=user)

        # Use correct manager for many-to-many fields
        if model in ["clubs", "leagues"]:
            manager = getattr(athlete, model)
            manager.remove(pk)
        else:
            get_object_or_404(getattr(athlete, f"{model}_set"), pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountRetrieve(APIView):
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=AccountResponseSerializer,
            ),
            404: OpenApiResponse(description="Account not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), pk=kwargs["pk"])
        response = AccountResponseSerializer(user).data
        viewer = request.user
        # Default to not hiding sensitive fields
        hide_sensitive = False
        # Try to get account_type from JWT claims (set by custom authentication)
        account_type = getattr(viewer, "account_type", None)
        # If not set as attribute, try to get from JWT payload (if available)
        if not account_type and hasattr(viewer, "jwt_claims"):
            account_type = viewer.jwt_claims.get("custom:account_type")
        # Fallback: try to infer from related models
        if not account_type:
            if hasattr(viewer, "coach") and viewer.coach is not None:
                account_type = "coach"
            elif hasattr(viewer, "athlete") and viewer.athlete is not None:
                account_type = "athlete"
        # Hide sensitive if viewer is athlete and not viewing self
        if account_type == "athlete" and viewer != user:
            hide_sensitive = True
        try:
            athlete = Athlete.objects.get(user=user)
            response["athlete"] = AthleteSerializer(athlete, context={"hide_sensitive": hide_sensitive}).data
        except Athlete.DoesNotExist:
            pass
        try:
            coach = Coach.objects.get(user=user)
            response["coach"] = CoachSerializer(coach).data
        except Coach.DoesNotExist:
            pass
        return Response(response, status=status.HTTP_200_OK)


class SearchAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Search query for account's first name or last name",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AccountResponseSerializer(many=True),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        query_params = ValidateSearchQueryParams(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        search_query = query_params.validated_data.get("name")
        print(search_query)
        if not search_query:
            return Response([], status=status.HTTP_200_OK)
        if " " in search_query:
            first_name, last_name = search_query.split(" ")
            search_result = Account.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
        else:
            # Search by first name OR last name when only one term
            search_result = Account.objects.filter(
                Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
            )
        return Response(AccountResponseSerializer(search_result, many=True).data, status=status.HTTP_200_OK)
