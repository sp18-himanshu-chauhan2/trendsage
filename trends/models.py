from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import uuid
import random
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


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
    query = models.ForeignKey(
        TrendQuery, related_name='results', on_delete=models.CASCADE)
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


class QuerySubscription(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="query_subscriptions",
    )
    query = models.ForeignKey(
        TrendQuery,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    wants_emails = models.BooleanField(default=True)  # email
    is_active = models.BooleanField(default=True)  # refresh updates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "query")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.query.industry}/{self.query.region} (emails={self.wants_emails} active={self.is_active})"


def generate_numeric_otp(n=6):
    return "".join(random.choices("0123456789", k=n))


class SignUpOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=32, default="signup")

    class Meta:
        indexes = [
            models.Index(fields=["email", "created_at"]),
        ]

    def set_otp(self, otp_plain: str):
        self.otp_hash = make_password(otp_plain)

    def check_otp(self, otp_plain: str) -> bool:
        return check_password(otp_plain, self.otp_hash)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"OTP for {self.email} (used={self.is_used})"
