from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import TrendQuery, TrendResult

API_BASE = "http://127.0.0.1:8000/trendsage/api"


def query_form(request):
    return render(request, "trends/query_form.html")


def submit_query(request):
    if request.method == "POST":
        industry = request.POST.get("industry")
        region = request.POST.get("region")
        persona = request.POST.get("persona")
        date_range = request.POST.get("date_range")

        payload = {
            "industry": industry,
            "region": region,
            "persona": persona,
            "date_range": date_range,
        }

        try:
            response = requests.post(f"{API_BASE}/trends/query/", json=payload)
            if response.status_code in [200, 201]:
                data = response.json()
                query_id = data.get("query_id")
                return redirect(f"/trendsage/web/query/{query_id}/results")
            else:
                return render(request, "trends/query_form.html", {
                    "error": response.json().get("error", "Something went wrong"),
                })
        except requests.RequestException as e:
            return render(request, "trends/query_form.html", {
                "error": str(e),
            })

    return render(request, "trends/query_form.html")


def query_detail(request, id):
    query = get_object_or_404(TrendQuery, id=id)
    results = TrendResult.objects.filter(query=query).order_by("-final_score")
    return render(request, "trends/query_detail.html", {
        "query": query,
        "results": results
    })


def result_detail(request, query_id, id):
    response = requests.get(f"{API_BASE}/trends/{id}/")
    if response.status_code == 200:
        data = response.json()
        return render(request, "trends/result_detail.html", {"result": data, "query_id": query_id})
    return render(request, "trends/result_detail.html", {"error": "Result not found", "query_id": query_id})
