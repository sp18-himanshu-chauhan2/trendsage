def build_perplexity_query(industry: str, region: str, persona: str, date_range: str) -> str:
    """
    Build an impactful query string for Perplexity API.
    """

    return (
        f"What are the trending topics among {persona} in the {industry} sector "
        f"within {region} during {date_range}? "
        f"Please provide a concise summary, key sources, and suggested content angles."
    )