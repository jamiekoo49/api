from django.urls import path

from .views import (
    ConfirmCodeView,
    ConfirmForgotPasswordView,
    ForgotPasswordView,
    LoginView,
    RefreshTokenView,
    RegisterView,
    ResendCodeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("confirm/", ConfirmCodeView.as_view(), name="user-confirm"),
    path("resend/", ResendCodeView.as_view(), name="user-resend"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="user-forgot-password"),
    path("confirm-forgot-password/", ConfirmForgotPasswordView.as_view(), name="user-confirm-forgot-password"),
    path("refresh-token/", RefreshTokenView.as_view(), name="user-refresh-token"),
]
