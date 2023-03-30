from django.db import models
from django.contrib.auth.models import AbstractUser
from newspaper_agency import settings
from django.urls import reverse


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Newspaper(models.Model):
    title = models.CharField(max_length=255)
    context = models.TextField()
    published_date = models.DateField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    redactors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="newspapers")

    def __str__(self):
        return self.title


class Redactor(AbstractUser):
    years_of_experience = models.IntegerField()

    class Meta:
        verbose_name = "redactor"
        verbose_name_plural = "redactors"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

    def get_absolute_url(self):
        return reverse("agency:redactor-detail", kwargs={"pk": self.pk})
