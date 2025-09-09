from rest_framework import serializers
from .models import TrendQuery, TrendResult


class TrendResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendResult
        fields = [
            'id',
            'topic',
            'summary',
            'sources',
            'engagement_score',
            'freshness_score',
            'relevance_score',
            'final_score',
            'suggested_angles',
            'created_at',
        ]


class TrendQuerySerializer(serializers.ModelSerializer):
    results = TrendResultSerializer(many=True, read_only=True)

    class Meta:
        model = TrendQuery
        fields = [
            'id',
            'industry',
            'region',
            'persona',
            'date_range',
            'status',
            'created_at',
            'results',
        ]


class TrendQueryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendQuery
        fields = [
            'id',
            'industry',
            'region',
            'persona',
            'date_range',
        ]
