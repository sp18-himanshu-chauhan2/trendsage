def build_perplexity_query(industry: str, region: str, persona: str, date_range: str) -> str:
    return f"""
You are an AI research assistant. 
Given the following query parameters, find and summarize the most relevant and recent trends.

Query Parameters:
- Industry: {industry}
- Region: {region}
- Persona / Target Audience: {persona}
- Date Range: {date_range}

Instructions:
1. Identify 5 key emerging trends in this industry and region for the given persona within the specified date range. 
2. For each trend, return a JSON object with the following fields:
    - "topic": A short, descriptive title of the trend.
    - "summary": A concise summary (3–5 sentences) explaining the trend.
    - "sources": An object with parallel lists:
        {{
            "urls": ["https://...", "https://..."],
            "snippets": ["Excerpt from source 1", "Excerpt from source 2"],
            "dates": ["YYYY-MM-DD", "YYYY-MM-DD"]
        }}
    - "suggested_angles": List of 2–3 potential directions or insights for exploring this trend further.

3. Return ONLY a valid JSON object in the following format:
{{
    "results": [
        {{
        "topic": "...",
        "summary": "...",
        "sources": {{
            "urls": ["...", "..."],
            "snippets": ["...", "..."],
            "dates": ["YYYY-MM-DD", "YYYY-MM-DD", ...]
        }},
        "suggested_angles": ["...", "..."]
        }},
        ...
    ]
}}

Important:
- Do not include any extra commentary outside of the JSON.
- Ensure the number of items in "urls", "snippets", and "dates" always match.
- Dates must be valid ISO 8601 format (YYYY-MM-DD).
"""
