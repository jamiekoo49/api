from django.urls import path

from .views import ApplicantListView, OpeningDetailView, OpeningView

urlpatterns = [
    path("<int:id>/", OpeningDetailView.as_view(), name="opening-detail"),
    path("", OpeningView.as_view(), name="opening"),
    path("my-applications/", ApplicantListView.as_view(), name="applicant-list"),
]
