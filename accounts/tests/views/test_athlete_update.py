import pytest
from django.urls import reverse
from rest_framework import status

from academics.models import AthleteExam, Exam
from sports.models import Club, League, PersonalStatistic, Sport, SportStatistic


@pytest.mark.unit
@pytest.mark.django_db
class TestAccountProfileView:
    def test_add_and_delete_exam(self, api_client, create_athlete):
        athlete = create_athlete(email="exam@example.com", password="pass")
        exam = Exam.objects.create(name="SAT", exam_type="AP")
        athlete_exam = AthleteExam.objects.create(athlete=athlete, exam=exam, score=1500)
        assert AthleteExam.objects.filter(pk=athlete_exam.pk).exists()
        url = reverse("account-delete-data", kwargs={"object": "athleteexam", "pk": athlete_exam.pk})
        api_client.force_authenticate(user=athlete.user)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not AthleteExam.objects.filter(pk=athlete_exam.pk).exists()

    def test_add_and_delete_club(self, api_client, create_athlete):
        athlete = create_athlete(email="club@example.com", password="pass")
        sport = Sport.objects.create(name="Chess", gender="male")
        club = Club.objects.create(name="Chess Club", sport=sport)
        athlete.clubs.add(club)
        assert club in athlete.clubs.all()
        url = reverse("account-delete-data", kwargs={"object": "clubs", "pk": club.pk})
        api_client.force_authenticate(user=athlete.user)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert club not in athlete.clubs.all()

    def test_add_and_delete_league(self, api_client, create_athlete):
        sport = Sport.objects.create(name="Soccer", gender="male")
        athlete = create_athlete(email="league@example.com", password="pass")
        league = League.objects.create(name="Premier League", sport=sport)
        athlete.leagues.add(league)
        assert league in athlete.leagues.all()
        url = reverse("account-delete-data", kwargs={"object": "leagues", "pk": league.pk})
        api_client.force_authenticate(user=athlete.user)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert league not in athlete.leagues.all()

    def test_add_and_delete_personal_statistic(self, api_client, create_athlete):
        athlete = create_athlete(email="stat@example.com", password="pass")
        stat = PersonalStatistic.objects.create(athlete=athlete, name="Bench Press", value="200lbs")
        assert PersonalStatistic.objects.filter(pk=stat.pk).exists()
        url = reverse("account-delete-data", kwargs={"object": "personalstatistic", "pk": stat.pk})
        api_client.force_authenticate(user=athlete.user)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not PersonalStatistic.objects.filter(pk=stat.pk).exists()

    def test_add_and_delete_sport_statistic(self, api_client, create_athlete):
        sport = Sport.objects.create(name="Basketball", gender="male")
        athlete = create_athlete(email="sportstat@example.com", password="pass")
        stat = SportStatistic.objects.create(
            athlete=athlete, sport=sport, name="Points", year=2025, season="fall", value="100"
        )
        assert SportStatistic.objects.filter(pk=stat.pk).exists()
        url = reverse("account-delete-data", kwargs={"object": "sportstatistic", "pk": stat.pk})
        api_client.force_authenticate(user=athlete.user)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not SportStatistic.objects.filter(pk=stat.pk).exists()
