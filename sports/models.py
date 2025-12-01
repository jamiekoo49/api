from django.db import models

from academics.models import Highschool


class Sport(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
    )

    def __str__(self):
        return f"{self.gender.capitalize()} {self.name}"


class Club(models.Model):
    name = models.CharField(max_length=255)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PersonalStatistic(models.Model):
    athlete = models.ForeignKey("accounts.Athlete", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.athlete} - {self.name}"


class SportStatistic(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    athlete = models.ForeignKey("accounts.Athlete", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    season = models.CharField(
        max_length=20,
        choices=[
            ("spring", "Spring"),
            ("summer", "Summer"),
            ("fall", "Fall"),
            ("winter", "Winter"),
        ],
    )
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.SET_NULL)
    highschool = models.ForeignKey(Highschool, null=True, blank=True, on_delete=models.SET_NULL)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.athlete} - {self.name} ({self.sport})"


class Position(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    abbreviation = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.sport})"


class League(models.Model):
    name = models.CharField(max_length=255)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    level = models.CharField(
        max_length=100,
        choices=[
            ("youth", "Youth"),
            ("highschool", "High School"),
            ("club", "Club"),
            ("college", "College"),
            ("professional", "Professional"),
            ("other", "Other"),
        ],
        default="highschool",
    )

    def __str__(self):
        return self.name
