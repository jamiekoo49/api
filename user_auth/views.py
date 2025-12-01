import boto3
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import UniversityEmailDomain

from .serializers import (
    ConfirmCodeSerializer,
    ConfirmForgotPasswordSerializer,
    ForgotPasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResendCodeSerializer,
)

client = boto3.client("cognito-idp", region_name=settings.AWS_REGION)


class RegisterView(APIView):
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="User registered successfully"),
            400: OpenApiResponse(description="User already exists"),
            500: OpenApiResponse(description="Registration failed"),
        },
    )
    def put(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        account_type = serializer.validated_data["account_type"]
        phone = serializer.validated_data.get("phone", "")
        if account_type == "coach":
            domain = email.split("@")[-1]
            if not UniversityEmailDomain.objects.filter(domain=domain).exists():
                return Response(
                    {"error": "Email domain is not allowed for coach registration"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            client.sign_up(
                ClientId=settings.APP_CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "phone_number", "Value": phone},
                    {"Name": "custom:account_type", "Value": account_type},
                ],
            )
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        except client.exceptions.UsernameExistsException:
            # TODO: resend confirmation code logic
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmCodeView(APIView):
    permission_classes = []

    @extend_schema(
        request=ConfirmCodeSerializer,
        responses={
            200: OpenApiResponse(description="User confirmed successfully"),
            400: OpenApiResponse(description="Invalid or expired confirmation code"),
            500: OpenApiResponse(description="Confirmation failed"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ConfirmCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        try:
            client.confirm_sign_up(
                ClientId=settings.APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=code,
            )
            return Response({"message": "User confirmed successfully"}, status=status.HTTP_200_OK)
        except client.exceptions.CodeMismatchException:
            return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)
        except client.exceptions.ExpiredCodeException:
            return Response({"error": "Confirmation code expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Confirmation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendCodeView(APIView):
    permission_classes = []

    @extend_schema(
        request=ResendCodeSerializer,
        responses={
            200: OpenApiResponse(description="Confirmation code resent successfully"),
            400: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            client.resend_confirmation_code(
                ClientId=settings.APP_CLIENT_ID,
                Username=email,
            )
            return Response({"message": "Confirmation code resent successfully"}, status=status.HTTP_200_OK)
        except client.exceptions.UserNotFoundException:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Resend code failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description="Invalid credentials"),
            403: OpenApiResponse(description="User not confirmed"),
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Login failed"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            response = client.initiate_auth(
                ClientId=settings.APP_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": serializer.validated_data["email"],
                    "PASSWORD": serializer.validated_data["password"],
                },
            )
            return Response(response["AuthenticationResult"], status=status.HTTP_200_OK)
        except client.exceptions.NotAuthorizedException:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except client.exceptions.UserNotConfirmedException:
            return Response({"error": "User not confirmed"}, status=status.HTTP_403_FORBIDDEN)
        except client.exceptions.UserNotFoundException:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Login failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
    permission_classes = []

    @extend_schema(
        request=ForgotPasswordSerializer, responses={200: OpenApiResponse(description="Forgot Password endpoint")}
    )
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            client.forgot_password(
                ClientId=settings.APP_CLIENT_ID,
                Username=email,
            )
            return Response({"message": "Password reset code sent successfully"}, status=status.HTTP_200_OK)
        except client.exceptions.UserNotFoundException:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Forgot Password failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmForgotPasswordView(APIView):
    permission_classes = []

    @extend_schema(
        request=ConfirmForgotPasswordSerializer,
        responses={200: OpenApiResponse(description="Confirm Forgot Password endpoint")},
    )
    def post(self, request, *args, **kwargs):
        serializer = ConfirmForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        confirmation_code = serializer.validated_data["confirmation_code"]
        password = serializer.validated_data["password"]
        try:
            client.confirm_forgot_password(
                ClientId=settings.APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=password,
            )
            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
        except client.exceptions.UserNotFoundException:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.CodeMismatchException:
            return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)
        except client.exceptions.ExpiredCodeException:
            return Response({"error": "Confirmation code has expired"}, status=status.HTTP_400_BAD_REQUEST)
        except client.exceptions.UserNotConfirmedException:
            # TODO: handle user not confirmed case
            return Response({"error": "User not confirmed"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": f"Confirm Forgot Password failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    permission_classes = []

    @extend_schema(
        request=RefreshTokenSerializer, responses={200: OpenApiResponse(description="Refresh Token endpoint")}
    )
    def post(self, request, *args, **kwargs):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]
        try:
            response = client.initiate_auth(
                ClientId=settings.APP_CLIENT_ID,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                },
            )
            return Response(response["AuthenticationResult"], status=status.HTTP_200_OK)
        except client.exceptions.NotAuthorizedException:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        except client.exceptions.UserNotFoundException:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Refresh Token failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
