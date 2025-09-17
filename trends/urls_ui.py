from django.urls import path
from . import views_ui


urlpatterns = [
    path("query/", views_ui.query_form, name="query-form-frontend"),
    path("query/submit/", views_ui.submit_query,
        name="trend-query-create-frontend"),
    path("query/<uuid:id>/results/", views_ui.query_detail,
        name="query-detail-frontend"),
    path("query/<uuid:query_id>/results/<uuid:id>/", views_ui.result_detail,
        name="trend-result-detail-frontend"),

    # Auth
    path("signup/", views_ui.signup_view, name="signup"),
    path("login/", views_ui.login_view, name="login"),
    path("logout/", views_ui.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views_ui.dashboard, name="dashboard"),
]
