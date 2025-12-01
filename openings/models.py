from django.db import models


class Opening(models.Model):
    posted_by = models.ForeignKey("accounts.Coach", on_delete=models.CASCADE)
    description = models.TextField()
    sport = models.ForeignKey("sports.Sport", on_delete=models.CASCADE)
    positions = models.ManyToManyField("sports.Position", blank=True)

    gpa = models.FloatField(null=True, blank=True)
    is_gpa_weighted = models.BooleanField(default=False)
    sat = models.PositiveIntegerField(null=True, blank=True)
    act = models.PositiveIntegerField(null=True, blank=True)
    min_budget = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum Yearly School Budget in USD")
    max_budget = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum Yearly School Budget in USD")
    grad_year = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    exam_scores = models.ManyToManyField(
        "academics.Exam",
        through="OpeningExamScore",
        through_fields=("opening", "exam"),
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.sport.__str__() if self.sport else 'No Sport'} opening by "
            f"{self.posted_by if self.posted_by else 'No Coach'} at "
            f"{self.posted_by.university.name if self.posted_by.university else 'No University'}"
        )


class OpeningExamScore(models.Model):
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    exam = models.ForeignKey("academics.Exam", on_delete=models.CASCADE)
    min_score = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.opening.__str__()} opening - {self.exam.name}"


class Applicant(models.Model):
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    athlete = models.ForeignKey("accounts.Athlete", on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("reviewed", "Reviewed"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    status_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.athlete} applied to {self.opening}"

    class Meta:
        unique_together = ("opening", "athlete")
