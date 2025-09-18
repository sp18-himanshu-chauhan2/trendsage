from django.urls import path
from .views import TrendQueryDetailView, TrendQueryCreateView, TrendResultDetailView, SignupAPI, LoginAPI, DashboardAPI, LogoutAPI, QuerySubscriptionToggleAPI


urlpatterns = [
    # path('trends/', TrendListView.as_view(), name='trend-list'),
    path('trends/query/<uuid:id>/', TrendQueryDetailView.as_view(),
        name='trend-query-detail'),
    path('trends/query/', TrendQueryCreateView.as_view(),
        name='trend-query-create'),
    path("trends/<uuid:id>/", TrendResultDetailView.as_view(),
        name="trend-result-detail"),
    
    # Auth
    path("auth/signup/", SignupAPI.as_view(), name="api-signup"),
    path("auth/login/", LoginAPI.as_view(), name="api-login"),
    path("auth/logout/", LogoutAPI.as_view(), name="api-logout"),

    # Dashboard
    path("dashboard/", DashboardAPI.as_view(), name="api-dashboard"),

    # Subscription
    path("trends/query/<uuid:query_id>/subscription/", QuerySubscriptionToggleAPI.as_view(), name="api-query-subscription"),

]
