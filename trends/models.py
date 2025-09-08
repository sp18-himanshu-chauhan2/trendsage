from django.db import models
import uuid


class TrendQuery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    industry = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    persona = models.CharField(max_length=100)
    date_range = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.industry} | {self.region} | {self.persona} | {self.date_range}"


class TrendResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.ForeignKey(
        TrendQuery, related_name='results', on_delete=models.CASCADE)
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

    def __str__(self):
        return f"{self.topic} (Score: {self.final_score})"
