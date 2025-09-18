from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"


def build_detail_url(query_id, version=None):
    url = urljoin(BASE_URL, f"/trendsage/web/query/{query_id}/results/")
    if version:
        url = f"{url}?version={version}"
    return url


def build_unsubscribe_url(user, query):
    return urljoin(BASE_URL, f"/trendsage/web/query/{query.id}/subscription/unsubscribe/{user.id}/")


def send_trend_email(user, query, version, results=None, subject=None, message=None, include_results=True):
    subject = subject or f"Trends Update for {query.industry} -- vesrion {version}"
    detail_url = build_detail_url(query.id, version)
    unsubscribe_url = build_unsubscribe_url(user, query)
    updated_at = timezone.localtime(query.updated_at)

    results_list = list(results) if results is not None else []

    context = {
        "user": user,
        "subject": subject,
        "query": query,
        "version": version,
        "results": results_list,
        "message": message or "",
        "detail_url": detail_url,
        "updated_at": updated_at,
        "unsubscribe_url": unsubscribe_url,
    }

    text_body = render_to_string("emails/trend_notification.txt", context)
    html_body = render_to_string("emails/trend_notification.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
