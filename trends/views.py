from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import TrendQuery, TrendResult, QuerySubscription
from .serializers import TrendQuerySerializer, TrendResultSerializer, TrendQueryCreateSerializer, SignupSerializer, LoginSerializer, UserSerializer, TrendQueryBriefSerializer, QuerySubscriptionSerializer
from .tasks import process_trend_query
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now
from datetime import timedelta
from celery import current_app as celery_app
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from uuid import UUID
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.db.models import Max
# Create your views here.


User = get_user_model()


class SignupAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if not all([first_name, last_name, email, password, password2]):
            return Response(
                {
                    "success": False,
                    "message": "All fields are required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {"success": False, "message": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"success": False, "message": "Email already in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "success": True,
                "message": "Signup successful",
                "data": {
                    "user_id": str(user.id),
                    "full_name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "token": token.key
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "message": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": str(user.id),
                    "full_name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "token": token.key
                },
            }
        )


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(
            {"success": True, "message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )


class DashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: "Dashboard data with queries."})
    def get(self, request):
        queries = request.user.trend_queries.all().order_by("-created_at")
        serializer = TrendQuerySerializer(queries, many=True)

        return Response(
            {
                "success": True,
                "message": "Dashboard data fetched successfully",
                "data": {
                    "full_name": f"{request.user.first_name} {request.user.last_name}",
                    "email": request.user.email,
                    "queries": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


class TrendQueryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        query = get_object_or_404(TrendQuery, id=id)

        if query.status == 'pending':
            return Response(
                {
                    'message': "Query is pending. Please check again later.",
                    'status': query.status
                },
                status=status.HTTP_202_ACCEPTED,
            )

        if query.status == 'failed':
            return Response(
                {
                    'message': 'Query failed. Please retry.',
                    'status': query.status
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = TrendQuerySerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrendQueryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TrendQueryCreateSerializer(data=request.data)

        if serializer.is_valid():
            industry = serializer.validated_data["industry"]
            region = serializer.validated_data["region"]
            persona = serializer.validated_data["persona"]
            date_range = serializer.validated_data["date_range"]

            one_day_ago = now() - timedelta(days=1)
            existing_query = (
                TrendQuery.objects.filter(
                    industry=industry,
                    region=region,
                    persona=persona,
                    date_range=date_range,
                    status="completed",
                    created_at__gte=one_day_ago,
                )
                .order_by("-created_at")
                .first()
            )

            if existing_query:
                new_query = TrendQuery.objects.create(
                    user=request.user,
                    industry=industry,
                    region=region,
                    persona=persona,
                    date_range=date_range,
                    status="completed",
                )

                for result in existing_query.results.all():
                    TrendResult.objects.create(
                        query=new_query,
                        topic=result.topic,
                        summary=result.summary,
                        sources=result.sources,
                        engagement_score=result.engagement_score,
                        freshness_score=result.freshness_score,
                        relevance_score=result.relevance_score,
                        final_score=result.final_score,
                        suggested_angles=result.suggested_angles,
                    )

                return Response(
                    {
                        "message": "Using existing recent query results.",
                        "query_id": str(existing_query.id),
                        "status": existing_query.status,
                    },
                    status=status.HTTP_200_OK,
                )

            query = serializer.save(status="pending", user=request.user)
            QuerySubscription.objects.get_or_create(
                user=request.user,
                query=query,
                defaults={
                    "wants_emails": True,
                    "is_active": True
                }
            )
            process_trend_query.delay(str(query.id))
            return Response(
                {
                    "message": "Trend query created successfully. Processing started.",
                    "query_id": str(query.id),
                    "status": query.status,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrendResultDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            UUID(str(id))
        except ValueError:
            return Response(
                {"error": "Invalid ID format. Must be a valid UUID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            trend = TrendResult.objects.get(id=id)
        except TrendResult.DoesNotExist:
            return Response(
                {"error": "TrendResult not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TrendResultSerializer(trend)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuerySubscriptionToggleAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, query_id):
        try:
            query = TrendQuery.objects.get(id=query_id)
        except TrendQuery.DoesNotExist:
            return Response(
                {
                    "error": "Query not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        sub, created = QuerySubscription.objects.get_or_create(
            user=request.user,
            query=query,
            defaults={"wants_emails": True}
        )

        wants = request.data.get("wants_emails", None)
        if wants is None:
            sub.wants_emails = not sub.wants_emails
        else:
            sub.wants_emails = bool(wants)

        sub.save()
        return Response(
            {
                "query_id": str(query_id),
                "wants_emails": sub.wants_emails
            }
        )


class ToggleSubscriptionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, query_id):
        action = request.data.get("action")
        query = get_object_or_404(TrendQuery, id=query_id)
        sub, _ = QuerySubscription.objects.get_or_create(
            user=request.user, 
            query=query, 
            defaults={"wants_emails": True, "is_active": True},
        )

        if action == "subscribe":
            sub.wants_emails = True
        elif action == "unsubscribe":
            sub.wants_emails = False
        elif action == "activate":
            sub.is_active = True
        elif action == "deactivate":
            sub.is_active = False
        else:
            return Response({"error": "Invalid action"}, status=400)

        sub.save()
        return Response(
            {
                "query_id": str(query_id), 
                "wants_emails": sub.wants_emails, 
                "is_active": sub.is_active
            }
        )


class MeAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        user_data = UserSerializer(user).data
        user_queries_qs = user.trend_queries.all().order_by("-created_at")[:10]
        queries_data = TrendQueryBriefSerializer(
            user_queries_qs, many=True).data

        subs_qs = QuerySubscription.objects.filter(user=user)
        subs_count = subs_qs.filter(wants_emails=True).count()
        subs_data = QuerySubscriptionSerializer(subs_qs, many=True).data

        payload = {
            "user": user_data,
            "stats": {
                "total_queries": user.trend_queries.count(),
                "acive_subscriptions": subs_count,
            },
            "recent_queries": queries_data,
            "subscriptions": subs_data,
        }
        return Response(payload, status=status.HTTP_200_OK)
