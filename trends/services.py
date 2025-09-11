import requests
import logging
from decouple import config
from .models import TrendQuery, TrendResult
from .query_builder import build_perplexity_query
from django.utils import timezone
import json
import time
import re

logger = logging.getLogger(__name__)
PERPLEXITY_API_KEY = config("PERPLEXITY_API_KEY", default='')
API_URL = "https://api.perplexity.ai/chat/completions"


def compute_engagement_from_sources(sources):
    urls = sources.get("urls", []) if isinstance(sources, dict) else []
    base = min(100, len(urls) * 20)
    return float(base)


def compute_freshness_from_sources(sources, query_created_at):
    dates = sources.get("dates", []) if isinstance(sources, dict) else []

    if dates:
        try:
            parsed = [timezone.datetime.fromisoformat(d) for d in dates]
            newest = max(parsed)
            age_days = (timezone.now() - newest).days
            score = max(0.0, 100.0 - age_days * 5)
            return float(score)
        except Exception:
            pass

    age_days = (timezone.now() - query_created_at).days
    return float(max(0.0, 100.0 - age_days * 3))


def compute_relevance(query_obj, topic, summary):
    q_tokens = set(re.findall(
        r"\w+", f"{query_obj.industry} {query_obj.persona} {query_obj.region} {query_obj.date_range}".lower()))

    text_tokens = set(re.findall(r"\w+", f"{topic} {summary}".lower()))

    if not q_tokens or not text_tokens:
        return 0.0

    inter = q_tokens.intersection(text_tokens)
    union = q_tokens.union(text_tokens)
    score = (len(inter) / len(union)) * 100.0
    return float(round(score, 2))


def extract_json_from_text(text):
    m = re.search(r'(\{.*"results"\s*:\s*\[.*\]\s*\})', text, re.S)

    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass

    m2 = re.search(r'(\[.*\])', text, re.S)

    if m2:
        try:
            return json.loads(m2.group)
        except Exception:
            pass

    return None


def fetch_trends_from_perplexity(query_obj: TrendQuery, max_retries=3, timeout=30):
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
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": query_text
            }
        ],
        "temperature": 0.2,
    }

    resp = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            break
        except requests.exceptions.ReadTimeout:
            logger.warning(f"Timeout on attempt {attempt+1} / {max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise

    try:
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ).strip()

        print("Raw content:", content)

        # Try direct JSON
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = extract_json_from_text(content)

        if not parsed or "results" not in parsed:
            logger.warning("No valid results in API response")
            query_obj.status = "completed"
            query_obj.save()
            return []

        for r in parsed["results"]:
            sources = r.get("sources", {})
            engagement_score = r.get("engagement")
            freshness_score = r.get("freshness")
            relevance_score = r.get("relevance")

            if engagement_score is None:
                engagement_score = compute_engagement_from_sources(sources)

            if freshness_score is None:
                freshness_score = compute_freshness_from_sources(
                    sources, query_obj.created_at)

            if relevance_score is None:
                relevance_score = compute_relevance(
                    query_obj, r.get("topic", ""), r.get("summary", ""))

            trend = TrendResult.objects.create(
                query=query_obj,
                topic=r.get("topic", "Untitled"),
                summary=r.get("summary", ""),
                sources=sources,
                engagement_score=float(engagement_score),
                freshness_score=float(freshness_score),
                relevance_score=float(relevance_score),
                suggested_angles=r.get(
                    "suggested_angles") or r.get("angles") or [],
            )
            trend.calculate_final_score()
            trend.save()

        query_obj.status = "completed"
        query_obj.save()
        return parsed["results"]

    except Exception as e:
        logger.exception("Error calling Perplexity API")
        query_obj.status = "failed"
        query_obj.save()
        raise
