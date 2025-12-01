import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from academics.models import Highschool, University
from accounts.managers import CustomUserManager
from sports.models import Position, Sport


class Account(AbstractUser):
    username = None
    password = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    avatar = models.FileField(null=True, blank=True)
    background_image = models.FileField(null=True, blank=True)

    # Notification preferences
    notify_applications_in_app = models.BooleanField(default=True)
    notify_messages_in_app = models.BooleanField(default=True)
    notify_profile_updates_in_app = models.BooleanField(default=True)
    notify_profile_updates_email = models.BooleanField(default=True)
    notify_feedback_email = models.BooleanField(default=True)
    notify_product_updates_email = models.BooleanField(default=True)

    objects = CustomUserManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email


class NotificationToken(models.Model):
    account = models.ForeignKey(Account, related_name="notification_tokens", on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.email} - {self.token}"


class Athlete(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.OneToOneField(Account, null=True, blank=True, on_delete=models.SET_NULL)

    height = models.FloatField(help_text="Height in inches", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in pounds", null=True, blank=True)

    sport = models.ForeignKey(Sport, null=True, blank=True, on_delete=models.SET_NULL)
    position = models.ForeignKey(Position, null=True, blank=True, on_delete=models.SET_NULL)

    gpa = models.FloatField(null=True, blank=True)
    is_gpa_weighted = models.BooleanField(default=False)
    sat = models.PositiveIntegerField(null=True, blank=True)
    act = models.PositiveIntegerField(null=True, blank=True)
    budget = models.PositiveIntegerField(null=True, blank=True, help_text="Yearly School Budget in USD")

    highschool_grad_year = models.PositiveIntegerField(null=True, blank=True)
    highschool = models.ForeignKey(Highschool, null=True, blank=True, on_delete=models.SET_NULL)
    university = models.ForeignKey(University, null=True, blank=True, on_delete=models.SET_NULL)

    clubs = models.ManyToManyField("sports.Club", blank=True)
    leagues = models.ManyToManyField("sports.League", blank=True)

    def __str__(self):
        return f"{self.user if self.user else ''}"


class Coach(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.OneToOneField(Account, null=True, blank=True, on_delete=models.SET_NULL)

    university = models.ForeignKey(University, null=True, blank=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user if self.user else ''} - {self.university.name if self.university else 'No University'}"

    @property
    def is_paid(self):
        is_university_plan_active = Payment.objects.filter(
            plan="university", university=self.university, active=True
        ).exists()
        if is_university_plan_active:
            return True
        is_coach_plan_active = Payment.objects.filter(plan="coach", coach=self, active=True).exists()

        return is_coach_plan_active


class SavedAccount(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("athlete", "coach")

    def __str__(self):
        return f"{self.coach.user.email} saved {self.athlete.user.email}"


class Payment(models.Model):
    plan = models.CharField(
        max_length=10,
        choices=[
            ("university", "University"),
            ("coach", "Coach"),
        ],
    )

    # TODO: Make sure we cannot set a university if the plan is coach and vice versa
    university = models.ForeignKey(University, null=True, blank=True, on_delete=models.SET_NULL)
    coach = models.ForeignKey(Coach, null=True, blank=True, on_delete=models.SET_NULL)

    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    current_period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = (
            self.university.name
            if self.university
            else self.coach.user
            if self.coach and self.coach.user
            else "No Name"
        )
        status = "Active" if self.active else "Inactive"
        return f"{self.plan} - {name} - {status}"
