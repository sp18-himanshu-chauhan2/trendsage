from rest_framework import serializers
from .models import TrendQuery, TrendResult, QuerySubscription
from django.contrib.auth import get_user_model
from django.db.models import Max

User = get_user_model()


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
            'version',
        ]
        read_only_fields = ("id", "created_at", "updated_at")


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


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "date_joined",
            "last_login",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TrendQueryBriefSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    latest_results_count = serializers.SerializerMethodField()

    class Meta:
        model = TrendQuery
        fields = [
            "id",
            "industry",
            "region",
            "persona",
            "date_range",
            "status",
            "created_at",
            "updated_at",
            "latest_version",
            "latest_results_count",
        ]

    def get_latest_version(self, obj):
        return obj.results.aggregate(Max("version"))["version__max"] or None

    def get_latest_results_count(self, obj):
        v = self.get_latest_version(obj)
        if not v:
            return 0
        return obj.results.filter(version=v).count()


class QuerySubscriptionSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source="user.id")
    query_id = serializers.ReadOnlyField(source="query.id")

    class Meta:
        model = QuerySubscription
        fields = [
            "id",
            "user_id",
            "query_id",
            "wants_emails",
            "is_active",
            "created_at",
        ]
