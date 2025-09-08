import requests
import logging
from decouple import config
from .models import TrendQuery, TrendResult
from .query_builder import build_perplexity_query


logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = config("PERPLEXITY_API_KEY", default='')

API_URL = "https://api.perplexity.ai/chat/completions"


def fetch_trends_from_perplexity(query_obj: TrendQuery):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    query_text = build_perplexity_query(
        query_obj.industry, 
        query_obj.region, 
        query_obj.persona, 
        query_obj.date_range,
    )

    payload = {
        "q": query_text,
        "search_type": "web",
        "num_results": 5,
        "response_format": "detailed",
        "include_sources": True,
        "include_summaries": True,
        "include_suggested_angles": True,
    }

    try:
        response = requests.post(
            API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            logger.error(
                f"Perplexity API Error: {response.status_code}: {response.text}")
            query_obj.status = 'failed'
            query_obj.save()
            return None

        data = response.json()

        results = data.get("results", [])

        for r in results:
            TrendResult.objects.create(
                query=query_obj,
                topic=r.get("topic", "Unknown"),
                summary=r.get("summary", ""),
                sources={
                    "urls": r.get("urls", []),
                    "citations": r.get("citations", []),
                    "snippets": r.get("snippets", []),
                },
                engagement_score=0.0,
                freshness_score=0.0,
                relevance_score=0.0,
                final_score=0.0,
                suggested_angles=r.get("angles", []),
            )

        query_obj.status = 'completed'
        query_obj.save()
        return results

    except Exception as e:
        logger.exception("Error calling Perplexity API")
        query_obj.status = 'failed'
        query_obj.save()
        return None


def fetch_trends_mock(query_obj: TrendQuery):
    dummy_results = [
        {
            "topic": "AI in Education",
            "summary": "AI-driven tools are transforming EdTech...",
            "urls": ["https://example.com/ai-education"],
            "snippets": ["AI is reshaping classrooms..."],
            "angles": ["Write about AI tutors", "Impact on teachers"],
        },
        {
            "topic": "Remote Learning Platforms",
            "summary": "Increased adoption of remote platforms post-pandemic...",
            "urls": ["https://example.com/remote-learning"],
            "snippets": ["Zoom, Teams adoption rising..."],
            "angles": ["Market analysis", "Startup opportunities"],
        },
    ]

    for r in dummy_results:
        TrendResult.objects.create(
            query=query_obj,
            topic=r["topic"],
            summary=r["summary"],
            sources={"urls": r["urls"], "snippets": r["snippets"]},
            final_score=0.0,
            suggested_angles=r["angles"],
        )

    query_obj.status = "completed"
    query_obj.save()
    return dummy_results
