from django.urls import path
from .views import TrendQueryDetailView, TrendQueryCreateView, TrendResultDetailView


urlpatterns = [
    # path('trends/', TrendListView.as_view(), name='trend-list'),
    path('trends/query/<uuid:id>/', TrendQueryDetailView.as_view(),
        name='trend-query-detail'),
    path('trends/query/', TrendQueryCreateView.as_view(),
        name='trend-query-create'),
    path("trends/<uuid:id>/", TrendResultDetailView.as_view(),
        name="trend-result-detail"),
]
