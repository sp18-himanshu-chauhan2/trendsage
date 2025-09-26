def build_perplexity_query(industry: str, region: str, persona: str, date_range: str) -> str:
    return f'''
You are a search engine.
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
    - "summary": A concise summary (3-5 sentences) explaining the trend.
    - "sources": An object with parallel lists:
        {{
            "urls": ["https://...", "..."],
            "snippets": ["Excerpt from source 1", "..."],
            "dates": ["YYYY-MM-DD", "..."],
            "engagement": [{{"likes":123,"shares":45,"comments":10}}, ...]
        }}
    - "suggested_angles": List of 2-3 potential directions or insights for exploring this trend further.

3. Source and URL Rules:
    - Provide completely different sets of URLs for each of the 5 trends — no URL should be repeated across trends.
    - Each trend should include between 1 to 5 URLs.
    - Include a minimum of one URL from social media platforms and it must be valid and accessible: LinkedIn, Twitter/X, YouTube, or Instagram.
    - Include at least one credible news, research paper, or authoritative blog URL per trend.
    - Do NOT fabricate or generate fake URLs. Only provide genuine, publicly accessible URLs.
    - URLs should be recent and fall within the specified date range.
    - Engagement metrics should reflect realistic approximate counts from social platforms where available; for news/blog URLs, set likes/shares/comments to 0.

4. Engagement and Date Rules:
    - Social media URLs must include engagement data (likes, shares, comments) if available.
    - Dates must be valid ISO 8601 format (YYYY-MM-DD) matching the actual publish or post date of the source.
    - Ensure the number of URLs, snippets, dates, and engagement entries match per trend.

5. Return ONLY a valid JSON object in the following format:
{{
    "results": [
        {{
        "topic": "...",
        "summary": "...",
        "sources": {{
            "urls": ["...", "...", "..."],
            "snippets": ["...", "...", "..."],
            "dates": ["YYYY-MM-DD", "YYYY-MM-DD", "YYYY-MM-DD"],
            "engagement": [
                {{"likes":..., "shares":..., "comments":...}}, 
                {{"likes":..., "shares":..., "comments":...}}, 
                {{"likes":..., "shares":..., "comments":...}}
            ]
        }},
        "suggested_angles": ["...", "..."]
        }},
        ...
    ]
}}

Important:
- Do not include any explanations or commentary outside the JSON.
- Verify URL authenticity and accessibility; exclude any broken, spammy, or fraudulent links.
- No duplicate URLs should appear across any of the 5 trends.
- The number of URLs per trend can vary from 1 to 5 according to availability.
'''
