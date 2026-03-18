from config import S2_API_KEY
from typing import Any
from screen import get_with_backoff_jitter
from utils import normalize_record


def fetch_semantic_scholar(query: str, limit: int) -> list[dict[str, Any]]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,authors,externalIds,venue,url,citationCount"
    }
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    data = get_with_backoff_jitter(url, params=params)
    items = data.get("data", [])
    results = []

    for item in items:
        authors = ", ".join(a.get("name", "") for a in item.get("authors", [])) or None
        ext = item.get("externalIds", {}) or {}
        doi = ext.get("DOI")

        results.append(normalize_record(
            source="semantic_scholar",
            title=item.get("title"),
            authors=authors,
            year=item.get("year"),
            doi=doi,
            journal=item.get("venue"),
            url=item.get("url"),
            extra={},
            citation_count=item.get("citationCount")
        ))
    return results