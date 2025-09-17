from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    wants_emails = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrendQuery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="trend_queries",
        null=True, 
        blank=True
    )
    industry = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    persona = models.CharField(max_length=100)
    date_range = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.industry} | {self.region} | {self.persona} | {self.date_range} | {self.id} | {self.status}"


class TrendResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.ForeignKey(TrendQuery, related_name='results', on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    topic = models.CharField(max_length=255)
    summary = models.TextField()
    sources = models.JSONField(default=dict)
    engagement_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)
    suggested_angles = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_final_score(self, weights=(0.3, 0.4, 0.3)):
        engagement, freshness, relevance = weights

        self.final_score = round(
            (self.engagement_score * engagement) +
            (self.freshness_score * freshness) +
            (self.relevance_score * relevance), 2)
        return self.final_score

    def __str__(self):
        return f"{self.topic} (Score: {self.final_score} | Query ID: {self.query.id})"
