from celery import shared_task
import logging
from .models import TrendQuery
from .services import fetch_trends_mock


logger = logging.getLogger(__name__)


@shared_task
def test_celery():  # Simple test task to verify Celery is working
    logger.info("Celery task executed successfully.")
    return "Hello from Celery!"


@shared_task
def fetch_trends_mock_task():  # Task to fetch mock trends for testing
    q = TrendQuery.objects.create(
        industry='EdTech',
        region='India',
        persona='founders',
        date_range='last_week',
    )
    fetch_trends_mock(q)
    logger.info(f"Mock trends fetched for query ID {q.id}")
    return f"Mock trends fetched for query ID {q.id}"


@shared_task
def process_trend_query(query_id):
    try:
        query = TrendQuery.objects.get(id=query_id)
        fetch_trends_mock(query)  # replace with real service later
        query.status = 'completed'
        query.save()
        logger.info(f"Trends fetched for query {query.id}")
        return f"Trends fetched for query {query.id}"
    except TrendQuery.DoesNotExist:
        logger.error(f"TrendQuery {query.id} not found")
        return f"TrendQuery {query.id} not found"
