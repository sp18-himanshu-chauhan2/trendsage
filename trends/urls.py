from django.urls import path
from .views import TrendQueryDetailView, TrendQueryCreateView, TrendResultDetailView, SignupAPI, LoginAPI, DashboardAPI, LogoutAPI, QuerySubscriptionToggleAPI, MeAPIView, ToggleSubscriptionAPI, SignupStartAPI, SignupVerifyAPI
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('trends/query/<uuid:id>/', TrendQueryDetailView.as_view(),
        name='trend-query-detail'),
    path('trends/query/', TrendQueryCreateView.as_view(),
        name='trend-query-create'),
    path("trends/<uuid:id>/", TrendResultDetailView.as_view(),
        name="trend-result-detail"),
    
    # Auth
    path("auth/signup/start/", SignupStartAPI.as_view(), name="api-signup-start"),
    path("auth/signup/verify/", SignupVerifyAPI.as_view(), name="api-signup-verify"),
    path("auth/login/", LoginAPI.as_view(), name="api-login"),
    path("auth/logout/", LogoutAPI.as_view(), name="api-logout"),

    # Dashboard
    path("dashboard/", DashboardAPI.as_view(), name="api-dashboard"),

    # Subscription
    path("trends/query/<uuid:query_id>/subscription/", QuerySubscriptionToggleAPI.as_view(), name="api-query-subscription"),
    path("trends/query/<uuid:query_id>/subscription/toggle/", ToggleSubscriptionAPI.as_view(), name="toggle-subscription-api"),

    # Profile
    path("auth/token/", obtain_auth_token, name="api_token_auth"),
    path("profile/me/", MeAPIView.as_view(), name="api-me"),
]
