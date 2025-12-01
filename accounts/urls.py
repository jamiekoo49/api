from django.urls import path

from .views import (
    AccountRetrieve,
    AccountUpdateView,
    DeleteAthleteDataView,
    NotificationAddTokenView,
    NotificationDeleteTokenView,
    SaveAccountCreateDeleteView,
    SaveAccountListView,
    SearchAccountsView,
)

urlpatterns = [
    path("notification-token/", NotificationAddTokenView.as_view(), name="account-notification-token"),
    path("notification-token/<str:token>/", NotificationDeleteTokenView.as_view(), name="account-notification-token"),
    path("<str:object>/<int:pk>", DeleteAthleteDataView.as_view(), name="account-delete-data"),
    path("<int:pk>/", AccountRetrieve.as_view(), name="account-detail"),
    path("save/<str:athlete_uuid>/", SaveAccountCreateDeleteView.as_view(), name="account-save"),
    path("save/", SaveAccountListView.as_view(), name="account-saved-list"),
    path("search/", SearchAccountsView.as_view(), name="account-search"),
    path("", AccountUpdateView.as_view(), name="account-update"),
]
