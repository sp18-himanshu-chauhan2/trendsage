from rest_framework import serializers
from .models import TrendQuery, TrendResult


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


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
    results = serializers.SerializerMethodField()

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

    def get_results(self, obj):
        results = obj.results.order_by("-final_score")
        return TrendResultSerializer(results, many=True).data


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
