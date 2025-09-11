def build_perplexity_query(industry: str, region: str, persona: str, date_range: str) -> str:
    return (
        f"Find the top 5 trending topics for {persona} in the {industry} sector "
        f"in {region} during {date_range}. "
        "For each trend return a JSON object with keys: "
        "`topic` (string), `summary` (string), "
        "`sources` (object with `urls` list and optional `snippets` list and optional `dates` list), "
        "`suggested_angles` (array of strings). "
        "Return the full result as a JSON object with a top-level key `results` which is an array of these objects. "
        "Do NOT return any other text. Example output:\n"
        "Return ONLY a JSON object with this exact structure, no extra text:"
        "{"
            '"results": ['
                '{'
                    '"topic": "string",'
                    '"summary": "string",'
                    '"sources": { "urls": ["string"], "snippets": ["string"] },'
                    '"suggested_angles": ["string"]'
                '}'
            ']'
        "}"
    )
