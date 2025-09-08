from celery import shared_task
import logging
from .models import TrendQuery
from .services import fetch_trends_mock


logger = logging.getLogger(__name__)

@shared_task
def test_celery():
    logger.info("Celery task executed successfully.")
    return "Hello from Celery!"


@shared_task
def fetch_trends_mock_task():
    q = TrendQuery.objects.create(
        industry='EdTech',
        region='India',
        persona='founders',
        date_range='last_week',
    )
    fetch_trends_mock(q)
    logger.info(f"Mock trends fetched for query ID {q.id}")
    return f"Mock trends fetched for query ID {q.id}"