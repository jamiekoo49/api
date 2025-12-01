import uuid

from django.db import models


class Highschool(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    address = models.ForeignKey("core.Address", null=True, blank=True, on_delete=models.SET_NULL)
    bio = models.TextField(blank=True)
    logo = models.FileField(null=True, blank=True)
    background_image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.name


class University(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    address = models.ForeignKey("core.Address", null=True, blank=True, on_delete=models.SET_NULL)
    email_domains = models.ManyToManyField("academics.UniversityEmailDomain", blank=True, related_name="universities")
    bio = models.TextField(blank=True)
    athletic_division = models.CharField(
        max_length=100,
        choices=[
            ("NCAA Division I", "NCAA Division I"),
            ("NCAA Division II", "NCAA Division II"),
            ("NCAA Division III", "NCAA Division III"),
            ("NAIA", "NAIA"),
            ("NJCAA", "NJCAA"),
            ("Other", "Other"),
        ],
    )
    acceptance_rate = models.FloatField(null=True, blank=True, help_text="Percentage (0-100)")

    logo = models.FileField(null=True, blank=True)
    background_image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.name


class UniversityEmailDomain(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.domain} ({self.university.name})"


class Exam(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    exam_type = models.CharField(
        max_length=100,
        choices=[
            ("AP", "AP"),
            ("IB", "IB"),
        ],
    )

    def __str__(self):
        return self.name


class AthleteExam(models.Model):
    athlete = models.ForeignKey("accounts.Athlete", on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField(blank=True, null=True)
    date_taken = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.athlete} - {self.exam.name} - {self.score}"
