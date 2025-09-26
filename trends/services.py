import requests
import logging
from decouple import config
from .models import TrendQuery, TrendResult
from .query_builder import build_perplexity_query
from django.utils import timezone
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
import json
import time
import re
import math

logger = logging.getLogger(__name__)
PERPLEXITY_API_KEY = config("PERPLEXITY_API_KEY", default='')
API_URL = "https://api.perplexity.ai/chat/completions"
model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_engagement_from_sources(sources):
    urls = sources.get("urls", [])
    data = sources.get("engagement", [])

    score = 0
    for e in data:
        likes = e.get("likes", 0)
        shares = e.get("shares", 0)
        comments = e.get("comments", 0)
        score += (likes * 0.5) + (shares * 1.0) + (comments * 0.8)

    if score == 0:
        score = min(100, len(urls) * 20)

    return float(min(score, 100.0))


def compute_freshness_from_sources(sources, query_created_at, decay_factor=7):
    dates = sources.get("dates", []) if isinstance(sources, dict) else []

    parsed_dates = []
    for d in dates:
        try:
            dt = datetime.fromisoformat(d)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            parsed_dates.append(dt)
        except Exception:
            continue

    if parsed_dates:
        newest = max(parsed_dates)  # most recent source
    else:
        newest = query_created_at  # fallback to query timestamp

    age_days = (timezone.now() - newest).days
    score = 100 * math.exp(-age_days / decay_factor)

    return float(round(score, 2))


def compute_relevance(query_obj, topic, summary):
    query_text = f"{query_obj.industry} {query_obj.persona} {query_obj.region} {query_obj.date_range}"
    trend_text = f"{topic} {summary}"

    embeddings = model.encode([query_text, trend_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    relevance = max(0.0, round(similarity * 100, 2))
    return relevance


def clean_json_numbers(text: str) -> str:
    return re.sub(r'(\d+)_(\d+)', r'\1\2', text)


def sanitize_json(text: str) -> str:
    text = re.sub(r',(\s*[\]}])', r'\1', text)
    text = re.sub(r'\"\"(\s*[,\]])', r'"\1', text)
    text = text.replace("“", "\"").replace("”", "\"")
    return text


def extract_json_from_text(text):
    cleaned = clean_json_numbers(text)
    cleaned = sanitize_json(cleaned)

    try:
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"Direct JSON parse failed: {e}")

    m = re.search(r'(\{.*"results"\s*:\s*\[.*\]\s*\})', cleaned, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception as e:
            logger.error(f"JSON parse error from regex 1: {e}")

    m2 = re.search(r'(\[.*\])', cleaned, re.S)
    if m2:
        try:
            return {"results": json.loads(m2.group(1))}
        except Exception as e:
            logger.error(f"JSON parse error from regex 2: {e}")

    logger.error(
        f"❌ Could not parse content into JSON. First 500 chars: {cleaned[:500]}")
    return None


def fetch_trends_from_perplexity(query_obj: TrendQuery, max_retries=3, timeout=120):
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
        "temperature": 1.5,
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

        from django.db.models import Max
        latest_version = query_obj.results.aggregate(Max("version"))[
            "version__max"] or 0
        new_version = latest_version + 1

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

            logger.info(
                f"Preparing trend result for query {query_obj.id}, version {new_version}: {r.get('topic')}")

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
                version=new_version,
            )
            trend.calculate_final_score()
            trend.save()

        logger.info(
            f"✅ Saved {query_obj.results.filter(version=new_version).count()} results for query {query_obj.id} (v{new_version})")

        query_obj.status = "completed"
        query_obj.save()
        return parsed["results"]

    except Exception as e:
        logger.exception("Error calling Perplexity API")
        query_obj.status = "failed"
        query_obj.save()
        raise
