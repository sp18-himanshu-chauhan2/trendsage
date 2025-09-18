from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import TrendQuery, TrendResult, QuerySubscription
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import TrendQuery
from django.utils.timezone import now
from datetime import timedelta
from django.urls import reverse
from .tasks import process_trend_query
from django.db.models import Max
from django.views.decorators.http import require_http_methods

API_BASE = "http://127.0.0.1:8000/trendsage/api"
User = get_user_model()


# --- Signup ---
def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "trends/signup.html", {
                "error": "Passwords do not match"
            })

        from .models import User
        if User.objects.filter(email=email).exists():
            return render(request, "trends/signup.html", {
                "error": "Email already registered"
            })

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        login(request, user)
        return redirect("dashboard")

    return render(request, "trends/signup.html")


# --- Login ---
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "trends/login.html", {
                "error": "Invalid email or password"
            })

    return render(request, "trends/login.html")


# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect("login")


# --- Dashboard ---
@login_required
def dashboard(request):
    user = request.user
    queries = user.trend_queries.all().order_by("-created_at")
    return render(request, "trends/dashboard.html", {"queries": queries})


@login_required
def query_form(request):
    return render(request, "trends/query_form.html")


@login_required
def submit_query(request):
    if request.method == "POST":
        industry = request.POST.get("industry")
        region = request.POST.get("region")
        persona = request.POST.get("persona")
        date_range = request.POST.get("date_range")

        # Check if same query exists within last 1 day
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
            # Reuse existing query → redirect to its detail page
            existing_query.user.add(request.user)
            return redirect(reverse("query-detail-frontend", args=[existing_query.id]))

        # If no recent query found → create new one
        query = TrendQuery.objects.create(
            industry=industry,
            region=region,
            persona=persona,
            date_range=date_range,
            status="pending",
        )

        query.user.add(request.user)

        QuerySubscription.objects.get_or_create(
            user=request.user,
            query=query,
            defaults={"wants_emails": True}
        )

        process_trend_query.delay(str(query.id))

        # Redirect to detail page
        return redirect(reverse("query-detail-frontend", args=[query.id]))

    return render(request, "trends/query_form.html")


@login_required
def query_detail(request, id):
    query = get_object_or_404(TrendQuery, id=id)

    version_param = request.GET.get("version")

    if version_param:
        try:
            version = int(version_param)
        except ValueError:
            version = query.results.aggregate(Max("version"))[
                "version__max"] or 1
    else:
        version = query.results.aggregate(Max("version"))["version__max"] or 1

    if request.user not in query.user.all():
        return render(request, "trends/query_detail.html", {
            "error": "You do not have permission to view this query."
        })

    versions = (
        query.results.values_list("version", flat=True)
        .distinct()
        .order_by("-version")
    )

    sub = QuerySubscription.objects.filter(
        user=request.user, query=query).first()
    subscribed = sub.wants_emails if sub else False

    results = query.results.filter(version=version).order_by("-final_score")
    return render(
        request,
        "trends/query_detail.html",
        {
            "query": query,
            "results": results,
            "version": version,
            "versions": versions,
            "subscribed": subscribed,
        },
    )


@login_required
def result_detail(request, query_id, id):
    query = get_object_or_404(TrendQuery, id=query_id)

    if request.user not in query.user.all():
        return render(request, "trends/result_detail.html", {
            "error": "You do not have permission to view this result."
        })

    result = get_object_or_404(TrendResult, id=id, query__id=query_id)
    return render(request, "trends/result_detail.html", {
        "result": result,
        "query_id": query_id
    })


@login_required
def toggle_subscriptions(request, id):
    query = get_object_or_404(TrendQuery, id=id)

    if request.method != "POST":
        return redirect(reverse("query-detail-frontend", args=[id]))

    sub, created = QuerySubscription.objects.get_or_create(
        user=request.user,
        query=query,
        defaults={"wants_emails": True}
    )

    action = request.POST.get("action")
    if action == "subscribe":
        sub.wants_emails = True
    elif action == "unsubscribe":
        sub.wants_emails = False
    else:
        sub.wants_emails = not sub.wants_emails

    sub.save()
    return redirect(reverse("query-detail-frontend", args=[id]))


@login_required
@require_http_methods(["GET", "POST"])
def unsubscribe_query_confirm(request, query_id, user_id):
    user = request.user
    if not request.user.is_authenticated or str(request.user.id) != str(user_id):
        return redirect("login")

    query = get_object_or_404(TrendQuery, id=query_id)
    if request.method == "POST":
        sub = QuerySubscription.objects.filter(
            user=request.user, query=query).first()
        if sub:
            sub.wants_emails = False
            sub.save()
        return render(request, "trends/unsubscribed.html", {"user": request.user})
    return render(request, "trends/unsubscribe_confirm.html", {"user": request.user, "query": query})
