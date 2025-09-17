from .services import fetch_trends_from_perplexity
from celery import shared_task
from .models import TrendQuery, TrendResult
import logging
from django.utils.timezone import now
from .email_utils import send_trend_email
from django.db.models import Max

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_trend_query(self, query_id):
    try:
        query = TrendQuery.objects.get(id=query_id)

        if query.status != "pending":
            logger.info(f"Query {query.id} is not pending. Skipping.")
            return f"Query {query.id} already processed or failed."

        query.status = 'running'
        query.save()

        fetch_trends_from_perplexity(query)

        query.status = "completed"
        query.updated_at = now()
        query.save()

        logger.info(
            f"Trends fetched for query {query.id}")
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


@shared_task
def refresh_trend_queries():
    logger.info("Running refresh_trend_queries task...")
    queries = TrendQuery.objects.filter(status="completed")

    for query in queries:
        try:
            logger.info(f"Refreshing query {query.id} ({query.industry})")
            fetch_trends_from_perplexity(query)

            latest_version = query.results.aggregate(Max("version"))["version__max"]

            if not latest_version:
                logger.warning(f"No results for query {query.id} after refresh")
                continue

            results = TrendResult.objects.filter(query=query, version=latest_version).order_by("-final_score")

            if hasattr(query, "user"):  # M2M
                recipients = list(query.user.all())
            else:
                recipients = []

            for user in recipients:
                if not getattr(user, "wants_emails", True):
                    logger.info(f"Skipping email to {user.email} (wants_emails=False)")
                    continue
                
                send_trend_email(
                    user=user,
                    query=query,
                    version=latest_version,
                    results=results,
                    subject=f"Your trends have been refreshed (v{latest_version})",
                )
                logger.info(
                    f"Email sent to {user.email} for query {query.id} (v{latest_version})"
                )
        except Exception as e:
            print(f"Failed to refresh query {query.id}: {e}")
