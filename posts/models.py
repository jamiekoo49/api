from django.db import models


class Post(models.Model):
    posted_by = models.ForeignKey("accounts.Athlete", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_date = models.DateField(auto_now_add=True)

    video = models.FileField()

    def __str__(self):
        return f"{self.title} by {self.posted_by}"
