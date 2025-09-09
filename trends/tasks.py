from .services import fetch_trends_from_perplexity
from celery import shared_task
from .models import TrendQuery
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_trend_query(self, query_id):
    try:
        query = TrendQuery.objects.get(id=query_id)
        query.status = 'running'
        query.save()

        fetch_trends_from_perplexity(query)

        logger.info(f"Trends fetched for query {query.id}")
        return f"Trends fetched for query {query.id}"

    except TrendQuery.DoesNotExist:
        logger.error(f"TrendQuery {query.id} not found")
        return self.retry(countdown=10, max_retries=3)

    except Exception as e:
        query = TrendQuery.objects.filter(id=query_id).first()
        if query:
            query.status = 'failed'
            query.save()
        logger.error(f"Error processing query {query_id}: {e}")
        raise e
